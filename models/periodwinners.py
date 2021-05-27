from mongoengine import Document, StringField, ReferenceField, DateTimeField, BooleanField
from models.employees import Employees

class PeriodWinners(Document):
    periodname = StringField()
    startdate = DateTimeField()
    enddate = DateTimeField()
    winner = ReferenceField(Employees, default=None, null=True)
    evaluated = BooleanField(default=False)