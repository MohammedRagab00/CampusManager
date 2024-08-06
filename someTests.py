import sqlite3


conn = sqlite3.connect('database.db')
print("Connected to database successfully")

cursor = conn.cursor()

cursor.execute('''
delete from registerdCourses
''')
cursor.execute('''
update course_grade 
set grade = 3
where std_id =1 and cc = "CS101";
''')


conn.commit()
conn.close()