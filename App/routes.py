from App import app, db
from flask import render_template, redirect, url_for, flash, request
from App.models import User, Courses, Department, Section, Place, Course_registered
from App.forms import (
    RegisterForm,
    LoginForm,
    AddCourseForm,
    AddDepartmentForm,
    AddSectionForm,
    AddPlaceForm,
    EnrollSectionForm,
    DropSectionForm,
)
from flask_login import login_user, logout_user, login_required, current_user
import os


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/profile")
@login_required
def profile_page():
    user = current_user
    return render_template("profile.html", user=user)


@app.route("/ed", methods=["GET", "POST"])
@login_required
def ed_page():
    enroll_form = EnrollSectionForm()
    drop_form = DropSectionForm()

    if request.method == "POST":
        # Enroll Section Logic
        enroll_section_id = request.form.get("enrolled_section")
        print(f"Received enrolled_section: {enroll_section_id}")  # Debugging line

        if enroll_section_id:
            try:
                enroll_section_id = int(enroll_section_id)  # Convert to integer
            except ValueError:
                return redirect(url_for("ed_page"))

            # Check if the user is already enrolled
            existing_enrollment = Course_registered.query.filter_by(
                student_id=current_user.id, section_id=enroll_section_id
            ).first()

            if existing_enrollment:
                flash(
                    f"Section: {enroll_section_id} is already enrolled",
                    category="danger",
                )
            else:
                # Fetch the section to enroll
                sec_obj = Section.query.get(enroll_section_id)
                if sec_obj and current_user.can_enroll(sec_obj):
                    # Create a new Course_registered object for enrollment
                    new_enrollment = Course_registered(
                        student_id=current_user.id, section_id=enroll_section_id
                    )
                    db.session.add(new_enrollment)
                    db.session.commit()
                    flash(
                        f"Section: {enroll_section_id} is successfully enrolled",
                        category="success",
                    )
                else:
                    flash("You cannot enroll in this section", category="danger")

        # Drop Section Logic
        drop_sec_id = request.form.get("drop_sec")
        print(f"Received drop_sec: {drop_sec_id}")  # Debugging line

        if drop_sec_id:
            try:
                drop_sec_id = int(drop_sec_id)  # Convert to integer
            except ValueError:
                return redirect(url_for("ed_page"))

            d_sec_obj = Course_registered.query.filter_by(
                student_id=current_user.id, section_id=drop_sec_id
            ).first()

            if d_sec_obj:
                d_sec_obj.drop(current_user)
                flash(
                    f"Section: {drop_sec_id} is dropped successfully",
                    category="success",
                )
            else:
                flash("Section not found or you are not enrolled", category="danger")

        return redirect(url_for("ed_page"))

    if request.method == "GET":
        sections = Section.query.all()
        enrolled_sec = Course_registered.query.filter_by(
            student_id=current_user.id
        ).all()
        return render_template(
            "ed.html",
            sections=sections,
            enroll_form=enroll_form,
            enrolled_sec=enrolled_sec,
            drop_form=drop_form,
        )

    enroll_form = EnrollSectionForm()
    drop_form = DropSectionForm()

    if request.method == "POST":
        # Enroll Section Logic
        enroll_section_id = request.form.get("enrolled_section")

        if enroll_section_id:
            enroll_section_id = int(enroll_section_id)  # Convert to integer if needed
            # Check if the user is already enrolled
            existing_enrollment = Course_registered.query.filter_by(
                student_id=current_user.id, section_id=enroll_section_id
            ).first()

            if existing_enrollment:
                flash(
                    f"Section: {enroll_section_id} is already enrolled",
                    category="danger",
                )
            else:
                # Fetch the section to enroll
                sec_obj = Section.query.get(enroll_section_id)
                if sec_obj and current_user.can_enroll(sec_obj):
                    # Create a new Course_registered object for enrollment
                    new_enrollment = Course_registered(
                        student_id=current_user.id, section_id=enroll_section_id
                    )
                    db.session.add(new_enrollment)
                    db.session.commit()
                    flash(
                        f"Section: {enroll_section_id} is successfully enrolled",
                        category="success",
                    )
                else:
                    flash("You cannot enroll in this section", category="danger")

        # Drop Section Logic
        drop_sec_id = request.form.get("drop_sec")

        if drop_sec_id:
            drop_sec_id = int(drop_sec_id)  # Convert to integer if needed
            d_sec_obj = Course_registered.query.filter_by(
                student_id=current_user.id, section_id=drop_sec_id
            ).first()

            if d_sec_obj:
                d_sec_obj.drop(current_user)
                flash(
                    f"Section: {drop_sec_id} is dropped successfully",
                    category="success",
                )
            else:
                flash("Section not found or you are not enrolled", category="danger")

        return redirect(url_for("ed_page"))

    if request.method == "GET":
        sections = Section.query.all()
        enrolled_sec = Course_registered.query.filter_by(
            student_id=current_user.id
        ).all()
        return render_template(
            "ed.html",
            sections=sections,
            enroll_form=enroll_form,
            enrolled_sec=enrolled_sec,
            drop_form=drop_form,
        )


