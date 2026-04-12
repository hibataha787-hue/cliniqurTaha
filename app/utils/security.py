from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
from app.models import db, AuditLog

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("Accès non autorisé.")
                return redirect(url_for('auth.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_audit_event(user_id, action, details=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
