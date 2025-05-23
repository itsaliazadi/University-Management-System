import os
import database
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

app.secret_key = os.urandom(24)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('ID').strip()
        password = request.form.get('password')
        role = request.form.get('role')

        if role == "admin":
            if user_id == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['ID'] = user_id
                session['role'] = 'admin'
                session['name'] = 'Administrator'
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password'
                return render_template('login.html', error=error)
        else:
            user = database.fetch_user(user_id, role)
            if user and password == str(user["password"]):
                session['ID'] = user_id
                session['role'] = role
                session['name'] = user["name"]
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password'
                return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'ID' not in session:
        return redirect(url_for('login'))

    user_id = session['ID']
    name = session['name']
    role = session['role']

    if role == 'student':
        courses = database.fetch_student_courses(user_id)
        return render_template('student_dashboard.html', user=name, role=role, courses=courses)
    elif role == 'instructor':
        courses = database.fetch_instructor_courses(user_id)
        return render_template('instructor_dashboard.html', user=name, role=role, courses=courses)
    elif role == 'admin':
        students = database.fetch_all_students()
        instructors = database.fetch_all_instructors()
        return render_template('admin_dashboard.html', user=name, role=role, students=students, instructors=instructors)

@app.route('/course/<course_id>/students')
def course_students(course_id):
    if 'ID' not in session or session['role'] != 'instructor':
        return redirect(url_for('login'))

    students = database.fetch_course_students(course_id)
    return render_template('course_students.html', course_id=course_id, students=students)

@app.route('/course/<course_id>/update_grades', methods=['POST'])
def update_grades(course_id):
    students = database.fetch_course_students(course_id)
    student_ids = [student['ID'] for student in students]

    for student_id in student_ids:
        grade_key = f'grade_{student_id}'
        new_grade = request.form.get(grade_key)
        if new_grade:
            database.update_grades(student_id, course_id, new_grade)

    return redirect(url_for('course_students', course_id=course_id))

@app.route('/delete_user/<role>/<ID>')
def delete_user(role, ID):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    database.delete_user(ID, role)
    return redirect(url_for('dashboard'))

@app.route('/edit_user/<role>/<ID>', methods=['GET', 'POST'])
def edit_user(role, ID):
    if 'ID' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name').strip()
        dept_name = request.form.get('dept_name').strip()
        extra_field = request.form.get('extra_field')
        password = request.form.get('password', '').strip()

        if not password:
            user = database.fetch_user(ID, role)
            if not user:
                return "User not found", 404
            password = user["password"]

        database.update_user(role, ID, name, dept_name, extra_field, password)
        return redirect(url_for('dashboard'))

    user = database.fetch_user(ID, role)
    if not user:
        return "User not found", 404

    return render_template('edit_user.html', user=user, role=role)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'ID' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        role = request.form.get('role')
        user_id = request.form.get('ID').strip()
        name = request.form.get('name').strip()
        dept_name = request.form.get('dept_name').strip()
        extra_field = request.form.get('extra_field')
        password = request.form.get('password').strip()

        if not all([user_id, name, dept_name, password]):
            error = 'All fields except extra field are required'
            return render_template('add_user.html', error=error)

        try:
            database.add_user(role, user_id, name, dept_name, extra_field, password)
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = f'Error adding user: {str(e)}'
            return render_template('add_user.html', error=error)

    return render_template('add_user.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
