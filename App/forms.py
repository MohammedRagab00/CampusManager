from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from App.models import User, Courses, Department, Place, Section
from flask import flash


class RegisterForm(FlaskForm):
    def validate_ssn(self, ssn_to_check):
        user = User.query.filter_by(ssn=ssn_to_check.data).first()
        if user:
            raise ValidationError("Ssn already exists!")
        if len(ssn_to_check.data) != 14:
            raise ValidationError("Ssn must be exactly 14 characters long.")
        ssn_str = str(ssn_to_check)
        # if (
        #     ssn_str[5:7] < "01"
        #     or ssn_str[5:7] > "31"
        #     or ssn_str[3:5] < "01"
        #     or ssn_str[3:5] > "12"
        #     or ssn_str[1:3] < "00"
        #     or ssn_str[1:3] > "24"
        # ):
        #     raise ValidationError("Invalid Ssn.")

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(
            email_address=email_address_to_check.data
        ).first()
        if email_address:
            raise ValidationError(
                "Email Address already exists! Please try a different email"
            )

    first_name = StringField(
        label="First name: ", validators=[Length(min=2, max=14), DataRequired()]
    )
    last_name = StringField(
        label="Last name: ", validators=[Length(min=2, max=14), DataRequired()]
    )
    ssn = StringField(label="Ssn: ", validators=[DataRequired()])
    email_address = StringField(
        label="Email Address: ", validators=[Email(), DataRequired()]
    )
    password1 = PasswordField(
        label="Password: ", validators=[Length(min=6, max=60), DataRequired()]
    )
    password2 = PasswordField(
        label="Confirm Password: ", validators=[EqualTo("password1"), DataRequired()]
    )
    submit = SubmitField(
        label="Create Account",
    )


class LoginForm(FlaskForm):
    email_address = StringField(label="Email: ", validators=[DataRequired()])
    password = PasswordField(label="Password: ", validators=[DataRequired()])
    submit = SubmitField(
        label="Sign In",
    )


class AddDepartmentForm(FlaskForm):
    def validate_name(self, name_to_check):
        user = Courses.query.filter_by(name=name_to_check.data).first()
        if user:
            raise ValidationError("Department already exists!")

    name = StringField(label="Name: ", validators=[DataRequired()])
    head_id = IntegerField(label="Id of the department's head: ", default=0)

    submit = SubmitField(label="Add Course")


class AddSectionForm(FlaskForm):
    def validate_course_id(self, course_id_to_check):
        course_id = Courses.query.filter_by(id=course_id_to_check.data).first()
        if course_id:
            pass
        else:
            raise ValidationError("Course Id doesn't exist!")

    def validate_place(self, place_to_check):
        place_num = Place.query.filter_by(place_num=place_to_check.data).first()
        if place_num:
            pass
        else:
            raise ValidationError("Place doesn't exist!")

    def validate_combination(self):
        course_id = self.course_id.data
        section_type = self.type.data
        group = self.group.data

        # Query the database to check if the combination already exists
        section = Section.query.filter_by(
            course_id=course_id, type=section_type, group=group
        ).first()
        if section:
            flash(
                "This combination of Course ID, Type, and Group already exists.",
                category="danger",
            )
            return False
        return True

    def validate(self, extra_validators=None):
        """Override the validate method to include custom validation."""
        if not super(AddSectionForm, self).validate(extra_validators):
            return False

        # Call the custom combination validator
        if not self.validate_combination():
            return False

        return True

    course_id = StringField(label="Course Id: ", validators=[DataRequired()])
    place = IntegerField(label="Place Num: ", validators=[DataRequired()])
    semester = StringField(
        label="Semester: ", validators=[DataRequired(), Length(max=20)]
    )
    type = StringField(label="Type: ", validators=[DataRequired()])
    day = IntegerField(label="Day: ", validators=[DataRequired()])
    time = StringField(label="Time: ", validators=[DataRequired()])
    group = IntegerField(label="Group: ", validators=[DataRequired()])
    capacity = IntegerField(label="Max capacity: ", validators=[DataRequired()])

    submit = SubmitField(label="Add Section")


class AddCourseForm(FlaskForm):
    def validate_id(self, id_to_check):
        user = Courses.query.filter_by(id=id_to_check.data).first()
        if user:
            raise ValidationError("Course already exists!")

    def validate_credit_hours(self, credit_hours_to_check):
        if credit_hours_to_check.data < 0 or credit_hours_to_check.data > 5:
            raise ValidationError("Credit hours should be between 0-5")

    def validate_department(self, department_to_check):
        department = Department.query.filter_by(id=department_to_check.data).first()
        if department:
            pass
        else:
            raise ValidationError("Department number doesn't exist!")

    id = StringField(label="Course ID: ", validators=[DataRequired()])
    name = StringField(label="Name: ", validators=[DataRequired()])
    credit_hours = IntegerField(label="Credit hours: ", validators=[DataRequired()])
    department = IntegerField(label="Department number", validators=[DataRequired()])

    submit = SubmitField(label="Add Course")


class AddPlaceForm(FlaskForm):
    def validate_place_num(self, place_num_to_check):
        place_num = Place.query.filter_by(place_num=place_num_to_check.data).first()
        if place_num:
            raise ValidationError("Place already exists!")

    def validate_capacity(self, capacity_to_check):
        if capacity_to_check.data < 10 or capacity_to_check.data > 120:
            raise ValidationError("Capacity should be between 10-120")

    def validate_department(self, department_to_check):
        department = Department.query.filter_by(id=department_to_check.data).first()
        if department:
            pass
        else:
            raise ValidationError("Department number doesn't exist!")

    place_num = IntegerField(label="Place Num: ", validators=[DataRequired()])
    department = IntegerField(label="Department Num: ", validators=[DataRequired()])
    capacity = IntegerField(label="Capacity", validators=[DataRequired()])

    submit = SubmitField(label="Add Place")


class EnrollSectionForm(FlaskForm):
    submit = SubmitField(
        label="Enroll Section!",
    )


class DropSectionForm(FlaskForm):
    submit = SubmitField(
        label="Drop Section!",
    )
