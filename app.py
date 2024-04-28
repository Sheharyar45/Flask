from datetime import datetime, timedelta
from flask import Flask,jsonify, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text # textual queries
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'


app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)




class Person(db.Model):
    __tablename__ = 'Person'
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), primary_key=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    type = db.Column(db.String(20), nullable = False)

    def __repr__(self):
        return f"Person('{self.username}','{self.email}')"

class RemarkRequest(db.Model):
    __tablename__ = 'Remarks'
    student = db.Column(db.String(200), primary_key=True)
    test_type = db.Column(db.String(100), primary_key=True)
    reason = db.Column(db.String(200))

    def __init__(self, student, test_type, reason):
        self.student = student
        self.test_type = test_type
        self.reason = reason

class Grades(db.Model):
    __tablename__ = 'Grades'
    username = db.Column(db.String(100), nullable=False, primary_key=True)
    A1 = db.Column(db.Numeric, nullable=True)
    A2 = db.Column(db.Numeric, nullable=True)
    A3 = db.Column(db.Numeric, nullable=True)
    tutorials = db.Column(db.Numeric, nullable=True)
    midterm = db.Column(db.Numeric, nullable=True)
    exam = db.Column(db.Numeric, nullable=True)
    final = db.Column(db.Numeric, nullable=True)

    def __init__(self, username, A1, A2, A3, tutorials, midterm, exam, final):
        self.username = username
        self.A1 = A1
        self.A2 = A2
        self.A3 = A3
        self.tutorials = tutorials
        self.midterm = midterm
        self.exam = exam
        self.final = final

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    instructor = db.Column(db.String(200), primary_key=True)
    student = db.Column(db.String(100), primary_key=True)
    feedback = db.Column(db.String(10000))

    def __init__(self, instructor, student, feedback):
        self.instructor = instructor
        self.student = student
        self.feedback = feedback


with app.app_context():
    db.create_all()


def add_student_to_grades(username, A1=None, A2=None, A3=None, tutorials=None, midterm=None,exam=None, final=None):
    student = Grades(username, A1, A2, A3, tutorials, midterm,exam, final)
    db.session.add(student)
    db.session.commit()


def home():
    if 'name' in session and session['name'][1] == 'Student':
        flash('already logged in!!')
        return redirect(url_for('student', name = session['name'][0]))
    if 'name' in session and session['name'][1] == 'Instructor':
        flash('already logged in!!')
        return redirect(url_for('instructor', name = session['name'][0]))
    else:
        return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['Name']
        username = request.form['Username']
        email = request.form['Email']
        type = request.form['Type']
        password = request.form['Password']
        if not username or not name or not email or not type or not password:
            flash('Please fill in all fields.')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        reg_details =(
            username,
            name,
            email,
            type,
            hashed_password
        )
        existing_user = Person.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already in use!')
            return redirect(url_for('register'))
        existing_user = Person.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already in use!')
            return redirect(url_for('register'))

        add_users(reg_details)
        if type == 'student':
            add_student_to_grades(username)
        flash('Registration Successful! Please login now:')
        return redirect(url_for('login'))
    
@app.route('/')   
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
            return redirect(url_for('student', name = session['name'][0]))
        return render_template('login.html')
    else:
        username = request.form['Username']
        password = request.form['Password']
        person = Person.query.filter_by(username = username).first()
        if not person or not bcrypt.check_password_hash(person.password, password):
            flash('Please check your login details and try again', 'error')
            return render_template('login.html')
        else:
            name = person.name
            session['name'] = [name, person.type,person.username]
            session.permanent = True
            if person.type == 'student':
                return redirect(url_for('student', name = name))
            return redirect(url_for('student', name = name))
        
@app.route('/<name>/CSCB20', methods = ['GET', 'POST'])
def student(name):
    if 'name' in session and session['name'][1] == "student" :
        return render_template('index.html')
    if 'name' in session and session['name'][1] == "instructor" :
        return render_template('index.html')
    return render_template('login.html')

    

@app.route('/<name>/calendar.html')
def calendar(name):
    if 'name' in session:
        return render_template('calendar.html')
    else:
        return render_template('login.html')
@app.route('/<name>/index.html')
def index(name):
    if 'name' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')
@app.route('/<name>/news.html')
def news(name):
    if 'name' in session:
        return render_template('news.html')
    else:
        return render_template('login.html')

@app.route('/<name>/lectures.html')
def lectures(name):
    if 'name' in session:
        return render_template('lectures.html')
    else:
        return render_template('login.html')

@app.route('/<name>/labs.html')
def labs(name):
    if 'name' in session:
        return render_template('labs.html')
    else:
        return render_template('login.html')
@app.route('/<name>/assignments.html')
def assignments(name):
    if 'name' in session:
        return render_template('assignments.html')
    else:
        return render_template('login.html')
@app.route('/<name>/tests.html')
def tests(name):
    if 'name' in session:
        return render_template('tests.html')
    else:
        return render_template('login.html')
    
@app.route('/<name>/resources.html')
def resources(name):
    if 'name' in session:
        return render_template('resources.html')
    else:
        return render_template('login.html')
@app.route('/<name>/team.html')
def team(name):
    if 'name' in session:
        return render_template('team.html')
    else:
        return render_template('login.html')
    

def get_grades():
    grades = Grades.query.filter_by(username=session['name'][2]).all()
    return [grade for grade in grades]

@app.route('/<name>/grades.html')
def grades(name):
    if 'name' in session and session['name'][1] == 'student':
        grades = get_grades()
        return render_template('grades.html' , grades = grades)
    return render_template('login.html')


