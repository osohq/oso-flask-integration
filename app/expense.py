from dataclasses import dataclass
from datetime import datetime
from flask import Blueprint, g, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from .authorization import authorize
from .sqlite import query_db
from .sa import db
from .user import User
from . import models

bp = Blueprint("expense", __name__, url_prefix="/expenses")


@bp.route("/<int:id>", methods=["GET"])
def get_expense(id):
    expense = models.Expense.query.get(id)
    if expense is None:
        raise NotFound()

    authorize("read", expense)
    return expense.json()


@bp.route("/submit", methods=["PUT"])
def submit_expense():
    expense_data = request.get_json(force=True)
    if not expense_data:
        raise BadRequest()

    # if no user id supplied, assume it is for the current user
    expense_data.setdefault("user_id", g.current_user.id)

    expense = models.Expense.from_json(expense_data)
    db.session.add(expense)
    db.session.commit()

    return expense.json()
