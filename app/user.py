from dataclasses import dataclass
from flask import current_app, g, request, Blueprint
from werkzeug.exceptions import Unauthorized

from sqlalchemy.orm import Session

from .models import Organization, User, db
from flask_oso import skip_authorization, authorize

bp = Blueprint("user", __name__)


class Actor:
    """base abstract user type"""
    pass

class Guest(Actor):
    """Anonymous user."""
    def __str__(self):
        return "Guest"


@bp.before_app_request
def set_current_user():
    """Set the `current_user` from the authorization header (if present)"""
    if not "current_user" in g:
        email = request.headers.get("user")
        if email:
            try:
                # TODO hack to query through a separate session that isn't
                # authorized.
                session = Session(bind=db.engine)
                g.current_user = session.query(User).filter(User.email==email).first()
            except Exception as e:
                current_app.logger.exception(e)
                return Unauthorized("user not found")
        else:
            g.current_user = Guest()


@bp.route("/whoami")
@authorize(resource=request)
def whoami():
    you = g.current_user
    if isinstance(you, User):
        organization = Organization.query.get(you.organization_id).name
        return f"You are {you.email}, the {you.title} at {organization}. (User ID: {you.id})"
