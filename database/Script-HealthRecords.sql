CREATE TABLE health_records (
    health_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    attendance_status VARCHAR(10) NOT NULL,
    record_date DATE NOT NULL,
    body_temperature VARCHAR(10),
    nails_status BOOLEAN,
    hair_status BOOLEAN,
    teeth_status BOOLEAN,
    body_status BOOLEAN,
    eye_status BOOLEAN,
    ear_status BOOLEAN,
    nose_status BOOLEAN,
    student_photo VARCHAR(255), -- เก็บ Path/URL ของรูปภาพ
    notes TEXT,
    classroom_id INT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NOT NULL,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id), -- ต้องมีตาราง 'students' อยู่แล้ว
        
    CONSTRAINT fk_classroom
        FOREIGN KEY (classroom_id)
        REFERENCES classrooms(classroom_id), -- ต้องมีตาราง 'classrooms' อยู่แล้ว
        
    CONSTRAINT fk_healthrecords_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(user_id), -- ต้องมีตาราง 'users' อยู่แล้ว
        
    CONSTRAINT fk_healthrecords_updated_by
        FOREIGN KEY (updated_by)
        REFERENCES users(user_id) -- ต้องมีตาราง 'users' อยู่แล้ว
)


CREATE TABLE class_history (
    class_history_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    classroom_id INT NOT NULL,
    academic_year_id INT NOT NULL,
    
    -- เพื่อให้แน่ใจว่านักเรียนคนหนึ่งอยู่ในห้องเดียวต่อหนึ่งปีการศึกษา (ถ้าเป็นไปตามเงื่อนไขนี้)
    UNIQUE (student_id, academic_year_id), 
    
    CONSTRAINT fk_classhistory_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id),
        
    CONSTRAINT fk_classhistory_classroom
        FOREIGN KEY (classroom_id)
        REFERENCES classrooms(classroom_id),
        
    CONSTRAINT fk_classhistory_academic_year
        FOREIGN KEY (academic_year_id)
        REFERENCES academic_years(academic_year_id)
);

-- INSERT INTO `students` VALUES (1,'0000000000000','0000','เด็กหญิง','รุ่งนภา','เด่นหล้า','รุ่ง','หญิง','2019-07-23','5 ปี 11 เดือน','0000','10 พระบรมมหาราชวัง พระนคร กรุงเทพมหานคร 10200','144/4 บ้านโกทา ในเมือง เมืองขอนแก่น ขอนแก่น 40000',13.70539822,100.59518588,1,'student_1111.jpg',NULL,'A','2025-07-17 17:15:36',1,'2025-07-17 17:40:31',1);
-- INSERT INTO `students` VALUES (2,'0000000000001','0001','เด็กชาย','กร','เด่นภัย','กร','ชาย','2019-07-23','5 ปี 11 เดือน','0001','10 พระบรมมหาราชวัง พระนคร กรุงเทพมหานคร 10200','144/4 บ้านโกทา ในเมือง เมืองขอนแก่น ขอนแก่น 40000',13.70539822,100.59518588,1,'student_1111.jpg',NULL,'A','2025-07-17 17:15:36',1,'2025-07-17 17:40:31',1);
-- INSERT INTO `students` VALUES (3,'0000000000002','0002','เด็กชาย','พิรัชต์','เด่นดี','รัช','ชาย','2019-07-23','5 ปี 11 เดือน','0002','10 พระบรมมหาราชวัง พระนคร กรุงเทพมหานคร 10200','144/4 บ้านโกทา ในเมือง เมืองขอนแก่น ขอนแก่น 40000',13.70539822,100.59518588,1,'student_1111.jpg',NULL,'A','2025-07-17 17:15:36',1,'2025-07-17 17:40:31',1);
-- INSERT INTO `students` VALUES (4,'0000000000003','0003','เด็กหญิง','ลิซ่า','เด่นจัง','ลิลลี่','หญิง','2019-07-23','5 ปี 11 เดือน','0003','10 พระบรมมหาราชวัง พระนคร กรุงเทพมหานคร 10200','144/4 บ้านโกทา ในเมือง เมืองขอนแก่น ขอนแก่น 40000',13.70539822,100.59518588,1,'student_1111.jpg',NULL,'A','2025-07-17 17:15:36',1,'2025-07-17 17:40:31',1);


-- INSERT INTO class_history (
--     student_id,
--     classroom_id,
--     academic_year_id
-- ) VALUES
--     (1, 9, 13),  -- รุ่งนภา อนุบาล 1/1 ปีการศึกษา 2568
--     (2, 9, 13),  -- กร อนุบาล 1/1 ปีการศึกษา 2568
--     (3, 9, 13),  -- พิรัชต์ อนุบาล 1/1 ปีการศึกษา 2568
--     (4, 9, 13),  -- ลิซ่า อนุบาล 1/1 ปีการศึกษา 2568
--     (46, 12, 13); -- เรียนดี อนุบาล 1/2 ปีการศึกษา 2568


-- INSERT INTO health_records
-- (student_id, attendance_status, record_date, body_temperature, nails_status, hair_status, teeth_status, body_status, eye_status, ear_status, nose_status, student_photo, notes, classroom_id, created_date, created_by, updated_date, updated_by)
-- VALUES(1, 'present', CURDATE(), '36.5', true, true, true, false, true, false, true, 'student_1111.jpg', NULL, 9, current_timestamp(), 1, current_timestamp(), 1);