from App import app, db
from flask import render_template, redirect, url_for, flash, request
from App.models import (
    User,
    Courses,
    Department,
    Section,
    Place,
    Course_registered,
    Course_prerequisite,
    Course_grade,
)
from App.forms import (
    RegisterForm,
    LoginForm,
    AddCourseForm,
    AddDepartmentForm,
    AddSectionForm,
    AddPlaceForm,
    EnrollSectionForm,
    DropSectionForm,
    AddCoursePrerequisiteForm,
    EditRoleForm,
    DeleteUserForm,
    GradeStudentForm,
    RegisterTeachingForm,
    UnRegisterTeachingForm,
)
from flask_login import login_user, logout_user, login_required, current_user


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
                    # Check prerequisites
                    prerequisites = Course_prerequisite.query.filter_by(
                        course_id=sec_obj.course_id
                    ).all()
                    prerequisites_met = True

                    for prerequisite in prerequisites:
                        grade_entry = Course_grade.query.filter_by(
                            student_id=current_user.id,
                            course_id=prerequisite.prerequisite_id,
                            semester=sec_obj.semester,
                        ).first()

                        if not grade_entry or grade_entry.grade < 60:
                            prerequisites_met = False
                            break

                    if prerequisites_met:
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
                        flash(
                            "You have not met the prerequisites for this section",
                            category="danger",
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
        # Fetch all sections
        sections = Section.query.all()

        # Filter out sections where the user has already passed the course
        valid_sections = []
        for sec in sections:
            # Check if user has already passed the course
            grade_entry = Course_grade.query.filter_by(
                student_id=current_user.id,
                course_id=sec.course_id,
                semester=sec.semester,
            ).first()

            if not grade_entry or grade_entry.grade < 60:
                # Check prerequisites if not already passed
                prerequisites = Course_prerequisite.query.filter_by(
                    course_id=sec.course_id
                ).all()
                prerequisites_met = True

                for prerequisite in prerequisites:
                    prereq_grade_entry = Course_grade.query.filter_by(
                        student_id=current_user.id,
                        course_id=prerequisite.prerequisite_id,
                        semester=sec.semester,
                    ).first()

                    if not prereq_grade_entry or prereq_grade_entry.grade < 60:
                        prerequisites_met = False
                        break

                if prerequisites_met:
                    valid_sections.append(sec)

        enrolled_sec = Course_registered.query.filter_by(
            student_id=current_user.id
        ).all()
        return render_template(
            "ed.html",
            sections=valid_sections,
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
            if attempted_user.role == 2:
                return redirect(url_for("users_page"))
            elif attempted_user.role == 1:
                return redirect(url_for("instructor_dashboard"))
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


@app.route("/addCourse", methods=["GET", "POST"])
def add_course_page():
    if current_user.role != 2:
        return render_template("unauthorized.html"), 403

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


@app.route("/addDepartment", methods=["GET", "POST"])
def add_department_page():
    if current_user.role != 2:
        return render_template("unauthorized.html"), 403

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


@app.route("/addSection", methods=["GET", "POST"])
def add_section_page():
    if current_user.role != 2:
        return render_template("unauthorized.html"), 403

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


@app.route("/addPlace", methods=["GET", "POST"])
def add_place_page():
    if current_user.role != 2:
        return render_template("unauthorized.html"), 403

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


@app.route("/addCoursePrerequisite", methods=["GET", "POST"])
def add_course_prerequisite_page():
    if current_user.role != 2:
        return render_template("unauthorized.html"), 403

    # add a course_prerequisite
    form = AddCoursePrerequisiteForm()
    if form.validate_on_submit():
        course_prerequisite_to_create = Course_prerequisite(
            course_id=form.course_id.data,
            prerequisite_id=form.prerequisite_id.data,
        )
        db.session.add(course_prerequisite_to_create)
        db.session.commit()
        flash(
            f"{course_prerequisite_to_create.course_id}, {course_prerequisite_to_create.prerequisite_id} is added Successfully!",
            category="success",
        )

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f"There was an error with adding a course prerequisite: {err_msg}",
                category="danger",
            )

    return render_template("addcourseprerequisite.html", form=form)


@app.route("/users", methods=["GET", "POST"])
@login_required
def users_page():
    if current_user.role != 2:
        return render_template("unauthorized.html"), 403
    edit_form = EditRoleForm()
    delete_form = DeleteUserForm()

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_role = request.form.get("role")
        delete_user_id = request.form.get("delete_user_id")

        # Handle role edit
        if user_id and new_role is not None:
            try:
                user = User.query.get(int(user_id))
                user.role = int(new_role)
                db.session.commit()
                flash(
                    f"Role for User {user_id} has been updated to {new_role}.",
                    "success",
                )
            except Exception as e:
                flash(f"Error updating role for User {user_id}: {e}", "danger")

        # Handle user deletion
        if delete_user_id:
            try:
                user_to_delete = User.query.get(int(delete_user_id))
                db.session.delete(user_to_delete)
                db.session.commit()
                flash(f"User {delete_user_id} has been deleted.", "success")
            except Exception as e:
                flash(f"Error deleting User {delete_user_id}: {e}", "danger")

        return redirect(url_for("users_page"))

    if request.method == "GET":
        query = request.args.get("query")
        if query:
            users = User.query.filter(
                (User.first_name.ilike(f"%{query}%"))
                | (User.last_name.ilike(f"%{query}%"))
                | (User.email_address.ilike(f"%{query}%"))
            ).all()
        else:
            users = User.query.all()

        return render_template(
            "users.html", users=users, edit_form=edit_form, delete_form=delete_form
        )


@app.route("/instructor/dashboard")
@login_required
def instructor_dashboard():
    if current_user.role != 1:
        return render_template("unauthorized.html"), 403
    taught_sections = current_user.taught_sections
    return render_template("instructor_dashboard.html", taught_sections=taught_sections)


@app.route("/instructor/register_teaching", methods=["GET", "POST"])
@login_required
def teaching_page():
    if current_user.role != 1:
        return render_template("unauthorized.html"), 403

    register_form = RegisterTeachingForm()
    unregister_form = UnRegisterTeachingForm()

    if request.method == "POST":
        if (
            register_form.action.data == "register"
            and register_form.validate_on_submit()
        ):
            reg_sec_id = register_form.section_id.data
            section = Section.query.filter_by(id=reg_sec_id).first()
            if section:
                if section.instructor_id == current_user.id:
                    flash("You are already registered for this section.", "warning")
                else:
                    section.instructor_id = current_user.id
                    db.session.commit()
                    flash(
                        "Successfully registered for teaching the section.", "success"
                    )
                return redirect(url_for("instructor_dashboard"))
            flash("Section not found.", "danger")

        elif (
            unregister_form.action.data == "unregister"
            and unregister_form.validate_on_submit()
        ):
            unr_sec_id = unregister_form.section_id.data
            section = Section.query.get(unr_sec_id)
            if section:
                if section.instructor_id is None:
                    flash("You are not registered for this section.", "warning")
                elif section.instructor_id != current_user.id:
                    flash(
                        "You cannot unregister from a section you are not assigned to.",
                        "danger",
                    )
                else:
                    section.instructor_id = None
                    db.session.commit()
                    flash(
                        "Successfully unregistered from teaching the section.",
                        "success",
                    )
                return redirect(url_for("instructor_dashboard"))
            flash("Section not found.", "danger")

        return redirect(url_for("teaching_page"))

    if request.method == "GET":
        return render_template(
            "teaching.html",
            register_form=register_form,
            unregister_form=unregister_form,
        )


@app.route("/instructor/grade_students/<int:section_id>", methods=["GET", "POST"])
@login_required
def grade_students(section_id):
    if current_user.role != 1:
        return render_template("unauthorized.html"), 403

    section = Section.query.get_or_404(section_id)
    if section.instructor_id != current_user.id:
        return render_template("unauthorized.html"), 403

    form = GradeStudentForm()
    if form.validate_on_submit():
        # Form submission handling
        registration = Course_registered.query.filter_by(
            student_id=form.student_id.data, section_id=section_id
        ).first()
        if registration:
            registration.unregister_and_grade(form.grade.data)
            flash("Grade submitted successfully.", "success")
            return redirect(
                url_for("grade_students", section_id=section_id)
            )  # Redirect after successful submission
        else:
            flash("Student not found in this section.", "danger")
            return redirect(
                url_for("grade_students", section_id=section_id)
            )  # Redirect even when student is not found

    # Handle form errors
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f"There was an error with grading a student: {err_msg}",
                category="danger",
            )

    # Return the page with the form and students in case of GET request or form error
    registered_students = Course_registered.query.filter_by(section_id=section_id).all()
    return render_template(
        "grade_students.html",
        form=form,
        students=registered_students,
        section=section,
    )
