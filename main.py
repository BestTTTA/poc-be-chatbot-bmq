from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, time
from enum import Enum
import ollama
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import os
import PyPDF2
import io
from contextlib import contextmanager
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Document Management System with Queue Booking", version="3.0.0")

origins = [
    "http://localhost:3000",       
    "http://127.0.0.1:3000",
    "https://your-frontend-site.com",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_url = os.getenv("DATABASE_URL")
embedder = SentenceTransformer("BAAI/bge-m3")

class QueueStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TextInput(BaseModel):
    text: str
    service_id: int

class QueryRequest(BaseModel):
    question: str

class DocumentResponse(BaseModel):
    id: int
    message: str
    province_id: int
    district_id: int
    service_id: int
    province_name: str
    district_name: str
    service_name: str

class ServiceRelation(BaseModel):
    province_id: int
    province_name: str
    district_id: int
    district_name: str
    service_id: int
    service_name: str

class QueryResponse(BaseModel):
    answer: str
    relevant_documents: List[dict]

class QueueBookingCreate(BaseModel):
    citizen_name: str
    citizen_phone: str
    citizen_email: Optional[str] = None
    service_id: int
    booking_date: date
    booking_time: time
    notes: Optional[str] = None

class QueueBookingResponse(BaseModel):
    id: int
    queue_number: str
    citizen_name: str
    citizen_phone: str
    citizen_email: Optional[str]
    province_name: str
    district_name: str
    service_name: str
    booking_date: date
    booking_time: time
    status: QueueStatus
    notes: Optional[str]
    created_at: datetime
    province_id: int
    district_id: int
    service_id: int

class ServiceCreate(BaseModel):
    name: str

class DistrictCreate(BaseModel):
    name: str
    services: List[ServiceCreate]

class ProvinceCreate(BaseModel):
    name: str
    districts: List[DistrictCreate]

class ProvinceUpdate(BaseModel):
    name: str

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_database():
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS provinces (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS districts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    province_id INTEGER REFERENCES provinces(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS services (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    district_id INTEGER REFERENCES districts(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
                    embedding vector(1024),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS queue_bookings (
                    id SERIAL PRIMARY KEY,
                    queue_number VARCHAR(20) UNIQUE NOT NULL,
                    citizen_name VARCHAR(100) NOT NULL,
                    citizen_phone VARCHAR(20) NOT NULL,
                    citizen_email VARCHAR(100),
                    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
                    booking_date DATE NOT NULL,
                    booking_time TIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("CREATE INDEX IF NOT EXISTS idx_district_province ON districts(province_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_service_district ON services(district_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_document_service ON documents(service_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_queue_service ON queue_bookings(service_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_queue_date ON queue_bookings(booking_date);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON queue_bookings(status);")

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()

init_database()

def get_service_by_id(service_id: int):
    """Get service info and related IDs by service_id"""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT s.id as service_id, d.id as district_id, p.id as province_id,
                   s.name as service_name, d.name as district_name, p.name as province_name
            FROM services s
            JOIN districts d ON s.district_id = d.id
            JOIN provinces p ON d.province_id = p.id
            WHERE s.id = %s
        """, (service_id,))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"ไม่พบบริการ ID: {service_id}")
        return result

def generate_queue_number(service_id: int, booking_date: date) -> str:
    """Generate unique queue number"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        # Count bookings for the same service and date
        cur.execute("""
            SELECT COUNT(*) FROM queue_bookings 
            WHERE service_id = %s AND booking_date = %s
        """, (service_id, booking_date))
        count = cur.fetchone()[0]
        return f"Q{service_id:03d}{booking_date.strftime('%m%d')}{count+1:03d}"

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    try:
        pdf_content = pdf_file.file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))

        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="ไม่สามารถดึงข้อความจากไฟล์ PDF ได้")

        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"เกิดข้อผิดพลาดในการอ่านไฟล์ PDF: {str(e)}")

def create_embedding(text: str):
    try:
        embedding = embedder.encode(text)
        return embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการสร้าง embedding: {str(e)}")

def save_document_to_db(content: str, service_info: dict):
    try:
        embedding = create_embedding(content)
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO documents (content, service_id, embedding)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (content, service_info['service_id'], embedding))
            doc_id = cur.fetchone()[0]
            conn.commit()
            return doc_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการบันทึกเอกสาร: {str(e)}")

def search_similar_documents(query: str):
    try:
        query_embedding = create_embedding(query)
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # ค้นหาในทุกเอกสาร ไม่มีการ filter
            base_query = """
                SELECT d.id, d.content, s.name AS service, dt.name AS district, p.name AS province,
                       d.embedding <=> %s::vector AS similarity,
                       s.id as service_id, dt.id as district_id, p.id as province_id
                FROM documents d
                JOIN services s ON d.service_id = s.id
                JOIN districts dt ON s.district_id = dt.id
                JOIN provinces p ON dt.province_id = p.id
                ORDER BY similarity ASC LIMIT 1
            """
            
            cur.execute(base_query, [query_embedding])
            results = cur.fetchall()
            return [dict(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการค้นหาเอกสาร: {str(e)}")

def generate_answer_with_ollama(question: str, context_documents: List[dict]) -> str:
    try:
        context = "\n\n".join([doc['content'][:1000] for doc in context_documents[:3]])
        prompt = f"""
        ตอบคำถามต่อไปนี้โดยใช้ข้อมูลจากเอกสารที่เกี่ยวข้อง:

        คำถาม: {question}

        ข้อมูลอ้างอิง:
        {context}

        กรุณาตอบเป็นภาษาไทยและให้ข้อมูลที่ถูกต้องตามเอกสารที่ให้มา หากไม่มีข้อมูลในเอกสาร ให้บอกว่าไม่พบข้อมูลที่เกี่ยวข้อง
        """
        response = ollama.chat(model="qwen2.5:3b", messages=[
            {"role": "system", "content": "คุณเป็นผู้ช่วยตอบคำถามภาษาไทย ตอบด้วยความสุภาพและให้ข้อมูลที่ถูกต้อง ใช้คำว่า 'ครับ' หรือ 'ค่ะ' ตามความเหมาะสม"},
            {"role": "user", "content": prompt}
        ])
        return response["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการสร้างคำตอบ: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Document Management System with Queue Booking API v3", "version": "3.0.0"}

@app.post("/provinces/full")
async def create_province_full(data: ProvinceCreate):
    """
    Create full province structure
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO provinces (name) VALUES (%s) RETURNING id", (data.name,))
            province_id = cur.fetchone()[0]

            for district in data.districts:
                cur.execute("INSERT INTO districts (name, province_id) VALUES (%s, %s) RETURNING id", (district.name, province_id))
                district_id = cur.fetchone()[0]

                for service in district.services:
                    cur.execute("INSERT INTO services (name, district_id) VALUES (%s, %s) RETURNING id", (service.name, district_id))

            conn.commit()
            return {"id": province_id, "name": data.name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการสร้างข้อมูลแบบลำดับชั้น: {str(e)}")

# Province CRUD operations
@app.post("/provinces")
async def create_province(name: str):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO provinces (name) VALUES (%s) RETURNING id", (name,))
            province_id = cur.fetchone()[0]
            conn.commit()
            return {"id": province_id, "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/provinces")
async def list_provinces():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, name FROM provinces ORDER BY name")
            return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/provinces/{province_id}")
async def get_province(province_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, name FROM provinces WHERE id = %s", (province_id,))
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="ไม่พบจังหวัด")
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/provinces/{province_id}")
async def update_province(province_id: int, data: ProvinceUpdate):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE provinces SET name = %s WHERE id = %s", (data.name, province_id))
            conn.commit()
            return {"id": province_id, "name": data.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/provinces/{province_id}")
async def delete_province(province_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM provinces WHERE id = %s", (province_id,))
            conn.commit()
            return {"message": "ลบจังหวัดสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# District CRUD operations
@app.get("/districts")
async def list_districts(province_id: Optional[int] = None):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            if province_id:
                cur.execute("""
                    SELECT d.id, d.name, d.province_id, p.name as province_name
                    FROM districts d
                    JOIN provinces p ON d.province_id = p.id
                    WHERE d.province_id = %s
                    ORDER BY d.name
                """, (province_id,))
            else:
                cur.execute("""
                    SELECT d.id, d.name, d.province_id, p.name as province_name
                    FROM districts d
                    JOIN provinces p ON d.province_id = p.id
                    ORDER BY p.name, d.name
                """)
            return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/districts")
async def create_district(name: str, province_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO districts (name, province_id) VALUES (%s, %s) RETURNING id", (name, province_id))
            district_id = cur.fetchone()[0]
            conn.commit()
            return {"id": district_id, "name": name, "province_id": province_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/districts/{district_id}")
async def get_district(district_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT d.id, d.name, d.province_id, p.name as province_name
                FROM districts d
                JOIN provinces p ON d.province_id = p.id
                WHERE d.id = %s
            """, (district_id,))
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="ไม่พบเขต/อำเภอ")
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/districts/{district_id}")
async def update_district(district_id: int, name: str, province_id: Optional[int] = None):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            if province_id:
                cur.execute("UPDATE districts SET name = %s, province_id = %s WHERE id = %s", (name, province_id, district_id))
            else:
                cur.execute("UPDATE districts SET name = %s WHERE id = %s", (name, district_id))
            conn.commit()
            return {"id": district_id, "name": name, "province_id": province_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/districts/{district_id}")
async def delete_district(district_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM districts WHERE id = %s", (district_id,))
            conn.commit()
            return {"message": "ลบเขต/อำเภอสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Service CRUD operations
@app.get("/services")
async def list_services(district_id: Optional[int] = None, province_id: Optional[int] = None):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT s.id, s.name, s.district_id, d.name as district_name, 
                       p.id as province_id, p.name as province_name
                FROM services s
                JOIN districts d ON s.district_id = d.id
                JOIN provinces p ON d.province_id = p.id
            """
            params = []
            conditions = []
            
            if district_id:
                conditions.append("s.district_id = %s")
                params.append(district_id)
            elif province_id:
                conditions.append("p.id = %s")
                params.append(province_id)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY p.name, d.name, s.name"
            
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/services")
async def create_service(name: str, district_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO services (name, district_id) VALUES (%s, %s) RETURNING id", (name, district_id))
            service_id = cur.fetchone()[0]
            conn.commit()
            return {"id": service_id, "name": name, "district_id": district_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/{service_id}")
async def get_service(service_id: int):
    try:
        service_info = get_service_by_id(service_id)
        return service_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/services/{service_id}")
async def update_service(service_id: int, name: str, district_id: Optional[int] = None):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            if district_id:
                cur.execute("UPDATE services SET name = %s, district_id = %s WHERE id = %s", (name, district_id, service_id))
            else:
                cur.execute("UPDATE services SET name = %s WHERE id = %s", (name, service_id))
            conn.commit()
            return {"id": service_id, "name": name, "district_id": district_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/services/{service_id}")
async def delete_service(service_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
            conn.commit()
            return {"message": "ลบบริการสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document upload endpoints
@app.post("/upload/pdf", response_model=DocumentResponse)
async def upload_pdf_document(
    file: UploadFile = File(...),
    service_id: int = Form(...)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์ PDF เท่านั้น")
    
    service_info = get_service_by_id(service_id)
    text_content = extract_text_from_pdf(file)
    doc_id = save_document_to_db(text_content, service_info)
    
    return DocumentResponse(
        id=doc_id, 
        message=f"อัปโหลดและบันทึกไฟล์ PDF สำเร็จ ID: {doc_id}",
        province_id=service_info['province_id'],
        district_id=service_info['district_id'],
        service_id=service_info['service_id'],
        province_name=service_info['province_name'],
        district_name=service_info['district_name'],
        service_name=service_info['service_name']
    )

@app.post("/upload/text", response_model=DocumentResponse)
async def upload_text_document(
    file: UploadFile = File(...),
    service_id: int = Form(...)
):
    if not file.filename.lower().endswith(('.txt', '.text')):
        raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์ text (.txt) เท่านั้น")
    
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="ไฟล์ text ว่างเปล่า")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="ไฟล์ text ต้องเป็น encoding UTF-8")
    
    service_info = get_service_by_id(service_id)
    doc_id = save_document_to_db(text_content, service_info)
    
    return DocumentResponse(
        id=doc_id, 
        message=f"อัปโหลดและบันทึกไฟล์ text สำเร็จ ID: {doc_id}",
        province_id=service_info['province_id'],
        district_id=service_info['district_id'],
        service_id=service_info['service_id'],
        province_name=service_info['province_name'],
        district_name=service_info['district_name'],
        service_name=service_info['service_name']
    )

@app.post("/add/text", response_model=DocumentResponse)
async def add_text_directly(text_input: TextInput):
    if not text_input.text.strip():
        raise HTTPException(status_code=400, detail="กรุณาใส่ข้อความ")
    
    service_info = get_service_by_id(text_input.service_id)
    doc_id = save_document_to_db(text_input.text, service_info)
    
    return DocumentResponse(
        id=doc_id, 
        message=f"บันทึกข้อความสำเร็จ ID: {doc_id}",
        province_id=service_info['province_id'],
        district_id=service_info['district_id'],
        service_id=service_info['service_id'],
        province_name=service_info['province_name'],
        district_name=service_info['district_name'],
        service_name=service_info['service_name']
    )

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_documents(query_request: QueryRequest):
    if not query_request.question.strip():
        raise HTTPException(status_code=400, detail="กรุณาใส่คำถาม")
    
    # ค้นหาในทุกเอกสาร ไม่มีการ filter
    similar_docs = search_similar_documents(query_request.question)
    
    if not similar_docs:
        return QueryResponse(
            answer="ไม่พบเอกสารที่เกี่ยวข้อง", 
            relevant_documents=[]
        )
    
    answer = generate_answer_with_ollama(query_request.question, similar_docs)
    
    relevant_docs = []
    
    for doc in similar_docs:
        relevant_docs.append({
            "id": doc['id'],
            "content_preview": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
            "province": doc['province'],
            "district": doc['district'],
            "service": doc['service'],
            "similarity_score": float(doc['similarity']),
            "province_id": doc['province_id'],
            "district_id": doc['district_id'],
            "service_id": doc['service_id']
        })
    
    return QueryResponse(
        answer=answer, 
        relevant_documents=relevant_docs
    )

# Queue booking endpoints
@app.post("/queue/book", response_model=QueueBookingResponse)
async def book_queue(booking: QueueBookingCreate):
    try:
        service_info = get_service_by_id(booking.service_id)
        queue_number = generate_queue_number(service_info['service_id'], booking.booking_date)
        
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                INSERT INTO queue_bookings (
                    queue_number, citizen_name, citizen_phone, citizen_email,
                    service_id, booking_date, booking_time, status, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                queue_number, booking.citizen_name, booking.citizen_phone, booking.citizen_email,
                service_info['service_id'], booking.booking_date, booking.booking_time, 
                QueueStatus.PENDING, booking.notes
            ))
            result = cur.fetchone()
            conn.commit()
            
            return QueueBookingResponse(
                **dict(result),
                province_name=service_info['province_name'],
                district_name=service_info['district_name'],
                service_name=service_info['service_name'],
                province_id=service_info['province_id'],
                district_id=service_info['district_id']
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการจองคิว: {str(e)}")

@app.get("/queue/bookings")
async def list_queue_bookings(
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    service_id: Optional[int] = None,
    booking_date: Optional[date] = None,
    status: Optional[QueueStatus] = None
):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT qb.*, s.name as service_name, d.name as district_name, p.name as province_name,
                       s.id as service_id, d.id as district_id, p.id as province_id
                FROM queue_bookings qb
                JOIN services s ON qb.service_id = s.id
                JOIN districts d ON s.district_id = d.id
                JOIN provinces p ON d.province_id = p.id
            """
            
            conditions = []
            params = []
            
            if province_id:
                conditions.append("p.id = %s")
                params.append(province_id)
            if district_id:
                conditions.append("d.id = %s")
                params.append(district_id)
            if service_id:
                conditions.append("s.id = %s")
                params.append(service_id)
            if booking_date:
                conditions.append("qb.booking_date = %s")
                params.append(booking_date)
            if status:
                conditions.append("qb.status = %s")
                params.append(status.value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY qb.booking_date, qb.booking_time"
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            return [QueueBookingResponse(**dict(result)) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลคิว: {str(e)}")

@app.get("/queue/bookings/{booking_id}")
async def get_queue_booking(booking_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT qb.*, s.name as service_name, d.name as district_name, p.name as province_name,
                       s.id as service_id, d.id as district_id, p.id as province_id
                FROM queue_bookings qb
                JOIN services s ON qb.service_id = s.id
                JOIN districts d ON s.district_id = d.id
                JOIN provinces p ON d.province_id = p.id
                WHERE qb.id = %s
            """, (booking_id,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="ไม่พบการจองคิว")
            
            return QueueBookingResponse(**dict(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลคิว: {str(e)}")

@app.put("/queue/{booking_id}/status")
async def update_queue_status(booking_id: int, status: QueueStatus):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE queue_bookings 
                SET status = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (status.value, booking_id))
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="ไม่พบการจองคิว")
            
            conn.commit()
            return {"message": f"อัปเดตสถานะคิวเป็น {status.value} สำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการอัปเดตสถานะ: {str(e)}")

@app.delete("/queue/{booking_id}")
async def delete_queue_booking(booking_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM queue_bookings WHERE id = %s", (booking_id,))
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="ไม่พบการจองคิว")
            
            conn.commit()
            return {"message": "ลบการจองคิวสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบการจองคิว: {str(e)}")

@app.get("/queue/statistics")
async def get_queue_statistics(
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    service_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
                    COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_count,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_count,
                    p.name as province_name, d.name as district_name, s.name as service_name,
                    p.id as province_id, d.id as district_id, s.id as service_id
                FROM queue_bookings qb
                JOIN services s ON qb.service_id = s.id
                JOIN districts d ON s.district_id = d.id
                JOIN provinces p ON d.province_id = p.id
            """
            
            conditions = []
            params = []
            
            if province_id:
                conditions.append("p.id = %s")
                params.append(province_id)
            if district_id:
                conditions.append("d.id = %s")
                params.append(district_id)
            if service_id:
                conditions.append("s.id = %s")
                params.append(service_id)
            if start_date:
                conditions.append("qb.booking_date >= %s")
                params.append(start_date)
            if end_date:
                conditions.append("qb.booking_date <= %s")
                params.append(end_date)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " GROUP BY p.id, p.name, d.id, d.name, s.id, s.name ORDER BY p.name, d.name, s.name"
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            return [dict(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงสถิติคิว: {str(e)}")

@app.get("/structure")
async def get_structure():
    """Get complete hierarchical structure"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT
                    p.id AS province_id,
                    p.name AS province_name,
                    d.id AS district_id,
                    d.name AS district_name,
                    s.id AS service_id,
                    s.name AS service_name
                FROM provinces p
                LEFT JOIN districts d ON d.province_id = p.id
                LEFT JOIN services s ON s.district_id = d.id
                ORDER BY p.name, d.name, s.name
            """)
            rows = cur.fetchall()

            structure = {}
            for row in rows:
                province_id = row['province_id']
                district_id = row['district_id']
                service_id = row['service_id']

                if province_id not in structure:
                    structure[province_id] = {
                        "id": province_id,
                        "name": row['province_name'],
                        "districts": {}
                    }

                if district_id and district_id not in structure[province_id]["districts"]:
                    structure[province_id]["districts"][district_id] = {
                        "id": district_id,
                        "name": row['district_name'],
                        "services": []
                    }

                if service_id and district_id:
                    structure[province_id]["districts"][district_id]["services"].append({
                        "id": service_id,
                        "name": row['service_name']
                    })

            # Convert to list format
            provinces = []
            for p in structure.values():
                p["districts"] = list(p["districts"].values())
                provinces.append(p)

            return provinces

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการโหลดโครงสร้างข้อมูล: {str(e)}")

@app.get("/documents")
async def list_documents(
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    service_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0
):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT d.id, d.content, d.created_at,
                       s.id as service_id, s.name as service_name,
                       dt.id as district_id, dt.name as district_name,
                       p.id as province_id, p.name as province_name
                FROM documents d
                JOIN services s ON d.service_id = s.id
                JOIN districts dt ON s.district_id = dt.id
                JOIN provinces p ON dt.province_id = p.id
            """
            
            conditions = []
            params = []
            
            if province_id:
                conditions.append("p.id = %s")
                params.append(province_id)
            if district_id:
                conditions.append("dt.id = %s")
                params.append(district_id)
            if service_id:
                conditions.append("s.id = %s")
                params.append(service_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY d.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            # Also get total count
            count_query = """
                SELECT COUNT(*) as total
                FROM documents d
                JOIN services s ON d.service_id = s.id
                JOIN districts dt ON s.district_id = dt.id
                JOIN provinces p ON dt.province_id = p.id
            """
            
            count_params = []
            if province_id:
                count_query += " WHERE p.id = %s"
                count_params.append(province_id)
                if district_id:
                    count_query += " AND dt.id = %s"
                    count_params.append(district_id)
                if service_id:
                    count_query += " AND s.id = %s"
                    count_params.append(service_id)
            elif district_id:
                count_query += " WHERE dt.id = %s"
                count_params.append(district_id)
                if service_id:
                    count_query += " AND s.id = %s"
                    count_params.append(service_id)
            elif service_id:
                count_query += " WHERE s.id = %s"
                count_params.append(service_id)
            
            cur.execute(count_query, count_params)
            total = cur.fetchone()['total']
            
            return {
                "documents": [dict(result) for result in results],
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลเอกสาร: {str(e)}")

@app.get("/documents/{document_id}")
async def get_document(document_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT d.id, d.content, d.created_at,
                       s.id as service_id, s.name as service_name,
                       dt.id as district_id, dt.name as district_name,
                       p.id as province_id, p.name as province_name
                FROM documents d
                JOIN services s ON d.service_id = s.id
                JOIN districts dt ON s.district_id = dt.id
                JOIN provinces p ON dt.province_id = p.id
                WHERE d.id = %s
            """, (document_id,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="ไม่พบเอกสาร")
            
            return dict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลเอกสาร: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="ไม่พบเอกสาร")
            
            conn.commit()
            return {"message": "ลบเอกสารสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบเอกสาร: {str(e)}")

@app.get("/documents/count")
async def get_document_count(
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    service_id: Optional[int] = None
):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            if service_id:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_documents,
                        p.name as province_name,
                        dt.name as district_name,
                        s.name as service_name,
                        s.id as service_id,
                        dt.id as district_id,
                        p.id as province_id
                    FROM documents d
                    JOIN services s ON d.service_id = s.id
                    JOIN districts dt ON s.district_id = dt.id
                    JOIN provinces p ON dt.province_id = p.id
                    WHERE s.id = %s
                    GROUP BY p.id, p.name, dt.id, dt.name, s.id, s.name
                """, (service_id,))
            elif district_id:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_documents,
                        COUNT(DISTINCT d.service_id) as services_with_documents,
                        p.name as province_name,
                        dt.name as district_name,
                        s.name as service_name,
                        s.id as service_id,
                        dt.id as district_id,
                        p.id as province_id
                    FROM documents d
                    JOIN services s ON d.service_id = s.id
                    JOIN districts dt ON s.district_id = dt.id
                    JOIN provinces p ON dt.province_id = p.id
                    WHERE dt.id = %s
                    GROUP BY p.id, p.name, dt.id, dt.name, s.id, s.name
                    ORDER BY s.name
                """, (district_id,))
            elif province_id:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_documents,
                        COUNT(DISTINCT d.service_id) as services_with_documents,
                        p.name as province_name,
                        dt.name as district_name,
                        s.name as service_name,
                        s.id as service_id,
                        dt.id as district_id,
                        p.id as province_id
                    FROM documents d
                    JOIN services s ON d.service_id = s.id
                    JOIN districts dt ON s.district_id = dt.id
                    JOIN provinces p ON dt.province_id = p.id
                    WHERE p.id = %s
                    GROUP BY p.id, p.name, dt.id, dt.name, s.id, s.name
                    ORDER BY dt.name, s.name
                """, (province_id,))
            else:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_documents,
                        COUNT(DISTINCT d.service_id) as services_with_documents,
                        p.name as province_name,
                        dt.name as district_name,
                        s.name as service_name,
                        s.id as service_id,
                        dt.id as district_id,
                        p.id as province_id
                    FROM documents d
                    JOIN services s ON d.service_id = s.id
                    JOIN districts dt ON s.district_id = dt.id
                    JOIN provinces p ON dt.province_id = p.id
                    GROUP BY p.id, p.name, dt.id, dt.name, s.id, s.name
                    ORDER BY p.name, dt.name, s.name
                """)
            
            results = cur.fetchall()
            
            total_count = sum(result['total_documents'] for result in results)
            
            return {
                "total_documents": total_count,
                "by_service": [dict(result) for result in results]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/suggestions")
async def get_search_suggestions(query: str):
    """Get search suggestions based on document content"""
    try:
        if len(query.strip()) < 2:
            return {"suggestions": []}
        
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # ค้นหาในทุกเอกสาร ไม่มีการ filter
            base_query = """
                SELECT DISTINCT 
                    SUBSTRING(d.content, 1, 100) as content_preview,
                    s.name AS service, dt.name AS district, p.name AS province,
                    s.id as service_id, dt.id as district_id, p.id as province_id
                FROM documents d
                JOIN services s ON d.service_id = s.id
                JOIN districts dt ON s.district_id = dt.id
                JOIN provinces p ON dt.province_id = p.id
                WHERE d.content ILIKE %s
                LIMIT 10
            """
            
            cur.execute(base_query, [f"%{query}%"])
            results = cur.fetchall()
            
            return {"suggestions": [dict(result) for result in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการค้นหาคำแนะนำ: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)