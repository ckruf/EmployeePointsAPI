from mongoengine import Document, StringField, ReferenceField, DateTimeField, BooleanField
from models.employees import Employees
from models.applications import Applications
from datetime import datetime

class Points(Document):
    date_added = DateTimeField(default=datetime.utcnow())
    date_earned = DateTimeField()
    employee = ReferenceField(Employees)
    application = ReferenceField(Applications)
    description = StringField()
    prod_env = BooleanField()


