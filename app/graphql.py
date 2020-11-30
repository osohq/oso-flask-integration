from flask import Blueprint
from flask_graphql import GraphQLView
from flask import current_app
from promise import Promise

from sqlalchemy_oso.hooks import authorized_sessionmaker

from werkzeug.exceptions import Forbidden

from .authorization import oso

from .schema import schema
from .models import db

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

def field_authorized(parent, info):
    graphene_type = getattr(info.parent_type, "graphene_type", None)
    if graphene_type is None:
        return True

    should_auth = one_result(current_app.oso.oso.query_rule("graphql_authorize_schema",
                                                            graphene_type))
    if not should_auth:
        print(f"field  should not auth type {graphene_type}")
        return True

    field_allowed = one_result(
        current_app.oso.oso.query_rule("allow_field", current_app.oso.current_actor,
                                       "query",
                                       graphene_type,
                                       parent,
                                       info.field_name))

    return field_allowed

class UnauthException(Exception): pass

class AuthorizationMiddleware(object):
    def resolve(self, next, root, info, **args):
        if not field_authorized(root, info):
            raise UnauthException(f"Field {info.field_name} not authorized on {info.parent_type.name}")

        print(f"resolve: field_name = {info.field_name}, parent = {root}, rt type = {info.return_type}")
        field_value = next(root, info, **args)

        if isinstance(field_value, Promise):
            field_value = field_value.then(authorize_graphql_value)
        else:
            field_value = authorize_graphql_value(value)

        return field_value

class SQLAlchemyAuthorizedGraphQLView(GraphQLView):
    sessionmaker = authorized_sessionmaker(
        get_oso=lambda: current_app.oso.oso,
        get_user=lambda: current_app.oso.current_actor,
        # TODO non read action.
        get_action=lambda: "read")

    def get_context(self):
        return {
            'session': self.sessionmaker(bind=db.engine)
        }


bp.add_url_rule('/graphql', view_func=SQLAlchemyAuthorizedGraphQLView.as_view(
    'graphql',
    schema=schema,
    middleware=[],
    graphiql=True))