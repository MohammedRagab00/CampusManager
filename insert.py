import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
print("Connected to database successfully")

# Create a cursor object
cursor = conn.cursor()

cursor.execute("INSERT INTO student (std_id, first_name, middle_name, last_name, email, dob, Sph, password, major, passed_credit_hour, GPA) VALUES (3, 'John', 'A', 'Doe', 'john.doe@example.com', '1995-01-01', '123-456-7890', 'password123', 'Computer Science', '120',  NULL);")
cursor.execute("INSERT INTO student (std_id, first_name, middle_name, last_name, email, dob, Sph, password, major, passed_credit_hour, GPA) VALUES (4, 'Jane', 'B', 'Smith', 'jane.smith@example.com', '1996-02-02', '123-456-7891', 'password456', 'Mathematics', '110',  NULL);")

cursor.execute("INSERT INTO grade (std_id, semester, semester_grade) VALUES (1, 'Fall 2023', '3.14');")
cursor.execute("INSERT INTO grade (std_id, semester, semester_grade) VALUES (2, 'Fall 2023', '4');")

cursor.execute("INSERT INTO holds (std_id, date, price) VALUES (1, '2024-01-01', 100);")
cursor.execute("INSERT INTO holds (std_id, date, price) VALUES (2, '2024-01-02', 150);")

cursor.execute("INSERT INTO Department (Did, head_id, Dname) VALUES (1, 1, 'Computer Science');")
cursor.execute("INSERT INTO Department (Did, head_id, Dname) VALUES (2, 2, 'Mathematics');")

cursor.execute("INSERT INTO course (cc, Cname, credit_hours, Did) VALUES ('CS102', 'porg2', '4', 2);")
cursor.execute("INSERT INTO course (cc, Cname, credit_hours, Did) VALUES ('MATH102', 'Calculus II', '4', 2);")
cursor.execute("INSERT INTO course (cc, Cname, credit_hours, Did) VALUES ('MATH101', 'Calculus I', '3', 2);")
cursor.execute("INSERT INTO course (cc, Cname, credit_hours, Did) VALUES ('CS101', 'Intro to CS', '3', 1);")


cursor.execute("INSERT INTO place (place_num, building, Did) VALUES ('101', 'Engineering Hall', 1);")
cursor.execute("INSERT INTO place (place_num, building, Did) VALUES ('102', 'Science Hall', 2);")

cursor.execute("INSERT INTO instructor (ins_id, fName, lName, email, number, Did, password) VALUES (1, 'Alice', 'Brown', 'alice.brown@example.com', '123-456-7892', 1, 'pass789');")
cursor.execute("INSERT INTO instructor (ins_id, fName, lName, email, number, Did, password) VALUES (2, 'Bob', 'White', 'bob.white@example.com', '123-456-7893', 2, 'pass987');")

cursor.execute("INSERT INTO course_grade (semester, cc, std_id, grade) VALUES ('Fall 2023', 'CS101', 1 , 4);")
cursor.execute("INSERT INTO course_grade (semester, cc, std_id, grade) VALUES ('Fall 2023', 'MATH101', 1, 2.4);")
cursor.execute("INSERT INTO course_grade (semester, cc, std_id ,grade) VALUES ('Fall 2023', 'CS101', 2 , 3.7);")
cursor.execute("INSERT INTO course_grade (semester, cc, std_id ,grade) VALUES ('Fall 2023', 'MATH101', 2 , 3.3);")

cursor.execute("INSERT INTO section (sec_id, cc, place_num, semester, type, days, time, groups_code) VALUES (1, 'CS101', '101', 'Fall 2023', 'Lecture', 'MWF', '10:00-11:00', 'A');")
cursor.execute("INSERT INTO section (sec_id, cc, place_num, semester, type, days, time, groups_code) VALUES (2, 'MATH101', '102', 'Fall 2023', 'Lecture', 'TTh', '14:00-15:30', 'B');")

cursor.execute("INSERT INTO pre_req (cc, precc) VALUES ('MATH102', 'MATH101');")
cursor.execute("INSERT INTO pre_req (cc, precc) VALUES ('CS102', 'CS101');")

cursor.execute("INSERT INTO register (rid, std_id, cc) VALUES (1, 1, 'CS102');")
cursor.execute("INSERT INTO register (rid, std_id, cc) VALUES (2, 2, 'CS102');")
cursor.execute("INSERT INTO register (rid, std_id, cc) VALUES (3, 1, 'MATH102');")
cursor.execute("INSERT INTO register (rid, std_id, cc) VALUES (4, 2, 'MATH102');")

print("Values inserted successfully!")

# Commit the changes
conn.commit()

# Close the connection
conn.close()
