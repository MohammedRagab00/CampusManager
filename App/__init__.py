from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# from flask_migrate import Migrate  # * Import Migrate (No need for now)
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///database.db"  # URI == Uniform Resource Identifier
)
app.config["SECRET_KEY"] = os.getenv("secretKey")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# Initialize Flask-Migrate
# migrate = Migrate(app, db)  # * No need for now

from App import routes  # ! Don't remove  # noqa: E402, F401
