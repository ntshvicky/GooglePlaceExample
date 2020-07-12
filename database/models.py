from .db import db

class User(db.Document):
    phone = db.StringField(unique=True, required=True)
    fullname = db.StringField(required=True)
    mailid = db.StringField()
    password = db.StringField()

class Comment(db.Document):
    place_id = db.StringField(required=True)
    user_id = db.StringField(required=True)
    comment = db.StringField(required=True)


