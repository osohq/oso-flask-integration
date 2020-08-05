from dataclasses import dataclass
from flask import current_app, g, request, Blueprint
from oso import Oso, OsoException
from oso.extras import Http
from werkzeug.exceptions import BadRequest, Forbidden

from oso_flask import FlaskOso

bp = Blueprint("authorization", __name__)

base_oso = Oso()
oso = FlaskOso(base_oso)

def init_oso(app):
    from .user import Actor, Guest, User
    from . import models

    base_oso.register_class(Actor)
    base_oso.register_class(Guest)
    base_oso.register_class(User)

    base_oso.register_class(models.Organization)
    base_oso.register_class(models.Expense)

    oso.init_app(app)
    oso.require_authorization(app)
    oso.perform_route_authorization(app)

    for policy in app.config.get("OSO_POLICIES", []):
        base_oso.load_file(policy)

    app.oso = oso

    return oso
