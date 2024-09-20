from marshmallow import fields, pre_dump, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from sqlalchemy.types import LargeBinary, BLOB

from framework.commons.hex import b2h, h2b


import binascii
from marshmallow import fields

class HexBlob(fields.Field):
    """Custom field to serialize binary data as a hex string."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return binascii.hexlify(value).decode('utf-8')

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return binascii.unhexlify(value)
        except binascii.Error:
            raise fields.ValidationError("Invalid hex string")


def generate_marshmallow_auto_schema(sqlalchemy_model):
    class AutoSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = sqlalchemy_model
            load_instance = True
            include_relationships = True
            include_fk = True

    for column in sqlalchemy_model.__table__.columns:
        if not hasattr(AutoSchema, column.name):
            field = AutoSchema().get_field(column)
            if isinstance(column.type, (LargeBinary, BLOB)):
                field = HexBlob()
            setattr(AutoSchema, column.name, field)

    return AutoSchema


def obj2json(cls, obj):
    return generate_marshmallow_auto_schema(cls)().dump(obj)


def json2obj(cls, obj):
    return generate_marshmallow_auto_schema(cls).load(obj)
