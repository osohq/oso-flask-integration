from flask import Blueprint, current_app, jsonify
from werkzeug.exceptions import NotFound

from .models import Organization

bp = Blueprint("organization", __name__, url_prefix="/organizations")

@bp.route("/<int:id>", methods=["GET"])
def get_organization(id):
    organization = Organization.query.get(id)
    if organization is None:
        raise NotFound()

    current_app.oso.authorize(action="read", resource=organization)

    return jsonify(organization.as_dict())
