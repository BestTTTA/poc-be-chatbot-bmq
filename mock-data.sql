-- ============================================
-- Mockup Data for Document Management System
-- Bangkok Only - Starting with Bang Khen District
-- ============================================

-- Clear existing data (optional - use with caution)
-- DELETE FROM queue_bookings;
-- DELETE FROM documents;
-- DELETE FROM services;
-- DELETE FROM districts;
-- DELETE FROM provinces;

-- ============================================
-- 1. INSERT PROVINCES (Bangkok Only)
-- ============================================
INSERT INTO provinces (name) VALUES 
('กรุงเทพมหานคร')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 2. INSERT DISTRICTS (Bangkok Only)
-- ============================================
INSERT INTO districts (name, province_id) VALUES 
-- กรุงเทพมหานคร
('บางเขน', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('บางรัก', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('ปทุมวัน', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('วัฒนา', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('คลองเตย', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('ยานนาวา', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('บางกะปิ', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')),
('หลักสี่', (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร'));

-- ============================================
-- 3. INSERT SERVICES (Bangkok Only)
-- ============================================
INSERT INTO services (name, district_id) VALUES 
-- บางเขน
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'บางเขน')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'บางเขน')),
('ใบอนุญาตก่อสร้าง', (SELECT id FROM districts WHERE name = 'บางเขน')),
('ภาษีโรงเรือนและที่ดิน', (SELECT id FROM districts WHERE name = 'บางเขน')),
('สาธารณสุขและสิ่งแวดล้อม', (SELECT id FROM districts WHERE name = 'บางเขน')),
('การศึกษา', (SELECT id FROM districts WHERE name = 'บางเขน')),
('สวัสดิการสังคม', (SELECT id FROM districts WHERE name = 'บางเขน')),
('การจราจรและขนส่ง', (SELECT id FROM districts WHERE name = 'บางเขน')),

-- บางรัก
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'บางรัก')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'บางรัก')),
('การท่องเที่ยว', (SELECT id FROM districts WHERE name = 'บางรัก')),
('ภาษีโรงเรือนและที่ดิน', (SELECT id FROM districts WHERE name = 'บางรัก')),

-- ปทุมวัน
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'ปทุมวัน')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'ปทุมวัน')),
('การพาณิชย์', (SELECT id FROM districts WHERE name = 'ปทุมวัน')),
('ภาษีและการเงิน', (SELECT id FROM districts WHERE name = 'ปทุมวัน')),

-- วัฒนา
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'วัฒนา')),
('ใบอนุญาตก่อสร้าง', (SELECT id FROM districts WHERE name = 'วัฒนา')),
('การศึกษา', (SELECT id FROM districts WHERE name = 'วัฒนา')),
('สาธารณสุข', (SELECT id FROM districts WHERE name = 'วัฒนา')),

-- คลองเตย
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'คลองเตย')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'คลองเตย')),
('การขนส่งสินค้า', (SELECT id FROM districts WHERE name = 'คลองเตย')),
('ภาษีโรงเรือนและที่ดิน', (SELECT id FROM districts WHERE name = 'คลองเตย')),

-- ยานนาวา
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'ยานนาวา')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'ยานนาวา')),
('การศึกษา', (SELECT id FROM districts WHERE name = 'ยานนาวา')),
('สาธารณสุข', (SELECT id FROM districts WHERE name = 'ยานนาวา')),

-- บางกะปิ
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'บางกะปิ')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'บางกะปิ')),
('การศึกษา', (SELECT id FROM districts WHERE name = 'บางกะปิ')),
('สาธารณสุข', (SELECT id FROM districts WHERE name = 'บางกะปิ')),

-- หลักสี่
('ทะเบียนราษฎร', (SELECT id FROM districts WHERE name = 'หลักสี่')),
('ใบอนุญาตประกอบธุรกิจ', (SELECT id FROM districts WHERE name = 'หลักสี่')),
('การศึกษา', (SELECT id FROM districts WHERE name = 'หลักสี่')),
('สาธารณสุข', (SELECT id FROM districts WHERE name = 'หลักสี่'));

