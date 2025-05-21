import os
import mysql.connector

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

def connect_mysql():
    return mysql.connector.connect(
        host='localhost',
        user=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        database='university'
    )



def fetch_user(ID, role):

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM {role} WHERE ID = %s"
    cursor.execute(query, (ID,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return user



def fetch_student_courses(ID):

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT title, course.dept_name, course.credits, takes.grade FROM student JOIN takes ON student.ID = takes.ID join course ON takes.course_id = course.course_id WHERE student.ID = %s;"

    cursor.execute(query, (ID,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    return courses



def fetch_instructor_courses(ID):

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT course.course_id, title, course.dept_name, course.credits FROM instructor join teaches ON instructor.ID = teaches.ID join course ON teaches.course_id = course.course_id WHERE instructor.ID = %s;"

    cursor.execute(query, (ID,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    print(courses)

    return courses



def fetch_course_students(course_id):

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT student.ID, name, takes.grade FROM student join takes ON student.ID = takes.ID join course ON takes.course_id = course.course_id WHERE course.course_id = %s;"

    cursor.execute(query, (course_id,))
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return students



def update_grades(ID, course_id, new_grade):

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)

    query = "UPDATE takes SET grade = %s WHERE ID = %s AND course_id = %s"

    cursor.execute(query, (new_grade, ID, course_id))
    conn.commit()
    cursor.close()
    conn.close()



def fetch_all_students():

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM student"
    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    conn.close()
    return students


def fetch_all_instructors():

    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM instructor"
    cursor.execute(query)
    instructors = cursor.fetchall()

    cursor.close()
    conn.close()
    return instructors



def delete_user(ID, role):

    conn = connect_mysql()
    cursor = conn.cursor()

    query = f"DELETE FROM {role} WHERE ID = %s"
    cursor.execute(query, (ID,))
    conn.commit()

    cursor.close()
    conn.close()



def update_user(role, ID, name, dept_name, extra_field, password):
    
    conn = connect_mysql()
    cursor = conn.cursor()

    if role == "student":
        cursor.execute("""
            UPDATE student 
            SET name=%s, dept_name=%s, tot_cred=%s, password=%s 
            WHERE ID=%s
        """, (name, dept_name, extra_field, password, ID))

    elif role == "instructor":
        cursor.execute("""
            UPDATE instructor 
            SET name=%s, dept_name=%s, salary=%s, password=%s 
            WHERE ID=%s
        """, (name, dept_name, extra_field, password, ID))

    conn.commit()
    cursor.close()
    conn.close()
