"""
This is a collection of models that can be used to describe a queryset. They nest into a single parent model that fully
describes the queryset, how to get it, and how to use it.

There is a collection of schemas in schemas.py that can be used to translate yaml configuration files into these python
configuration objects.
"""
import pathlib

import marshmallow as ma
from sqlalchemy import schema, types
import yaml

from query_tools.endpoints import EndpointSchema


class Field:
    """This object represents a column in the dataset

    Args:
        name: name of the field
        type: field type, one of: [Boolean, Date, DateTime, Float, Integer, Numeric, String, Text, Time]
        description: non-functional, short description of the field, can include notes about
        what the field is or how it's populated
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description', None)

    @property
    def column(self) -> schema.Column:
        """
        Returns: a sqlalchemy column with the attributes of this field
        """
        if self.type == 'Boolean':
            return schema.Column(self.name, types.Boolean)
        elif self.type == 'Date':
            return schema.Column(self.name, types.Date)
        elif self.type == 'DateTime':
            return schema.Column(self.name, types.DateTime)
        elif self.type == 'Float':
            return schema.Column(self.name, types.Float)
        elif self.type == 'Integer':
            return schema.Column(self.name, types.Integer)
        elif self.type == 'Numeric':
            return schema.Column(self.name, types.Numeric(18, 2))
        elif self.type == 'String':
            return schema.Column(self.name, types.String)
        elif self.type == 'Text':
            return schema.Column(self.name, types.Text)
        elif self.type == 'Time':
            return schema.Column(self.name, types.Time)

    def __repr__(self):
        return f'<Field(name={self.name})>'


class Queryset:
    """This object contains all of the information required to produce a dataset.

    Args:
        name: name of the dataset
        fit_for_use: describes the appropriate usage of the dataset
        endpoint: an endpoint object describing the source database
        fields: a collection of field objects describing the shape of the dataset
        definition: the sql that defines the dataset within the context of the endpoint
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.fit_for_use = kwargs.get('fit_for_use')
        self.endpoint = kwargs.get('endpoint')
        self.fields = kwargs.get('fields')
        self.definition = kwargs.get('definition')

    def __repr__(self):
        return f'<Queryset(name={self.name})>'


class FieldSchema(ma.Schema):
    """
    This schema allows the creation of an Field instance from a python dictionary of attributes. It is generally
    referenced indirectly as a component of a Queryset instance.
    """
    name = ma.fields.Str(required=True)
    description = ma.fields.Str(required=False)
    type = ma.fields.Str(required=True)

    @ma.post_load
    def make_query_field(self, data: dict):
        return Field(**data)


class QuerysetSchema(ma.Schema):
    """
    This schema allows the creation of an Queryset instance from a python dictionary of attributes.
    """
    name = ma.fields.Str(required=True)
    fit_for_use = ma.fields.Str(required=True)
    endpoint = ma.fields.Nested(EndpointSchema, required=True)
    fields = ma.fields.Nested(FieldSchema, required=True, many=True)
    definition = ma.fields.Str(required=True)

    def load_from_files(self, config_file: pathlib.Path, definition_file: pathlib.Path) -> dict:
        """This method contains boiler plate code to pull yaml from a file prior to loading into the schema, then
        passes the resulting dictionary to the marshmallow.Schema.load() function as usual

        Args:
            config_file: the configuration file for the Queryset
            definition_file: the sql file that contains the defining query, it's contents will get stuffed
            into the configuration dictionary prior to passing it to marshmallow.Schema.load()

        Returns: initially returns a validated dictionary, but ultimately returns a Queryset instance due to the
            marshmallow.post_load decorator on self.make_queryset()
        """
        config_yaml = config_file.read_text()
        config_dict = yaml.safe_load(config_yaml)
        config_dict['definition'] = definition_file.read_text()
        return self.load(config_dict)

    @ma.post_load
    def make_queryset(self, data: dict):
        return Queryset(**data)
