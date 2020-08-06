import datetime
import json

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def now():
    return datetime.datetime.now()

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)

    # TODO (dhatch): Forign key & relationship.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=now)
    updated_at = db.Column(db.DateTime, default=now)

    def json(self):
        return json.dumps({
            'id': self.id,
            'amount': self.amount,
            'user_id': self.user_id,
            'description': self.description
        })

    @classmethod
    def from_json(self, data):
        return self(**data)

class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def json(self):
        return json.dumps({
            'id': self.id,
            'name': self.name
        })

    @classmethod
    def from_json(self, data):
        return self(**data)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    title = db.Column(db.String(256))

    location_id = db.Column(db.Integer)
    organization_id = db.Column(db.Integer, db.ForeignKey('organiations.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def json(self):
        return json.dumps({
            'id': self.id,
            'email': self.email,
            'title': self.title,
            'location_id': self.location_id,
            'organization_id': self.organization_id,
            'manager_id': self.manager_id
        })

    @classmethod
    def from_json(self, data):
        return self(**data)
