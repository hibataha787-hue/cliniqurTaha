from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
mail = Mail()
limiter = Limiter(get_remote_address, default_limits=["200 per day", "50 per hour"])
talisman = Talisman()
csrf = CSRFProtect()
login_manager = LoginManager()
