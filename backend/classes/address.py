from mongoengine import Document,StringField,IntField

class Address(Document):
    residence_number = StringField(required=True,min_length=1,regex= r'[a-zA-Z0-9/, \\]+')
    street = StringField(required=True,min_length=1)
    locality = StringField(required=True,min_length=1)
    pincode = IntField(required=True,min_value=100000,max_value=999999)
    state = StringField(required=True,min_length=1)
    city = StringField(required=True, min_length=1)