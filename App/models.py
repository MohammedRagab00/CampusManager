from App import db, bcrypt, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(length=20), nullable=False, unique=False)
    last_name = db.Column(db.String(length=20), nullable=False, unique=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    ssn = db.Column(db.String(), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    major = db.Column(db.Integer(), db.ForeignKey("department.id"))
    role = db.Column(db.Integer(), nullable=False, default=0)
    gpa = db.Column(db.Integer(), nullable=False, default=0)
    passed_credit_hours = db.Column(db.Integer(), nullable=False, default=0)

    registered_courses = db.relationship(
        "Course_registered", backref="student", lazy=True
    )

    taught_sections = db.relationship(
        "Section", backref="instructor", lazy=True, foreign_keys="Section.instructor_id"
    )

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(
            self.password_hash, attempted_password
        )  # True or False

    def can_enroll(self, sec_obj):
        if Course_registered.query.filter_by(
            student_id=self.id, section_id=sec_obj.id
        ).first():
            return False
        return True

    def can_drop(self, sec_obj):
        if Course_registered.query.filter_by(
            student_id=self.id, section_id=sec_obj.section_id
        ).first():
            return True
        return False

    def __repr__(self):
        return f"User {self.first_name} {self.last_name}"


class Courses(db.Model):
    id = db.Column(db.String(length=10), primary_key=True)
    name = db.Column(db.String(length=20), nullable=False, unique=True)
    credit_hours = db.Column(db.Integer(), nullable=False, default=3)
    department = db.Column(db.Integer(), db.ForeignKey("department.id"))

    # Specify foreign_keys argument and change backref name
    courses = db.relationship(
        "Course_prerequisite",
        backref="course",
        lazy=True,
        foreign_keys="[Course_prerequisite.prerequisite_id]",
    )
    sections = db.relationship(
        "Section", backref="course", lazy=True, foreign_keys="[Section.course_id]"
    )


class Course_prerequisite(db.Model):
    course_id = db.Column(
        db.String(length=10), db.ForeignKey("courses.id"), primary_key=True
    )
    prerequisite_id = db.Column(
        db.String(length=10), db.ForeignKey("courses.id"), primary_key=True
    )


class Section(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    course_id = db.Column(db.String(length=10), db.ForeignKey("courses.id"))
    place = db.Column(db.Integer(), db.ForeignKey("place.place_num"), nullable=False)
    semester = db.Column(db.String(length=20), nullable=False)
    type = db.Column(db.String(length=10), nullable=False, default="Theoretical")
    day = db.Column(db.Integer(), nullable=False)
    time = db.Column(db.String(length=10), nullable=False)
    group = db.Column(db.Integer(), nullable=False)
    capacity = db.Column(db.Integer(), nullable=False, default=26)

    registered_courses = db.relationship(
        "Course_registered", backref="section", lazy=True
    )
    instructor_id = db.Column(db.Integer(), db.ForeignKey("user.id"))


class Course_registered(db.Model):
    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    section_id = db.Column(db.Integer(), db.ForeignKey("section.id"), primary_key=True)

    def enroll(self, user):
        self.student_id = user.id
        db.session.add(self)
        db.session.commit()

    def drop(self, user):
        self.student_id = user.id
        db.session.delete(self)
        db.session.commit()

    def unregister_and_grade(self, grade):
        self.grade = grade

        # Create a Course_grade entry
        course_grade = Course_grade(
            semester=self.section.semester,
            course_id=self.section.course_id,
            student_id=self.student_id,
            grade=grade,
        )
        db.session.add(course_grade)

        # Delete all registrations matching course_id and group
        registrations_to_delete = (
            Course_registered.query.join(Section)
            .filter(
                Course_registered.student_id == self.student_id,
                Section.course_id == self.section.course_id,
                Section.group == self.section.group,
            )
            .all()
        )

        for registration in registrations_to_delete:
            db.session.delete(registration)

        db.session.commit()


# class Grade(db.Model):
#     student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
#     semester = db.Column(db.String(length=20), primary_key=True)
#     grade = db.Column(db.Integer(), nullable=False)


class Course_grade(db.Model):
    semester = db.Column(db.String(length=20), primary_key=True)
    course_id = db.Column(db.Integer(), db.ForeignKey("courses.id"), primary_key=True)
    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    grade = db.Column(db.Integer(), nullable=False)


class Place(db.Model):
    place_num = db.Column(db.Integer(), primary_key=True)
    department = db.Column(db.Integer(), db.ForeignKey("department.id"))
    capacity = db.Column(db.Integer(), nullable=False, default=30)
    sections = db.relationship("Section", backref="place_ref", lazy=True)


class Department(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=20), nullable=False)
    head_id = db.Column(
        db.Integer(), db.ForeignKey("user.id"), nullable=False, default=0
    )
