import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from flask import g

from . import models

class Expense(SQLAlchemyObjectType):
    class Meta:
        model = models.Expense
        interfaces = (relay.Node,)

class ExpenseInput(graphene.InputObjectType):
    amount = graphene.Int(required=True)
    description = graphene.String(required=True)

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
    node = graphene.relay.Node.Field()

    def resolve_user(parent, info):
        return g.current_user if isinstance(g.current_user, models.User) else None


class CreateExpense(graphene.Mutation):
    class Arguments:
        expense_data = ExpenseInput(required=True)

    expense = graphene.Field(Expense)

    def mutate(root, info, expense_data=None):
        expense = models.Expense(
            description=expense_data.description,
            amount=expense_data.amount,
            user_id=g.current_user.id
        )

        models.db.session.add(expense)
        models.db.session.commit()

        return CreateExpense(expense=expense)

class Mutation(graphene.ObjectType):
    create_expense = CreateExpense.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)



def oso_register_schema(schema):
    """Register schema types with oso."""
    from .authorization import base_oso
    for name, type_ in schema.get_type_map().items():
        try:
            base_oso.register_class(type_.graphene_type, name=f"schema::{name}")
        except AttributeError:
            continue

oso_register_schema(schema)