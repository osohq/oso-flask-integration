from flask import Blueprint, g, request, current_app, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from flask_oso import skip_authorization

from .models import db, Expense

bp = Blueprint("expense", __name__, url_prefix="/expenses")


@bp.route("/<int:id>", methods=["GET"])
def get_expense(id):
    expense = Expense.query.get(id)
    if expense is None:
        raise NotFound()

    current_app.oso.authorize(action="read", resource=expense)
    return jsonify(expense.as_dict())


@bp.route("/submit", methods=["PUT"])
@skip_authorization
def submit_expense():
    expense_data = request.get_json(force=True)
    if not expense_data:
        raise BadRequest()

    # if no user id supplied, assume it is for the current user
    expense_data.setdefault("user_id", g.current_user.id)

    expense = Expense.from_json(expense_data)
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.as_dict())
