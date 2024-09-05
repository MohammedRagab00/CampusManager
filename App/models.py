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

    # Relationship to Course_prerequisite
    courses = db.relationship(
        "Course_prerequisite",
        backref="course",
        lazy=True,
        foreign_keys="[Course_prerequisite.prerequisite_id]",
    )

    # Relationship to Section
    sections = db.relationship("Section", back_populates="course", lazy=True)


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

    # Relationship to Courses with back_populates
    course = db.relationship(
        "Courses", back_populates="sections", foreign_keys=[course_id]
    )

    registered_courses = db.relationship(
        "Course_registered", backref="section", lazy=True
    )
    instructor_id = db.Column(db.Integer(), db.ForeignKey("user.id"))


class Course_registered(db.Model):
    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    section_id = db.Column(db.Integer(), db.ForeignKey("section.id"), primary_key=True)

    def unregister_and_grade(self, grade):
        # Create a Course_grade entry
        course_grade = Course_grade(
            semester=self.section.semester,
            course_id=self.section.course_id,
            student_id=self.student_id,
            grade=grade,
        )
        db.session.add(course_grade)

        # Get the course credit hours
        course_credit_hours = self.section.course.credit_hours

        user = User.query.get(self.student_id)
        if user:
            # Update the GPA (weighted by course credit hours)
            self.update_gpa(user, grade, course_credit_hours)

            # Update passed credit hours if grade >= 60
            if grade >= 60:
                user.passed_credit_hours += course_credit_hours

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

    @staticmethod
    def grade_to_gpa(grade):
        """Convert a numeric grade to the corresponding GPA."""
        if 60 <= grade <= 64:
            return 1.0 + (grade - 60) * 0.1
        elif 65 <= grade <= 74:
            return 1.5 + (grade - 65) * 0.1
        elif 75 <= grade <= 84:
            return 2.5 + (grade - 75) * 0.1
        elif 85 <= grade <= 100:
            return 3.5 + (grade - 85) * 0.1
        return 0  # GPA is 0 for grades below 60

    def update_gpa(self, user, grade, course_credit_hours):
        # Convert the numeric grade to the corresponding GPA
        gpa_value = self.grade_to_gpa(grade)

        # Calculate the current total weighted GPA and total credits
        total_grades = user.gpa * user.passed_credit_hours

        # Update total grades with the new GPA value
        total_grades += gpa_value * course_credit_hours

        # Update total credits
        total_credits = user.passed_credit_hours + course_credit_hours

        # Calculate new GPA
        new_gpa = total_grades / total_credits

        # Ensure GPA does not exceed the maximum value
        user.gpa = min(new_gpa, 5)

        db.session.commit()


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