-- ============================================
-- 4. INSERT DOCUMENTS (without embeddings first)
-- ============================================
INSERT INTO documents (content, service_id, created_at) VALUES 
-- ทะเบียนราษฎร - บางเขน
('วิธีการสมัครทะเบียนราษฎร สำหรับเขตบางเขน
ขั้นตอนการสมัคร:
1. เตรียมเอกสาร: สำเนาบัตรประชาชน, สำเนาทะเบียนบ้าน, รูปถ่าย 1 นิ้ว จำนวน 2 รูป
2. กรอกแบบฟอร์มคำขอ ฟ.ทร.1
3. ยื่นเอกสารที่สำนักงานเขตบางเขน ชั้น 2 ห้อง 201
4. ชำระค่าธรรมเนียม 20 บาท
5. รอรับบัตรประชาชนใหม่ ใช้เวลา 15 วันทำการ
วันเวลาให้บริการ: จันทร์-ศุกร์ 08:30-16:30 น.
ติดต่อสอบถาม: 02-123-4567', 
(SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
'2025-07-01 09:00:00'),

('เอกสารที่ต้องใช้ในการขอทะเบียนราษฎร เขตบางเขน
เอกสารสำหรับคนไทย:
- บัตรประชาชน (ต้นฉบับ + สำเนา)
- ทะเบียนบ้าน (ต้นฉบับ + สำเนา)
- หนังสือรับรองการเปลี่ยนชื่อ-สกุล (ถ้ามี)
- รูปถ่าย 1 นิ้ว จำนวน 2 รูป (ถ่ายมาแล้วไม่เกิน 6 เดือน)

เอกสารสำหรับชาวต่างชาติ:
- หนังสือเดินทาง
- ใบอนุญาตทำงาน
- หนังสือรับรองจากสถานทูต
- รูปถ่าย 1 นิ้ว จำนวน 3 รูป

หมายเหตุ: เอกสารทั้งหมดต้องไม่หมดอายุ', 
(SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
'2025-07-02 10:30:00'),

-- ใบอนุญาตประกอบธุรกิจ - บางเขน
('คู่มือการขอใบอนุญาตประกอบธุรกิจ เขตบางเขน
ประเภทธุรกิจที่ต้องขออนุญาต:
1. ร้านอาหาร และเครื่องดื่ม
2. โรงแรม และที่พักแรม
3. ร้านตัดผม และเสริมสวย
4. อู่ซ่อมรถยนต์
5. สถานบันเทิง
6. โรงงานขนาดเล็ก

ขั้นตอนการขออนุญาต:
1. ศึกษาข้อกำหนดของประเภทธุรกิจ
2. เตรียมเอกสารประกอบการขออนุญาต
3. กรอกแบบฟอร์มคำขอ
4. ยื่นคำขอพร้อมเอกสาร
5. ชำระค่าธรรมเนียม
6. รอการตรวจสอบ และออกใบอนุญาต

ระยะเวลาดำเนินการ: 15-30 วันทำการ
ค่าธรรมเนียน: 500-2,000 บาท (ขึ้นอยู่กับประเภทธุรกิจ)', 
(SELECT id FROM services WHERE name = 'ใบอนุญาตประกอบธุรกิจ' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
'2025-07-03 14:15:00'),

-- ใบอนุญาตก่อสร้าง - บางเขน
('การขอใบอนุญาตก่อสร้าง เขตบางเขน
ประเภทงานก่อสร้างที่ต้องขออนุญาต:
- ก่อสร้างอาคาร
- ดัดแปลงอาคาร
- เคลื่อนย้ายอาคาร
- รื้อถอนอาคาร

เอกสารที่ต้องใช้:
1. แบบแปลนก่อสร้าง (จำนวน 5 ชุด)
2. รายการคำนวณ โครงสร้าง
3. สำเนาโฉนดที่ดิน
4. สำเนาบัตรประชาชนผู้ขออนุญาต
5. หนังสือมอบอำนาจ (กรณีมอบหมาย)
6. ใบอนุญาตเป็นผู้ประกอบวิชาชีพวิศวกรรม

ขั้นตอนการขออนุญาต:
1. ยื่นคำขอพร้อมเอกสาร
2. เจ้าหน้าที่ตรวจสอบเอกสาร
3. สำรวจพื้นที่ก่อสร้าง
4. พิจารณาออกใบอนุญาต
5. ชำระค่าธรรมเนียม และรับใบอนุญาต

ระยะเวลา: 30 วันทำการ
ค่าธรรมเนียม: คำนวณตามขนาดพื้นที่ก่อสร้าง', 
(SELECT id FROM services WHERE name = 'ใบอนุญาตก่อสร้าง' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
'2025-07-04 11:20:00'),

-- ภาษีโรงเรือนและที่ดิน - บางเขน
('การชำระภาษีโรงเรือนและที่ดิน เขตบางเขน
กำหนดชำระภาษี:
- งวดที่ 1: เดือนมีนาคม - เมษายน
- งวดที่ 2: เดือนกันยายน - ตุลาคม

วิธีการชำระ:
1. ชำระที่สำนักงานเขต (เคาน์เตอร์ 1-3)
2. ชำระผ่านธนาคาร (กรุงไทย, กสิกรไทย, ไทยพาณิชย์)
3. ชำระผ่าน Mobile Banking
4. ชำระผ่าน 7-Eleven

เอกสารที่ต้องนำมา:
- ใบแจ้งภาษี
- บัตรประชาชน
- สำเนาทะเบียนบ้าน

อัตราภาษี:
- ที่ดินว่างเปล่า: 0.3% ของราคาประเมิน
- ที่ดินที่มีสิ่งปลูกสร้าง: 0.7% ของราคาประเมิน
- อาคารพาณิชย์: 1.0% ของราคาประเมิน

การขอผ่อนผันหรือลดหย่อน:
- ผู้สูงอายุ 60 ปีขึ้นไป
- ผู้พิการ
- ผู้มีรายได้น้อย', 
(SELECT id FROM services WHERE name = 'ภาษีโรงเรือนและที่ดิน' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
'2025-07-05 16:45:00'),

-- สาธารณสุขและสิ่งแวดล้อม - บางเขน
('บริการสาธารณสุขและสิ่งแวดล้อม เขตบางเขน
บริการที่ให้:
1. การตรวจสุขภาพประจำปี
2. การฉีดวัคซีนป้องกันโรค
3. การรณรงค์สุขภาพ
4. การตรวจคุณภาพน้ำ
5. การควบคุมโรคติดต่อ
6. การจัดการขยะและสิ่งแวดล้อม

ศูนย์สุขภาพชุมชน เขตบางเขน:
- ศูนย์สุขภาพชุมชนบางเขน 1 (ซอยเสรีไทย 10)
- ศูนย์สุขภาพชุมชนบางเขน 2 (ถนนรามอินทรา กม.8)
- ศูนย์สุขภาพชุมชนบางเขน 3 (ซอยนวมินทร์ 42)

บริการฟรี:
- การตรวจสุขภาพพื้นฐาน
- การฉีดวัคซีนตามปฏิทิน
- การให้คำปรึกษาด้านสุขภาพ

การรายงานปัญหาสิ่งแวดล้อม:
โทร: 02-123-4580
Line: @bangkhen_health
Email: health@bangkhen.go.th', 
(SELECT id FROM services WHERE name = 'สาธารณสุขและสิ่งแวดล้อม' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
'2025-07-06 13:30:00'),

-- ทะเบียนราษฎร - บางรัก
('บริการทะเบียนราษฎร เขตบางรัก
บริการที่ให้:
- การขอใหม่/เปลี่ยน/แก้ไข บัตรประชาชน
- การย้ายที่อยู่
- การขอหนังสือรับรองสถานภาพ
- การขอสำเนาทะเบียนราษฎร

ช่องทางการให้บริการ:
1. หน้าเคาน์เตอร์สำนักงาน (ชั้น 1)
2. บริการเคลื่อนที่ (Mobile Service)
3. ออนไลน์ผ่านแอป "ธรรมาภิบาล"

เวลาให้บริการ:
จันทร์-ศุกร์: 08:30-12:00 และ 13:00-16:30
วันพฤติหัสบดี: ขยายเวลาถึง 20:00 น.
วันเสาร์: 09:00-15:00 (เฉพาะวันเสาร์แรกของเดือน)

การนัดหมายล่วงหน้า:
- โทรศัพท์: 02-234-5678
- Line: @bangrak_registration
- Website: www.bangrak.go.th', 
(SELECT id FROM services WHERE name = 'ทะเบียนราษฏร' AND district_id = (SELECT id FROM districts WHERE name = 'บางรัก')), 
'2025-07-07 09:15:00'),

-- การท่องเที่ยว - บางรัก
('การขอใบอนุญาตธุรกิจท่องเที่ยว เขตบางรัก
ประเภทธุรกิจที่ครอบคลุม:
1. โรงแรม และเกสต์เฮาส์
2. ร้านอาหารสำหรับนักท่องเที่ยว  
3. ร้านขายของที่ระลึก
4. บริษัทนำเที่ยว
5. ร้านสปาและนวด
6. ภัตตาคารต่างชาติ

ข้อกำหนดพิเศษสำหรับเขตบางรัก:
- ต้องผ่านการรับรองมาตรฐานการท่องเที่ยว
- มีป้ายแสดงข้อมูลเป็นภาษาอังกฤษ
- พนักงานต้องสื่อสารภาษาอังกฤษได้

เอกสารประกอบการขออนุญาต:
1. แผนผังสถานที่ประกอบการ
2. รายการอุปกรณ์และเครื่องมือ
3. หนังสือรับรองสุขภาพ (สำหรับธุรกิจอาหาร)
4. ใบรับรองการอบรมด้านการท่องเที่ยว
5. ใบอนุญาตจากหน่วยงานที่เกี่ยวข้อง

ค่าธรรมเนียม:
- โรงแรม: 3,000 บาท/ปี
- ร้านอาหาร: 1,500 บาท/ปี  
- ร้านค้าของที่ระลึก: 800 บาท/ปี
- บริษัทนำเที่ยว: 5,000 บาท/ปี', 
(SELECT id FROM services WHERE name = 'การท่องเที่ยว' AND district_id = (SELECT id FROM districts WHERE name = 'บางรัก')), 
'2025-07-08 15:45:00'),

-- การพาณิชย์ - ปทุมวัน
('บริการการพาณิชย์ เขตปทุมวัน
บริการที่ให้:
1. การขึ้นทะเบียนพาณิชย์
2. การต่ออายุใบทะเบียนพาณิชย์
3. การแก้ไขเปลี่ยนแปลงใบทะเบียนพาณิชย์
4. การยกเลิกใบทะเบียนพาณิชย์

เอกสารที่ต้องใช้:
- สำเนาบัตรประชาชน
- สำเนาทะเบียนบ้าน
- หนังสือยินยอมให้ใช้สถานที่
- แผนที่แสดงที่ตั้งสถานประกอบการ

ค่าธรรมเนียม:
- ทะเบียนพาณิชย์: 50 บาท
- การแก้ไขเปลี่ยนแปลง: 30 บาท
- การต่ออายุ: 50 บาท

สถานที่ให้บริการ: ชั้น 3 สำนักงานเขตปทุมวัน
เวลาให้บริการ: จันทร์-ศุกร์ 08:30-16:30 น.', 
(SELECT id FROM services WHERE name = 'การพาณิชย์' AND district_id = (SELECT id FROM districts WHERE name = 'ปทุมวัน')), 
'2025-07-09 11:00:00'),

-- การศึกษา - วัฒนา
('บริการการศึกษา เขตวัฒนา
บริการที่ให้:
1. การรับสมัครเด็กเข้าเรียนในโรงเรียนเขต
2. การขอย้ายโรงเรียน
3. การขอเอกสารทางการศึกษา
4. โครงการพัฒนาการศึกษา

โรงเรียนในเขตวัฒนา:
- โรงเรียนวัฒนาวิทยาลัย
- โรงเรียนเบญจมราชูทิศ
- โรงเรียนเตรียมอุดมศึกษา

การสมัครเรียน:
- รอบที่ 1: มกราคม - มีนาคม
- รอบที่ 2: เมษายน - พฤษภาคม
- รอบพิเศษ: กรกฎาคม - สิงหาคม

เอกสารการสมัคร:
- สำเนาทะเบียนบ้าน
- สำเนาบัตรประชาชนผู้ปกครอง
- รูปถ่าย 1 นิ้ว จำนวน 2 รูป
- ใบรายงานผลการเรียน', 
(SELECT id FROM services WHERE name = 'การศึกษา' AND district_id = (SELECT id FROM districts WHERE name = 'วัฒนา')), 
'2025-07-10 14:30:00');

-- ============================================
-- 4.1 UPDATE DOCUMENTS WITH SAMPLE EMBEDDINGS
-- ============================================
-- Generate random embeddings for all documents
UPDATE documents SET embedding = (
    SELECT ('[' || array_to_string(array(
        SELECT (random() * 2 - 1)::text 
        FROM generate_series(1,1024)
    ), ',') || ']')::vector
) WHERE embedding IS NULL;

-- ============================================
-- 5. INSERT QUEUE BOOKINGS
-- ============================================
INSERT INTO queue_bookings (queue_number, citizen_name, citizen_phone, citizen_email, service_id, booking_date, booking_time, status, notes, created_at, updated_at) VALUES 
('Q00108030001', 'สมชาย ใจดี', '0812345678', 'somchai.jaidee@email.com', 
 (SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-03', '09:00:00', 'confirmed', 'ต้องการทำบัตรประชาชนใหม่', '2025-07-30 08:30:00', '2025-07-30 10:15:00'),

('Q00108030002', 'วันดี สดใส', '0823456789', 'wandee.sdsai@email.com', 
 (SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-03', '09:30:00', 'pending', 'ขอย้ายที่อยู่', '2025-07-30 09:45:00', '2025-07-30 09:45:00'),

('Q00208030001', 'ประสิทธิ์ การดี', '0834567890', 'prasit.karndi@email.com', 
 (SELECT id FROM services WHERE name = 'ใบอนุญาตประกอบธุรกิจ' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-03', '10:00:00', 'pending', 'ขอใบอนุญาตเปิดร้านอาหาร', '2025-07-30 10:20:00', '2025-07-30 10:20:00'),

('Q00108040001', 'สุมาลี ใจบุญ', '0845678901', 'sumalee.jaiboon@email.com', 
 (SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-04', '08:30:00', 'pending', 'ขอหนังสือรับรองสถานภาพ', '2025-07-30 11:00:00', '2025-07-30 11:00:00'),

('Q00308040001', 'ชาติชาย ดีมาก', '0856789012', 'chatichai.dimak@email.com', 
 (SELECT id FROM services WHERE name = 'ใบอนุญาตก่อสร้าง' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-04', '14:00:00', 'pending', 'ขอใบอนุญาตก่อสร้างบ้าน', '2025-07-30 12:30:00', '2025-07-30 12:30:00'),

('Q00408050001', 'ปราณี เก่งดี', '0867890123', 'pranee.kengdee@email.com', 
 (SELECT id FROM services WHERE name = 'ภาษีโรงเรือนและที่ดิน' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-05', '13:30:00', 'pending', 'ชำระภาษีโรงเรือน', '2025-07-30 13:15:00', '2025-07-30 13:15:00'),

('Q00508050001', 'นิรันดร์ รักสะอาด', '0878901234', 'nirun.raksaard@email.com', 
 (SELECT id FROM services WHERE name = 'สาธารณสุขและสิ่งแวดล้อม' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-05', '15:00:00', 'confirmed', 'ขอตรวจคุณภาพน้ำ', '2025-07-30 14:45:00', '2025-07-30 16:20:00'),

('Q00908060001', 'อรุณ สำเร็จ', '0889012345', 'arun.samret@email.com', 
 (SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางรัก')), 
 '2025-08-06', '11:00:00', 'pending', 'ต่ออายุบัตรประชาชน', '2025-07-30 15:30:00', '2025-07-30 15:30:00'),

('Q01108060001', 'สุภาพร ธุรกิจดี', '0890123456', 'supaporn.businessgood@email.com', 
 (SELECT id FROM services WHERE name = 'การท่องเที่ยว' AND district_id = (SELECT id FROM districts WHERE name = 'บางรัก')), 
 '2025-08-06', '16:00:00', 'pending', 'ขอใบอนุญาตโรงแรม', '2025-07-30 16:00:00', '2025-07-30 16:00:00'),

('Q00108070001', 'มานพ เรียนดี', '0901234567', 'manop.riandee@email.com', 
 (SELECT id FROM services WHERE name = 'ทะเบียนราษฎร' AND district_id = (SELECT id FROM districts WHERE name = 'บางเขน')), 
 '2025-08-07', '09:00:00', 'cancelled', 'ขอเปลี่ยนชื่อ-สกุล (ยกเลิกเนื่องจากติดธุระ)', '2025-07-30 17:15:00', '2025-07-30 18:45:00'),

('Q01508070001', 'สุดา การค้า', '0912345678', 'suda.karnka@email.com', 
 (SELECT id FROM services WHERE name = 'การพาณิชย์' AND district_id = (SELECT id FROM districts WHERE name = 'ปทุมวัน')), 
 '2025-08-07', '10:30:00', 'pending', 'ขึ้นทะเบียนพาณิชย์ใหม่', '2025-07-30 19:00:00', '2025-07-30 19:00:00'),

('Q01908080001', 'วิชัย เรียนดี', '0923456789', 'wichai.riandee@email.com', 
 (SELECT id FROM services WHERE name = 'การศึกษา' AND district_id = (SELECT id FROM districts WHERE name = 'วัฒนา')), 
 '2025-08-08', '14:00:00', 'confirmed', 'สมัครเรียนโรงเรียนในเขต', '2025-07-30 20:30:00', '2025-07-31 08:15:00');

-- ============================================
-- 6. VERIFICATION QUERIES
-- ============================================

-- Display summary of inserted data
SELECT 'DATA SUMMARY - BANGKOK ONLY' as info;

SELECT 
    'Provinces' as table_name,
    COUNT(*) as record_count
FROM provinces
UNION ALL
SELECT 
    'Districts' as table_name,
    COUNT(*) as record_count  
FROM districts
UNION ALL
SELECT 
    'Services' as table_name,
    COUNT(*) as record_count
FROM services
UNION ALL
SELECT 
    'Documents' as table_name,
    COUNT(*) as record_count
FROM documents
UNION ALL
SELECT 
    'Queue Bookings' as table_name,
    COUNT(*) as record_count
FROM queue_bookings;

-- Show hierarchical structure for Bangkok
SELECT 
    p.name as province,
    d.name as district,
    s.name as service,
    COUNT(doc.id) as document_count,
    COUNT(qb.id) as queue_count
FROM provinces p
LEFT JOIN districts d ON p.id = d.province_id
LEFT JOIN services s ON d.id = s.district_id
LEFT JOIN documents doc ON s.id = doc.service_id
LEFT JOIN queue_bookings qb ON s.id = qb.service_id
WHERE p.name = 'กรุงเทพมหานคร'
GROUP BY p.id, p.name, d.id, d.name, s.id, s.name
ORDER BY d.name, s.name;

-- Show queue status summary
SELECT 
    status,
    COUNT(*) as queue_count,
    MIN(booking_date) as earliest_date,
    MAX(booking_date) as latest_date
FROM queue_bookings
GROUP BY status
ORDER BY status;

-- Show districts and service counts
SELECT 
    d.name as district_name,
    COUNT(s.id) as service_count,
    COUNT(doc.id) as document_count,
    COUNT(qb.id) as queue_booking_count
FROM districts d
LEFT JOIN services s ON d.id = s.district_id
LEFT JOIN documents doc ON s.id = doc.service_id
LEFT JOIN queue_bookings qb ON s.id = qb.service_id
WHERE d.province_id = (SELECT id FROM provinces WHERE name = 'กรุงเทพมหานคร')
GROUP BY d.id, d.name
ORDER BY d.name;

-- ============================================
-- END OF SCRIPT - Bangkok Only Data Created
-- ============================================