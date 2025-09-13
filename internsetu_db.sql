
CREATE DATABASE IF NOT EXISTS internsetu_db
CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;
USE internsetu_db;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,   
    cgpa DECIMAL(3,2) NOT NULL,
    college_name VARCHAR(200),
    location VARCHAR(100),
    field VARCHAR(100),                      
    skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (CHAR_LENGTH(hashed_password) >= 60)
);


CREATE TABLE IF NOT EXISTS internships (
    internship_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    suggested_role VARCHAR(200) NOT NULL,
    location VARCHAR(100),
    mode ENUM('Remote','Onsite') NOT NULL DEFAULT 'Remote',
    min_cgpa DECIMAL(3,2) NOT NULL,
    field VARCHAR(100) NOT NULL,
    program VARCHAR(100) DEFAULT 'PM Internship',
    description TEXT,
    apply_link VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    rec_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    reason VARCHAR(255),
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON DELETE CASCADE,
    UNIQUE (student_id, internship_id)
);

-- ===========================================
-- ADMINS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (CHAR_LENGTH(hashed_password) >= 60)
);

-- ===========================================
-- LOGIN LOGS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS login_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    email VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    logged_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (student_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL
);

-- ===========================================
-- INDEXES
-- ===========================================
DROP INDEX idx_students_field_location ON students;

DROP INDEX idx_internships_field_location ON internships;

DROP INDEX idx_internships_min_cgpa ON internships;

CREATE INDEX idx_students_field_location ON students(field, location);
CREATE INDEX idx_internships_field_location ON internships(field, location);
CREATE INDEX idx_internships_min_cgpa ON internships(min_cgpa);

-- ===========================================
-- TRIGGER: auto-generate recommendations
-- ===========================================
DROP TRIGGER IF EXISTS trg_after_student_insert;
DELIMITER $$
CREATE TRIGGER trg_after_student_insert
AFTER INSERT ON students
FOR EACH ROW
BEGIN
    INSERT IGNORE INTO recommendations (student_id, internship_id, reason)
    SELECT NEW.student_id, i.internship_id,
           CONCAT('Matches field "', i.field, '" | min CGPA ', i.min_cgpa, ' | ', i.mode, ' in ', COALESCE(i.location,'Any'))
    FROM internships i
    WHERE
      (LOWER(i.field) = LOWER(NEW.field)
        OR LOWER(NEW.field) LIKE CONCAT('%', LOWER(i.field), '%')
        OR LOWER(i.field) LIKE CONCAT('%', LOWER(NEW.field), '%'))
      AND NEW.cgpa >= i.min_cgpa
      AND (i.mode = 'Remote'
           OR i.location IS NULL
           OR LOWER(i.location) = LOWER(NEW.location));
END$$
DELIMITER ;

-- ===========================================
-- VIEWS
-- ===========================================
CREATE OR REPLACE VIEW student_recommendations AS
SELECT r.rec_id,
       r.student_id,
       s.name AS student_name,
       s.email AS student_email,
       i.internship_id,
       i.company_name,
       i.suggested_role,
       i.location AS internship_location,
       i.mode AS internship_mode,
       i.min_cgpa,
       r.reason,
       r.recommended_at
FROM recommendations r
JOIN students s ON s.student_id = r.student_id
JOIN internships i ON i.internship_id = r.internship_id;

CREATE OR REPLACE VIEW admin_students_overview AS
SELECT s.student_id, s.name, s.email, s.cgpa, s.college_name, s.location, s.field, s.skills,
       (SELECT COUNT(*) FROM recommendations r WHERE r.student_id = s.student_id) AS recommendations_count
FROM students s;

-- ===========================================
-- SAMPLE DATA RESET (safe for re-runs)
-- ===========================================
TRUNCATE TABLE recommendations;
TRUNCATE TABLE students;
TRUNCATE TABLE internships;

