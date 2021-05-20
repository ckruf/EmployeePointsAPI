from mongoengine import Document, StringField, BooleanField

class Employees(Document):
    name = StringField(required=True)
    active = BooleanField(required=True)