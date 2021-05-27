from mongoengine import Document, StringField, BooleanField

class Employees(Document):
    name = StringField(required=True, unique=True)
    active = BooleanField(required=True)