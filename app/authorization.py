from dataclasses import dataclass
from flask import current_app, g, request, Blueprint
from oso import Oso, OsoException
from oso.extras import Http
from werkzeug.exceptions import BadRequest, Forbidden

from oso_flask import Oso

bp = Blueprint("authorization", __name__)

oso = Oso()

def init_oso(app):
    from .user import Actor, Guest, User
    from . import models

    oso.register_class(Actor)
    oso.register_class(Guest)
    oso.register_class(User)

    oso.register_class(models.Organization)
    oso.register_class(models.Expense)

    oso.init_app(app)
    oso.require_authorization(app)
    oso.perform_route_authorization(app)

    for policy in app.config.get("OSO_POLICIES", []):
        oso.load_file(policy)

    app.oso = oso

    return oso
