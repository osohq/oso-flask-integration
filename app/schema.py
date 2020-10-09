import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from flask import g

from . import models

class Expense(SQLAlchemyObjectType):
    class Meta:
        model = models.Expense
        interfaces = (relay.Node,)

class Organization(SQLAlchemyObjectType):
    class Meta:
        model = models.Organization
        interfaces = (relay.Node,)

class User(SQLAlchemyObjectType):
    class Meta:
        model = models.User
        interfaces = (relay.Node,)

class Query(graphene.ObjectType):
    expenses = SQLAlchemyConnectionField(Expense.connection)
    organizations = SQLAlchemyConnectionField(Organization.connection)
    user = graphene.Field(User)

    def resolve_user(parent, into):
        return g.current_user if isinstance(g.current_user, models.User) else None


schema = graphene.Schema(query=Query)
