"""
These schemas are all part of the aggregate schema Dataset. Reading the datasets out of a dataset catalog can lead to
a lot of user input, similar to reading input data on a REST api. As such, it makes sense to apply validation to all
data entered this way.
"""
import marshmallow as ma

from datarade import models


class FieldSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a datarade Field object

    This schema is only called indirectly as an attribute for DatasetSchema
    """
    name = ma.fields.Str(required=True)
    description = ma.fields.Str(required=False)
    type = ma.fields.Str(required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.Field':
        return models.Field(**data)


class DatabaseSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a datarade Database object

    This schema is only called indirectly as an attribute for DatasetSchema
    """
    driver = ma.fields.Str(required=True)
    database_name = ma.fields.Str(required=True)
    host = ma.fields.Str(required=True)
    port = ma.fields.Int(required=False)
    schema_name = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.Database':
        return models.Database(**data)


class DatasetSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a datarade Dataset object

    This is used to control and validate input from an end user's DatasetCatalog. It verifies that the proper
    structure was received.
    """
    name = ma.fields.Str(required=True)
    definition = ma.fields.Str(required=True)
    fields = ma.fields.Nested(FieldSchema, required=True, many=True)
    description = ma.fields.Str(required=False)
    database = ma.fields.Nested(DatabaseSchema, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> 'models.Dataset':
        return models.Dataset(**data)