-- ===========================================
-- SAMPLE DATA: internships
-- ===========================================
INSERT INTO internships (company_name, suggested_role, location, mode, min_cgpa, field, description, apply_link) VALUES
('PM Internship Cell','Software Intern','Mumbai','Onsite',7.00,'B.Tech','Work on gov tech projects','https://pm.gov.in/apply/1'),
('PM Internship Cell','Data Science Intern','Mumbai','Remote',7.50,'B.Tech','Data analysis for civic datasets','https://pm.gov.in/apply/2'),
('Skill India Initiative','Web Development Intern','Chennai','Remote',6.50,'BCA','Frontend and backend tasks','https://skillindia.gov/apply/3'),
('Digital India Fellows','Product Intern','Delhi','Onsite',8.00,'MBA','Product research & roadmap','https://digitalindia.gov/apply/4'),
('Smart Cities Mission','Urban Data Intern','Bengaluru','Remote',7.50,'M.Tech','Work on urban datasets','https://smartcities.gov/apply/5'),
('Startup India Hub','UI/UX Intern','Ahmedabad','Onsite',7.00,'B.Des','Design public-facing UIs','https://startupindia.gov/apply/6'),
('Make in India Secretariat','Cybersecurity Intern','Hyderabad','Remote',8.20,'B.Tech','Security audits and tooling','https://makeinindia.gov/apply/7'),
('NITI Aayog Partner Org','Finance Intern','Delhi','Onsite',7.80,'MBA','Financial modelling','https://niti.gov.in/apply/8'),
('MyGov Internship Program','Content Intern','Kolkata','Remote',6.90,'BA','Content creation for digital campaigns','https://mygov.in/apply/9'),
('Skill India Initiative','Accounts Intern','Surat','Onsite',7.20,'B.Com','Handle accounts and Tally','https://skillindia.gov/apply/10'),
('PM Internship Cell','DevOps Intern','Pune','Remote',7.50,'B.Tech','Maintain CI/CD pipelines','https://pm.gov.in/apply/11'),
('Digital India Fellows','Research Intern','Hyderabad','Remote',6.80,'M.Tech','Research on GovTech topics','https://digitalindia.gov/apply/12'),
('PM Internship Cell','Product Management Intern','Mumbai','Onsite',8.00,'MBA','PM support for digital services','https://pm.gov.in/apply/13'),
('Startup India Hub','Graphic Design Intern','Chennai','Remote',6.70,'B.Des','Create design assets','https://startupindia.gov/apply/14'),
('Make in India Secretariat','ML Intern','Bengaluru','Remote',8.00,'M.Tech','ML model development','https://makeinindia.gov/apply/15'),
('MyGov Internship Program','Community Manager Intern','Delhi','Onsite',6.50,'BA','Moderate and manage online community','https://mygov.in/apply/16'),
('Smart Cities Mission','GIS Intern','Ahmedabad','Onsite',7.10,'B.Tech','GIS mapping for projects','https://smartcities.gov/apply/17'),
('NITI Aayog Partner Org','Operations Intern','Pune','Onsite',7.00,'MBA','Operations support','https://niti.gov.in/apply/18'),
('PM Internship Cell','QA Intern','Mumbai','Remote',6.80,'BCA','Testing and automation','https://pm.gov.in/apply/19'),
('Digital India Fellows','NLP Intern','Bengaluru','Remote',8.10,'M.Tech','NLP research','https://digitalindia.gov/apply/20');

-- ===========================================
-- SAMPLE DATA: students
-- ===========================================
INSERT IGNORE INTO students (name, email, hashed_password, cgpa, college_name, location, field, skills) VALUES
('Aarav Sharma','aarav.sharma@example.com','$2y$12$examplehash......................',8.20,'IIT Bombay','Mumbai','B.Tech','C++, Java, SQL'),
('Isha Patel','isha.patel@example.com','$2y$12$examplehash......................',7.50,'NIT Trichy','Chennai','BCA','HTML, CSS, Python'),
('Rohan Mehta','rohan.mehta@example.com','$2y$12$examplehash......................',9.10,'BITS Pilani','Hyderabad','MBA','Finance, Excel, Operations'),
('Priya Nair','priya.nair@example.com','$2y$12$examplehash......................',7.90,'IIT Delhi','Delhi','B.Tech','Python, DSA, SQL'),
('Karan Singh','karan.singh@example.com','$2y$12$examplehash......................',6.80,'VIT Vellore','Pune','BCA','JavaScript, MySQL, PHP');

-- ===========================================
-- DATABASE USER
-- ===========================================
CREATE USER IF NOT EXISTS 'internsetu_user'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON internsetu_db.* TO 'internsetu_user'@'localhost';
FLUSH PRIVILEGES;

-- ===========================================
-- SAMPLE QUERY
-- ===========================================
SELECT i.internship_id, i.company_name, i.suggested_role,
       i.location, i.mode, i.min_cgpa, i.description, i.apply_link
FROM internships i
JOIN students s ON (
      LOWER(i.field) = LOWER(s.field)
      OR LOWER(s.field) LIKE CONCAT('%', LOWER(i.field), '%')
      OR LOWER(i.field) LIKE CONCAT('%', LOWER(s.field), '%')
)
WHERE s.student_id = 1
  AND s.cgpa >= i.min_cgpa
  AND (i.mode = 'Remote' OR i.location IS NULL OR LOWER(i.location) = LOWER(s.location))
ORDER BY i.min_cgpa ASC, i.mode DESC;

-- ===== End of script =====
 