@app.route('/<name>/instructor_feedback.html')
def instructor_feedback(name):
    if 'name' in session and session['name'][1] == 'instructor':
        feedbacks = db.session.query(Feedback).filter_by(instructor=session['name'][2]).all()
        return render_template('instructor_feedback.html', feedbacks=feedbacks)
    return render_template("login.html")

def get_all_student_grades():
    students = Grades.query.all()
    return [[s.username, s.A1, s.A2, s.A3, s.tutorials, s.midterm,s.exam,s.final] for s in students]

@app.route('/<name>/instructor_grades.html')
def instructor_grades(name):
    if 'name' in session and session['name'][1] == 'instructor':
        students = get_all_student_grades()
        for i in range(len(students)):
            for j in range(8):
                if students[i][j] == None:
                    students[i][j] = '-'
        return render_template('instructor_grades.html', students = students)
    else:
        return render_template('login.html')
    
@app.route('/insert_grade', methods=['POST'])
def insert_grade():
    stud = request.form['student_select'] 
    mark_for = request.form['grade']
    mark = request.form['mark']
    if not mark.isdigit():
        mark = 0
    elif mark.isdigit() and mark != '':
        mark = int(mark)

    db.session.query(Grades).filter(Grades.username == stud).update({mark_for: mark})
    db.session.commit()
    info = db.session.query(Grades).filter(Grades.username == stud).first()
    grade = 0
    total = 0
    if info.A1 != None:
        grade += 8 * info.A1 / 100
        total += 8
    if info.A2 != None:
        grade += 10 * info.A2 / 100
        total += 10
    if info.A3 != None:
        grade += 15 * info.A3 / 100
        total += 15
    if info.tutorials != None:
        grade += 2 * info.tutorials / 100
        total += 2
    if info.midterm != None:
        grade += 25 * info.midterm / 100
        total += 25
    if info.exam != None:
        grade += 40 * info.exam / 100
        total += 40
    db.session.query(Grades).filter(Grades.username == stud).update({'final': 100*grade/total})
    db.session.commit()
    return redirect(url_for('instructor_grades', name=session['name'][0]))

def get_all_instructors():
    instructors = Person.query.filter_by(type='instructor').all()
    return [instructor.username for instructor in instructors]

@app.route('/<name>/feedback.html')
def feedback(name):
    if 'name' in session:
        instructors = get_all_instructors()
        return render_template('feedback.html', instructors=instructors)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('name', default = None)
    session.pop('name', default = None)
    return redirect(url_for('register'))



def add_users(reg_details):
    person = Person(username = reg_details[0],name = reg_details[1] , email = reg_details[2],type = reg_details[3], password = reg_details[4])
    db.session.add(person)
    db.session.commit()


@app.route('/submit-remark-request', methods=['POST'])
def submit_remark_request():

    test_type = request.form['test_type']
    reason = request.form['reason']
    name = session['name'][2]

    existing_record = RemarkRequest.query.filter_by(student=name, test_type=test_type).first()
    if existing_record:
        flash('Request already submitted!', 'error')
        return redirect(url_for('grades' ,name= session['name'][0]))

    # Create a new RemarkRequest object and add it to the database
    remark_request = RemarkRequest(name,test_type=test_type, reason=reason)

    db.session.add(remark_request)
    db.session.commit()

    flash('Request submitted successfully!', 'success')
    return redirect(url_for('grades' ,name= session['name'][0]))


@app.route('/<name>/instructor_regrade_request.html')
def instructor_regrade_request(name):
    if 'name' in session and session['name'][1] == 'instructor':
        A1 = db.session.query(RemarkRequest).filter_by(test_type = 'Assignment 1').all()
        A2 = db.session.query(RemarkRequest).filter_by(test_type = 'Assignment 2').all()
        A3 = db.session.query(RemarkRequest).filter_by(test_type = 'Assignment 3').all()
        Midterm = db.session.query(RemarkRequest).filter_by(test_type = 'Midterm Exam').all()
        Tutorials = db.session.query(RemarkRequest).filter_by(test_type = 'Tutorials').all()
        Exam = db.session.query(RemarkRequest).filter_by(test_type = 'Final Exam').all()
        return render_template('instructor_regrade_request.html', A1=A1, A2=A2, A3=A3, Midterm=Midterm, Tutorials=Tutorials, Exam=Exam)
    return render_template('login.html')


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        feedback_text = request.form['feedback_text']
        instructor = request.form['instructor']
        student = session['name'][0]  # Assuming you store student's name in the session

        # Check if feedback already exists for the same student and instructor
        existing_feedback = Feedback.query.filter_by(instructor=instructor, student=student).first()

        if existing_feedback:
            # Feedback already exists, you can handle it here, e.g., update the existing feedback
            # For now, let's just show a message to the user
            flash('Feedback already submitted for this instructor!', 'error')
            return redirect(url_for('feedback', name=session['name'][0]))  # Redirect to a suitable page

        # Create a new Feedback object and add it to the database
        feedback = Feedback(instructor=instructor, student=student, feedback=feedback_text)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('feedback' ,name= session['name'][0]))








@app.route('/get-instructors', methods=['GET'])
def get_instructors():
    instructors = Person.query.filter_by(type='instructor').all()
    instructor_names = [instructor.name for instructor in instructors]
    return jsonify({'instructors': instructor_names})






if __name__ == '__main__':
    app.run(debug=True)
