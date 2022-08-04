from flask import Flask, redirect, request, session
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///week7_database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

def getApp():
    return app

class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False, unique=True)
    course_code = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    children = db.relationship("Student", secondary="enrollments")


class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(
        db.Integer, nullable=False, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey(
        "student.student_id"), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey(
        "course.course_id"), nullable=False)

@app.route("/", methods=["GET","POST"])
def Home():
    student = Student.query.all()
    if request.method=="GET":
        if len(student) == 0:
            return render_template("no_student.html")
        else:
            return render_template("student_list.html", student=student)

@app.route("/student/create", methods=["GET", "POST"])
def get_data():
    if request.method == "GET":
        return render_template("add_student_form.html")

    elif request.method == "POST":
        roll_no = request.form["roll"]
        first_name = request.form["f_name"]
        last_name = request.form["l_name"]
        engine = create_engine("sqlite:///./week7_database.sqlite3")
        with Session(engine, autoflush=False) as session:
            db.session.begin()
            try:
                student = Student(roll_number=roll_no,
                                  first_name=first_name, last_name=last_name)
                db.session.add(student)
                db.session.flush()

            except:
                db.session.rollback()
                return render_template("student_error.html")
            else:
                db.session.commit()
        db.session.clear() 
        return redirect("/")

@app.route("/student/<int:student_iid>/update", methods=["GET", "POST"])
def update_info(student_iid):
    if request.method == "GET":
        student_id = Student.query.get(student_iid)
        course = Course.query.all()
        return render_template("update_student_form.html", student_id = student_id, course = course)
    
    elif request.method == "POST":
        first_name = request.form["f_name"]
        last_name = request.form["l_name"]
        c_id = request.form["course"]

        engine = create_engine("sqlite:///./week7_database.sqlite3")
        with Session(engine, autoflush=False) as session:
            db.session.begin()
            try:
                student = Student.query.get(student_iid)
                student.first_name = first_name
                student.last_name = last_name

                c_name = Course.query.filter_by(course_id=c_id).first()
                student_course = Enrollments(estudent_id=student.student_id, ecourse_id=c_name.course_id)
                db.session.add(student_course)
            except:
                db.session.rollback()
                raise
            else:
                db.session.commit()
        db.session.clear() 
        return redirect("/")

@app.route("/student/<int:student_iid>/delete", methods=["GET", "POST"])
def delete_info(student_iid):
    engine = create_engine("sqlite:///./week7_database.sqlite3")
    with Session(engine, autoflush=False) as session:
        db.session.begin()
        try:
            student_id = Student.query.get(student_iid)
            to_delete = Enrollments.query.filter_by(estudent_id=student_iid).all()
            for i in to_delete:
                db.session.delete(i)
            db.session.delete(student_id)
        except:
            db.session.rollback()
            raise
        else:
            db.session.commit()
    db.session.clear() 
    return redirect("/")

@app.route("/student/<int:student_iid>", methods=["GET", "POST"])
def complete_info(student_iid):
    student_id = Student.query.get(student_iid)
    enrol_ids = Enrollments.query.filter_by(estudent_id=student_iid).all()
    course_ids = [] 
    for i in enrol_ids:
        course_ids.append(i.ecourse_id)
    course_id = Course.query.filter(Course.course_id.in_(course_ids)).all()

    return render_template("student_detail.html", student_id = student_id, course_id=course_id)

@app.route("/student/<int:student_id>/withdraw/<int:course_id>", methods=["GET","POST"])
def withdraw_course(student_id, course_id):
    engine = create_engine("sqlite:///./week7_database.sqlite3")
    with Session(engine, autoflush=False) as session:
        db.session.begin()
        try:
            enrol_id = Enrollments.query.filter_by(estudent_id=student_id)
            final_enrol_id = None
            for i in enrol_id:
                if i.ecourse_id==course_id:
                    final_enrol_id = i
                    break
            db.session.delete(final_enrol_id)
        except:
            db.session.rollback()
            raise
        else:
            db.session.commit()
    db.session.clear() 
    return redirect("/")

@app.route("/courses", methods=["GET","POST"])
def Course_page():
    course_list = Course.query.all()
    if request.method=="GET":
        if len(course_list) == 0:
            return render_template("no_course.html")
        else:
            return render_template("course_list.html", c_list= course_list)

@app.route("/course/create", methods=["GET", "POST"])
def get_course_data():
    if request.method == "GET":
        return render_template("course_form.html")

    elif request.method == "POST":
        c_code = request.form["code"]
        c_name = request.form["c_name"]
        c_desc = request.form["desc"]
        engine = create_engine("sqlite:///./week7_database.sqlite3")
        with Session(engine, autoflush=False) as session:
            db.session.begin()
            try:
                course = Course(course_code=c_code,
                                  course_name=c_name, course_description=c_desc)
                db.session.add(course)
                db.session.flush()
            except:
                db.session.rollback()
                return render_template("course_error.html")
            else:
                db.session.commit()
        db.session.clear() 
        return redirect("/courses")

@app.route("/course/<int:course_id>/update", methods=["GET","POST"])
def update_course(course_id):
    if request.method == "GET":
        course_iid = Course.query.filter_by(course_id = course_id).first()
        return render_template("course_update_form.html", course = course_iid)
    
    elif request.method=="POST":
        n_name = request.form["c_name"]
        n_desc = request.form["desc"]
        engine = create_engine("sqlite:///./week7_database.sqlite3")
        with Session(engine, autoflush=False) as session:
            db.session.begin()
            try:
                fcourse = Course.query.filter_by(course_id = course_id).first()
                fcourse.course_name = n_name
                fcourse.course_description = n_desc
            except:
                db.session.rollback()
                raise
            else:
                db.session.commit()
        db.session.clear() 
        return redirect("/courses")

@app.route("/course/<int:course_id>/delete", methods=["GET", "POST"])
def delete_course(course_id):
    engine = create_engine("sqlite:///./week7_database.sqlite3")
    with Session(engine, autoflush=False) as session:
        db.session.begin()
        try:
            fcourse = Course.query.get(course_id)
            to_delete = Enrollments.query.filter_by(ecourse_id=course_id).all()
            for i in to_delete:
                db.session.delete(i)
            db.session.delete(fcourse)
        except:
            db.session.rollback()
            raise
        else:
            db.session.commit()
    db.session.clear() 
    return redirect("/courses")

@app.route("/course/<int:course_id>", methods=["GET", "POST"])
def complete_course_info(course_id):
    fcourse = Course.query.get(course_id)
    enrol_ids = Enrollments.query.filter_by(ecourse_id=course_id).all()
    student_ids = [] 
    for i in enrol_ids:
        student_ids.append(i.estudent_id)
    stu_id = Student.query.filter(Student.student_id.in_(student_ids)).all()

    return render_template("course_detail.html", student_id = stu_id, course_id=fcourse)

if __name__ == "__main__":
    app.debug = True
    app.run()