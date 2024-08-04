import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')
print("Connected to database successfully")

# Create a cursor object
cursor = conn.cursor()


# Create new tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS student(
    std_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(50),
    dob DATE,
    Sph VARCHAR(14),
    password VARCHAR(50),
    major VARCHAR(50),
    passed_credit_hour VARCHAR(10),
    GPA INT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS grade(
    std_id INT,
    semester VARCHAR(50),
    semester_grade VARCHAR(50),
    FOREIGN KEY (std_id) REFERENCES student(std_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS holds(
    std_id INT,
    date DATE,
    price INT,
    FOREIGN KEY (std_id) REFERENCES student(std_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Department(
    Did INT PRIMARY KEY,
    head_id INT,
    Dname VARCHAR(40)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS course(
    cc VARCHAR(10) PRIMARY KEY,
    Cname VARCHAR(10),
    credit_hours VARCHAR(10),
    Did INT,
    FOREIGN KEY (Did) REFERENCES Department(Did)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS place(
    place_num VARCHAR(30) PRIMARY KEY,
    building VARCHAR(30),
    Did INT,
    FOREIGN KEY (Did) REFERENCES Department(Did)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS instructor(
    ins_id INT PRIMARY KEY,
    fName VARCHAR(30),
    lName VARCHAR(30),
    email VARCHAR(30),
    number VARCHAR(30),
    Did INT,
    password VARCHAR(30),
    FOREIGN KEY (Did) REFERENCES Department(Did)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS course_grade(
    semester VARCHAR(30),
    cc VARCHAR(10),
    std_id INT,
    grade VARCHAR(10),
    FOREIGN KEY (cc) REFERENCES course(cc),
    FOREIGN KEY (std_id) REFERENCES student(std_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS section(
    sec_id INT PRIMARY KEY,
    cc VARCHAR(10),
    place_num VARCHAR(30),
    semester VARCHAR(30),
    type VARCHAR(30),
    days VARCHAR(30),
    time VARCHAR(30),
    groups_code VARCHAR(30),
    FOREIGN KEY (cc) REFERENCES course(cc),
    FOREIGN KEY (place_num) REFERENCES place(place_num)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pre_req(
    cc VARCHAR(10),
    precc VARCHAR(10),
    FOREIGN KEY (cc) REFERENCES course(cc),
    FOREIGN KEY (precc) REFERENCES course(cc)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS register(
    rid INT PRIMARY KEY,
    std_id INT,
    cc VARCHAR(10),
    FOREIGN KEY (std_id) REFERENCES student(std_id),
    FOREIGN KEY (cc) REFERENCES course(cc)
);
''')

print("Tables created successfully!")

# Close the connection
conn.commit()
conn.close()
