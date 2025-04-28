from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for sessions

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('hw13.db')
    conn.row_factory = sqlite3.Row  # Makes results behave like dictionaries
    return conn

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): # Checks user logged in status
        return redirect('/login')

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    conn.close()

    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect('/login')

    error = None
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not first_name or not last_name:
            error = 'All fields are required.'
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)',
                         (first_name, last_name))
            conn.commit()
            conn.close()
            return redirect('/dashboard')

    return render_template('add_student.html', error=error)

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect('/login')

    error = None
    if request.method == 'POST':
        subject = request.form.get('subject')
        num_questions = request.form.get('num_questions')
        quiz_date = request.form.get('quiz_date')

        if not subject or not num_questions or not quiz_date:
            error = 'All fields are required.'
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)',
                         (subject, num_questions, quiz_date))
            conn.commit()
            conn.close()
            return redirect('/dashboard')

    return render_template('add_quiz.html', error=error)

@app.route('/student/<int:student_id>')
def view_student(student_id):
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    #results = conn.execute('SELECT * FROM results WHERE student_id = ? ORDER BY quiz_id', (student_id,)).fetchall()

    # Attempting the Optional Tasks
    results = conn.execute('''
        SELECT results.result_id, quizzes.subject, quizzes.quiz_date, results.score
        FROM results
        JOIN quizzes ON results.quiz_id = quizzes.id
        WHERE results.student_id = ?
        ORDER BY quizzes.quiz_date
    ''', (student_id,)).fetchall()

    conn.close()

    return render_template('student_results.html', student=student, results=results)

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()

    error = None
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        quiz_id = request.form.get('quiz_id')
        score = request.form.get('score')

        if not student_id or not quiz_id or not score:
            error = 'All fields are required.'
        else:
            conn.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)',
                         (student_id, quiz_id, score))
            conn.commit()
            conn.close()
            return redirect('/dashboard')

    conn.close()
    return render_template('add_result.html', students=students, quizzes=quizzes, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# Optional Delete Features

@app.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/quiz/delete/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    conn.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/result/delete/<int:result_id>/<int:student_id>', methods=['POST'])
def delete_result(result_id, student_id):
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    conn.execute('DELETE FROM results WHERE result_id = ?', (result_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_student', student_id=student_id))



if __name__ == '__main__':
    app.run(debug=True)
