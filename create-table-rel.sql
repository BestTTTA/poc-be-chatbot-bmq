-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Provinces
CREATE TABLE IF NOT EXISTS provinces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Districts
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    province_id INTEGER REFERENCES provinces(id) ON DELETE CASCADE
);

-- Services
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    district_id INTEGER REFERENCES districts(id) ON DELETE CASCADE
);

-- Documents (now directly linked to services, no sub_services)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    embedding vector(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Queue Bookings
CREATE TABLE IF NOT EXISTS queue_bookings (
    id SERIAL PRIMARY KEY,
    queue_number VARCHAR(20) UNIQUE NOT NULL,
    citizen_name VARCHAR(100) NOT NULL,
    citizen_phone VARCHAR(20) NOT NULL,
    citizen_email VARCHAR(100),
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast filtering
CREATE INDEX IF NOT EXISTS idx_district_province ON districts(province_id);
CREATE INDEX IF NOT EXISTS idx_service_district ON services(district_id);
CREATE INDEX IF NOT EXISTS idx_document_service ON documents(service_id);
CREATE INDEX IF NOT EXISTS idx_queue_service ON queue_bookings(service_id);
CREATE INDEX IF NOT EXISTS idx_queue_date ON queue_bookings(booking_date);
CREATE INDEX IF NOT EXISTS idx_queue_status ON queue_bookings(status);
CREATE INDEX IF NOT EXISTS idx_queue_number ON queue_bookings(queue_number);
CREATE INDEX IF NOT EXISTS idx_queue_citizen_phone ON queue_bookings(citizen_phone);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at on queue_bookings
CREATE TRIGGER update_queue_bookings_updated_at 
    BEFORE UPDATE ON queue_bookings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data insertion (optional)
-- Insert sample provinces
INSERT INTO provinces (name) VALUES 
    ('กรุงเทพมหานคร'),
    ('เชียงใหม่'),
    ('ขอนแก่น'),
    ('สงขลา')
ON CONFLICT (name) DO NOTHING;

-- Insert sample districts
INSERT INTO districts (name, province_id) VALUES 
    ('เขตบางรัก', 1),
    ('เขตสาทร', 1),
    ('เขตเมือง', 2),
    ('เขตสันทราย', 2),
    ('เขตเมือง', 3),
    ('เขตเมือง', 4)
ON CONFLICT DO NOTHING;

-- Insert sample services
INSERT INTO services (name, district_id) VALUES 
    ('บริการทะเบียน', 1),
    ('บริการประชาสัมพันธ์', 1),
    ('บริการภาษี', 1),
    ('บริการทะเบียน', 2),
    ('บริการภาษี', 2),
    ('บริการทะเบียน', 3),
    ('บริการประชาสัมพันธ์', 3),
    ('บริการทะเบียน', 4),
    ('บริการทะเบียน', 5),
    ('บริการภาษี', 5),
    ('บริการทะเบียน', 6)
ON CONFLICT DO NOTHING;

-- Views for easier querying
CREATE OR REPLACE VIEW service_details AS
SELECT 
    s.id as service_id,
    s.name as service_name,
    d.id as district_id,
    d.name as district_name,
    p.id as province_id,
    p.name as province_name
FROM services s
JOIN districts d ON s.district_id = d.id
JOIN provinces p ON d.province_id = p.id;

CREATE OR REPLACE VIEW document_details AS
SELECT 
    doc.id as document_id,
    doc.content,
    doc.created_at,
    s.id as service_id,
    s.name as service_name,
    d.id as district_id,
    d.name as district_name,
    p.id as province_id,
    p.name as province_name
FROM documents doc
JOIN services s ON doc.service_id = s.id
JOIN districts d ON s.district_id = d.id
JOIN provinces p ON d.province_id = p.id;

CREATE OR REPLACE VIEW queue_details AS
SELECT 
    qb.id as booking_id,
    qb.queue_number,
    qb.citizen_name,
    qb.citizen_phone,
    qb.citizen_email,
    qb.booking_date,
    qb.booking_time,
    qb.status,
    qb.notes,
    qb.created_at,
    qb.updated_at,
    s.id as service_id,
    s.name as service_name,
    d.id as district_id,
    d.name as district_name,
    p.id as province_id,
    p.name as province_name
FROM queue_bookings qb
JOIN services s ON qb.service_id = s.id
JOIN districts d ON s.district_id = d.id
JOIN provinces p ON d.province_id = p.id;

-- Function to generate queue number
CREATE OR REPLACE FUNCTION generate_queue_number(service_id_param INTEGER, booking_date_param DATE)
RETURNS VARCHAR(20) AS $$
DECLARE
    queue_count INTEGER;
    queue_number VARCHAR(20);
BEGIN
    -- Count existing bookings for the same service and date
    SELECT COUNT(*) INTO queue_count
    FROM queue_bookings 
    WHERE service_id = service_id_param 
    AND booking_date = booking_date_param;
    
    -- Generate queue number format: Q{service_id:03d}{MMDD}{count:03d}
    queue_number := 'Q' || 
                   LPAD(service_id_param::TEXT, 3, '0') ||
                   TO_CHAR(booking_date_param, 'MMDD') ||
                   LPAD((queue_count + 1)::TEXT, 3, '0');
    
    RETURN queue_number;
END;
$$ LANGUAGE plpgsql;

-- Function to get service by names
CREATE OR REPLACE FUNCTION get_service_by_names(
    province_name_param VARCHAR(100),
    district_name_param VARCHAR(100),
    service_name_param VARCHAR(100)
)
RETURNS TABLE(
    service_id INTEGER,
    district_id INTEGER,
    province_id INTEGER,
    service_name VARCHAR(100),
    district_name VARCHAR(100),
    province_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id as service_id,
        d.id as district_id,
        p.id as province_id,
        s.name as service_name,
        d.name as district_name,
        p.name as province_name
    FROM services s
    JOIN districts d ON s.district_id = d.id
    JOIN provinces p ON d.province_id = p.id
    WHERE LOWER(p.name) = LOWER(province_name_param)
    AND LOWER(d.name) = LOWER(district_name_param)
    AND LOWER(s.name) = LOWER(service_name_param);
END;
$$ LANGUAGE plpgsql;

-- Function to get queue statistics
CREATE OR REPLACE FUNCTION get_queue_statistics(
    start_date_param DATE DEFAULT NULL,
    end_date_param DATE DEFAULT NULL,
    service_id_param INTEGER DEFAULT NULL
)
RETURNS TABLE(
    total_bookings BIGINT,
    pending_count BIGINT,
    confirmed_count BIGINT,
    completed_count BIGINT,
    cancelled_count BIGINT,
    service_name VARCHAR(100),
    district_name VARCHAR(100),
    province_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_bookings,
        COUNT(CASE WHEN qb.status = 'pending' THEN 1 END) as pending_count,
        COUNT(CASE WHEN qb.status = 'confirmed' THEN 1 END) as confirmed_count,
        COUNT(CASE WHEN qb.status = 'completed' THEN 1 END) as completed_count,
        COUNT(CASE WHEN qb.status = 'cancelled' THEN 1 END) as cancelled_count,
        s.name as service_name,
        d.name as district_name,
        p.name as province_name
    FROM queue_bookings qb
    JOIN services s ON qb.service_id = s.id
    JOIN districts d ON s.district_id = d.id
    JOIN provinces p ON d.province_id = p.id
    WHERE (start_date_param IS NULL OR qb.booking_date >= start_date_param)
    AND (end_date_param IS NULL OR qb.booking_date <= end_date_param)
    AND (service_id_param IS NULL OR qb.service_id = service_id_param)
    GROUP BY s.id, s.name, d.name, p.name;
END;
$$ LANGUAGE plpgsql;