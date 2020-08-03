import datetime
import json

from .sa import db

def now():
    return datetime.datetime.now()

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)

    # TODO (dhatch): Forign key & relationship.
    user_id = db.Column(db.Integer)
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
