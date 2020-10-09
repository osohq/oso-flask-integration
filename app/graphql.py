from flask import Blueprint
from flask_graphql import GraphQLView
from flask import current_app
from promise import Promise

from werkzeug.exceptions import Forbidden

from .authorization import oso

from .schema import schema

bp = Blueprint("graphql", __name__)

def one_result(iter):
    try:
        next(iter)
    except StopIteration:
        return False

    return True

def authorize_graphql_value(value):
    print("authorize value", value)

    should_auth = one_result(current_app.oso.oso.query_rule("graphql_authorize", value))
    if should_auth:
        try:
            print(f"Authorize {value}")
            oso.authorize(resource=value, action="query")
        except Forbidden:
            return None

    return value

class AuthorizationMiddleware(object):
    def resolve(self, next, root, info, **args):
        field_value = next(root, info, **args)

        if isinstance(field_value, Promise):
            field_value = field_value.then(authorize_graphql_value)
        else:
            authorize_graphql_value(value)

        return field_value

bp.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    middleware=[AuthorizationMiddleware()],
    graphiql=True))
