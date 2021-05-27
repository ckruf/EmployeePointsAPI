from mongoengine import Document, StringField

class Applications(Document):
    name = StringField(required=True)
    