@app.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=form.password1.data,
            ssn=form.ssn.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(
            f"Account Created Successfully! U're now logged in as {user_to_create.first_name} {user_to_create.last_name}",
            category="success",
        )

        return redirect(url_for("profile_page"))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f"There was an error with creating a user: {err_msg}", category="danger"
            )
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(
            email_address=form.email_address.data
        ).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(
                f"Success! You're logged in as: {attempted_user.first_name} {attempted_user.last_name}",
                category="success",
            )
            if attempted_user.email_address == "mr@mr.com":
                return redirect(url_for("add_course_page"))
            return redirect(url_for("profile_page"))
        else:
            flash(
                "Username and Password are not matched! Please try again",
                category="danger",
            )

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been logged out", category="info")
    return redirect(url_for("home_page"))


@app.route(os.getenv("admin") + "0", methods=["GET", "POST"])
def add_course_page():
    # To add a course
    form3 = AddCourseForm()
    if form3.validate_on_submit():
        course_to_create = Courses(
            id=form3.id.data,
            name=form3.name.data,
            department=form3.department.data,
            credit_hours=form3.credit_hours.data,
        )
        db.session.add(course_to_create)
        db.session.commit()
        flash(
            f"{course_to_create.name} is added Successfully!",
            category="success",
        )

    if form3.errors != {}:
        for err_msg in form3.errors.values():
            flash(
                f"There was an error with adding a course: {err_msg}", category="danger"
            )

    return render_template("addcourse.html", form3=form3)


@app.route(os.getenv("admin") + "1", methods=["GET", "POST"])
def add_department_page():
    # To add a department
    form2 = AddDepartmentForm()
    if form2.validate_on_submit():
        department_to_create = Department(
            name=form2.name.data,
            head_id=form2.head_id.data,
        )
        db.session.add(department_to_create)
        db.session.commit()
        flash(
            f"{department_to_create.name} is created Successfully!",
            category="success",
        )

    if form2.errors != {}:
        for err_msg in form2.errors.values():
            flash(
                f"There was an error with adding a department: {err_msg}",
                category="danger",
            )

    return render_template("adddepartment.html", form2=form2)


@app.route(os.getenv("admin") + "2", methods=["GET", "POST"])
def add_section_page():
    form1 = AddSectionForm()
    if form1.validate_on_submit():
        section_to_create = Section(
            course_id=form1.course_id.data,
            place=form1.place.data,
            semester=form1.semester.data,
            type=form1.type.data,
            day=form1.day.data,
            time=form1.time.data,
            group=form1.group.data,
            capacity=form1.capacity.data,
        )
        db.session.add(section_to_create)
        db.session.commit()
        flash(
            f"{section_to_create.id} is added Successfully!",
            category="success",
        )

    if form1.errors != {}:
        for err_msg in form1.errors.values():
            flash(
                f"There was an error creating this section: {err_msg}",
                category="danger",
            )

    return render_template("addsection.html", form1=form1)


@app.route(os.getenv("admin") + "3", methods=["GET", "POST"])
def add_place_page():
    # To add a place
    form1 = AddPlaceForm()
    if form1.validate_on_submit():
        place_to_create = Place(
            place_num=form1.place_num.data,
            department=form1.department.data,
            capacity=form1.capacity.data,
        )
        db.session.add(place_to_create)
        db.session.commit()
        flash(
            f"{place_to_create.place_num} is added Successfully!",
            category="success",
        )

    if form1.errors != {}:
        for err_msg in form1.errors.values():
            flash(
                f"There was an error with adding a place: {err_msg}", category="danger"
            )

    return render_template("addplace.html", form1=form1)


# @app.route(os.getenv("admin")+"4", methods=["GET", "POST"])
# def add_course_prerequisite_page():
#     # TODO To add a course_prerequisite
#     form1 = AddCourseForm()
#     if form1.validate_on_submit():
#         course_to_create = Courses(
#             id=form1.id.data,
#             name=form1.name.data,
#             department=form1.department.data,
#             credit_hours=form1.credit_hours.data,
#         )
#         db.session.add(course_to_create)
#         db.session.commit()
#         flash(
#             f"{course_to_create.name} is added Successfully!",
#             category="success",
#         )


#     if form1.errors != {}:
#         for err_msg in form1.errors.values():
#             flash(
#                 f"There was an error with adding a course: {err_msg}", category="danger"
#             )

#     return render_template("addcourse.html", form1=form1)

# @app.route('/about/<username>')
# def about_page(username):
#     return f'<h2>This is the About Page of {username} </h2>'
