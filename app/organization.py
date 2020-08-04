from dataclasses import dataclass
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

from .authorization import oso
from .models import Organization

bp = Blueprint("organization", __name__, url_prefix="/organizations")


@bp.route("/<int:id>", methods=["GET"])
def get_organization(id):
    organization = Organization.query.get(id)
    if organization is None:
        raise NotFound()

    oso.authorize(action="read", resource=organization)

    return organization.json()
