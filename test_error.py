from app import app, db, User
from flask.testing import FlaskClient

with app.test_client() as client:
    app.config['TESTING'] = True
    with app.app_context():
        # Login as doctor
        doctor = User.query.filter_by(username='admin_doctor').first()
        with client.session_transaction() as sess:
            sess['_user_id'] = str(doctor.id)
            sess['_fresh'] = True
    
    # Hit messages page
    resp = client.get('/messages')
    print("Status:", resp.status_code)
    if resp.status_code == 500:
        print(resp.data.decode('utf-8'))
