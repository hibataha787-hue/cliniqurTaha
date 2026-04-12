from app import create_app
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    u = User.query.filter_by(username='taha').first()
    if u:
        print(f"User: {u.username}")
        print(f"Hash: {u.password}")
        success = check_password_hash(u.password, 'taha123')
        print(f"Password 'taha123' check: {success}")
    else:
        print("User 'taha' not found in database.")
