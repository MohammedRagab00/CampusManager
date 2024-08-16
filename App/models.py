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

    # items = db.relation("Item", backref="owned_user", lazy=True)

    # @property
    # def prettier_budget(self):
    #     if len(str(self.budget)) >= 4:
    #         return f"{str(self.budget)[:-3]},{str(self.budget)[-3:]}$"
    #     else:
    #         return f"{self.budget}$"

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


# class Item(db.Model):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(length=30), nullable=False, unique=True)
#     price = db.Column(db.Integer(), nullable=False)
#     barcode = db.Column(db.String(length=12), nullable=False, unique=True)
#     description = db.Column(db.String(length=1024), nullable=False, unique=True)
#     owner = db.Column(db.Integer(), db.ForeignKey("user.id"))

#     def __repr__(self):
#         return f"Item {self.name}"

#     def buy(self, user):
#         self.owner = user.id
#         user.budget -= self.price
#         db.session.commit()

#     def sell(self, user):
#         self.owner = None
#         user.budget += self.price
#         db.session.commit()


"""
from market import app,db
app.app_context().push()
db.create_all()
from market import Item
item1 = Item(name="", price = , barcode = '', description = "")
db.session.add(item1)
db.session.commit()

Item.query.all()

for item in Item.query.filter_by(price=500):
    item.name

import os
os.system('cls')


! -------------------------------------------------------------------------------------------------

from App.models import db,User,Courses,Course_prerequisite,Section,Course_registered,Course_grade,Place,Department
from App import app

app.app_context().push()

db.drop_all()
db.create_all()
u1 = User(first_name = 'me', last_name='me',password_hash = '123456', email_address = 'jsc@jsc.com')
db.session.add(u1)
db.session.commit()
User.query.all()

item1 = Item.query.filter_by(price=4400).first()
item1.owner  # we'll find nothing
item1.owner = User.query.filter_by(username='jsc').first() # Don't do this (Item only accept id not username)
db.session.rollback()
db.session.add(item1)
db.session.commit()
item1.owner = User.query.filter_by(username='jsc').first().id

item1 = Item.query.filter_by(price=4400).first()
item1.owned_user # returns obj

"""
