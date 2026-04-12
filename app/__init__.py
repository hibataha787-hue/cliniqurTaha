import os
from flask import Flask
from app.extensions import db, mail, limiter, talisman, csrf, login_manager
from werkzeug.security import generate_password_hash
from app.models import User

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = 'nutrition-clinic-secret-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'hanaaamira9@gmail.com'
    app.config['MAIL_PASSWORD'] = 'sliv wxlh aidb puhs'
    app.config['MAIL_DEFAULT_SENDER'] = 'hanaaamira9@gmail.com'

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    talisman.init_app(app, 
        content_security_policy=None, 
        force_https=False
    )
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.doctor import doctor_bp
    from app.routes.patient import patient_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Seed Admin Account
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='taha').first():
            doctor = User(
                username='taha',
                email='hanaaalira9@gmail.com',
                password=generate_password_hash('taha123', method='scrypt'),
                role='doctor',
                full_name='Dr. Taha',
                is_2fa_enabled=True
            )
            db.session.add(doctor)
            db.session.commit()
            print("Doctor account seeded: taha / taha123 (with Email 2FA)")

    return app
