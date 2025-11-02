from flask import Flask, render_template, request, g
import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# ------------------------------
# ENVIRONMENT VARIABLES
# ------------------------------
load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASS", ""),
    'database': os.getenv("DB_NAME", "internsetu_db")
}

# ------------------------------
# FLASK APP
# ------------------------------
app = Flask(__name__, template_folder='frontend', static_folder='frontend/assets')

# ------------------------------
# BACKEND + MODEL
# ------------------------------
sys.path.append(os.path.abspath('backend'))
sys.path.append(os.path.abspath('.'))

import model  # model.py must have companies, best_model, recommend_for_new_student, le_dept

# ------------------------------
# DATABASE CONNECTION HELPERS
# ------------------------------
def get_db_connection():
    if 'db_conn' not in g:
        try:
            g.db_conn = mysql.connector.connect(**DB_CONFIG)
            g.db_cursor = g.db_conn.cursor(dictionary=True)
        except Error as e:
            print(f"Database connection error: {e}")
            g.db_conn, g.db_cursor = None, None
    return g.db_conn, g.db_cursor

@app.teardown_appcontext
def close_db(exception):
    db_conn = g.pop('db_conn', None)
    db_cursor = g.pop('db_cursor', None)
    if db_cursor:
        db_cursor.close()
    if db_conn and db_conn.is_connected():
        db_conn.close()
        print("MySQL connection closed.")

# ------------------------------
# ROUTES
# ------------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/students')
def students():
    conn, cursor = get_db_connection()
    if not conn or not cursor:
        return "Database connection not established."
    try:
        cursor.execute("SELECT student_id, name, email, cgpa, college_name, location, field, skills FROM students;")
        students_list = cursor.fetchall()
        return render_template('students.html', students=students_list)
    except Error as e:
        return f"Error fetching students: {e}"

@app.route('/internships')
def internships():
    conn, cursor = get_db_connection()
    if not conn or not cursor:
        return "Database connection not established."
    try:
        cursor.execute("SELECT internship_id, company_name, suggested_role, location, mode, min_cgpa, field, description, apply_link FROM internships;")
        internships_list = cursor.fetchall()
        return render_template('internships.html', internships=internships_list)
    except Error as e:
        return f"Error fetching internships: {e}"

@app.route('/recommendations/<int:student_id>')
def recommendations(student_id):
    conn, cursor = get_db_connection()
    if not conn or not cursor:
        return "Database connection not established."
    try:
        cursor.execute("""
            SELECT r.rec_id, i.company_name, i.suggested_role, i.location, i.mode, i.min_cgpa, i.description, i.apply_link, r.reason, r.recommended_at
            FROM recommendations r
            JOIN internships i ON i.internship_id = r.internship_id
            WHERE r.student_id = %s
            ORDER BY r.recommended_at DESC
        """, (student_id,))
        recs = cursor.fetchall()
        return render_template('recommendations.html', recommendations=recs)
    except Error as e:
        return f"Error fetching recommendations: {e}"

@app.route('/profile')
def profile():
    return render_template('profile.html', recommendations=[], student={})

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        try:
            # Collect form data
            department = request.form.get('department')
            cgpa = float(request.form.get('cgpa', 0))
            projects = int(request.form.get('projects', 0))
            skills = request.form.get('skills')

            # Student profile
            new_student = {
                "department": department,
                "cgpa": cgpa,
                "projects": projects,
                "skills": skills
            }

            # Call ML model (pass le_dept)
            recommended_companies = model.recommend_for_new_student(
                new_student, model.companies, model.best_model, model.le_dept
            )

            return render_template(
                'profile.html',
                recommendations=recommended_companies,
                student=new_student
            )

        except Exception as e:
            return f"Error in recommendation: {e}", 500

    return render_template('application.html')

@app.route('/dbtest')
def dbtest():
    conn, cursor = get_db_connection()
    if not conn or not cursor:
        return "Database connection not established."
    try:
        cursor.execute("SELECT * FROM students LIMIT 10;")
        results = cursor.fetchall()
        return f"<pre>{results}</pre>"
    except Error as e:
        return f"Error executing query: {e}"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('sign_up.html')

@app.route('/alhome')
def alhome():
    return render_template('alhome.html')

@app.route('/alprofile')
def alprofile():
    return render_template('alprofile.html')

@app.route('/application')
def application():
    # Example data (replace with database query results)
    applications = [
        {"role": "Web Development Intern", "company": "Growify", "status": "Applied"},
        {"role": "Backend Developer Intern", "company": "URJA", "status": "In Review"},
        {"role": "Business Analyst Intern", "company": "TechDome", "status": "Selected"},
    ]
    return render_template('application.html', applications=applications)

# ------------------------------
# MAIN ENTRY
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
