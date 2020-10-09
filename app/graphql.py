from flask import Blueprint
from flask_graphql import GraphQLView

from .schema import schema

bp = Blueprint("graphql", __name__)

bp.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True))
