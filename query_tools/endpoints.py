"""
This modules contains objects for creating database level connections.
"""
import pathlib

import yaml
import bcp
import marshmallow as ma
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL


class Endpoint:
    """This identifies the source database for the dataset

    Args:
        driver: type of database (e.g. mssql)
        host: name of the machine hosting the database
        port: port to connect through
        database: name of the database
        schema: name of the schema
    """
    def __init__(self, **kwargs):
        self.driver = kwargs.get('driver')
        self.host = kwargs.get('host')
        self.port = kwargs.get('port', None)
        self.database = kwargs.get('database')
        self.schema = kwargs.get('schema')

    def bcp_connection(self):
        """This method generates a bcp Connection using the endpoint attributes

        Returns: a bcp Connection object
        """
        driver = self.driver.split('+')[0]
        return bcp.Connection(host=f'{self.host},{self.port}', driver=driver)

    def engine(self) -> Engine:
        """This method generates a sqlalchemy Engine using the endpoint attributes

        Returns: a sqlalchemy Engine object
        """
        url = URL(drivername=self.driver, host=self.host, port=self.port, database=self.database)
        return create_engine(url)

    def metadata(self) -> MetaData:
        """This method generates a sqlalchemy MetaData instance using the endpoint attributes

        Returns: a sqlalchemy MetaData object
        """
        return MetaData(bind=self.engine, schema=self.schema)

    def __repr__(self):
        return f'<Endpoint(host={self.host})>'


class EndpointSchema(ma.Schema):
    """
    This schema allows the creation of an Endpoint instance from a python dictionary of attributes
    """
    driver = ma.fields.Str(required=True)
    host = ma.fields.Str(required=True)
    port = ma.fields.Int(required=False)
    database = ma.fields.Str(required=True)
    schema = ma.fields.Str(required=False)

    def load_from_files(self, config_file: pathlib.Path) -> dict:
        """This method contains boiler plate code to pull yaml from a file prior to loading into the schema, then
        passes the resulting dictionary to the marshmallow.Schema.load() function as usual

        Args:
            config_file: the configuration file for the Endpoint

        Returns: initially returns a validated dictionary, but ultimately returns an Endpoint instance due to the
            marshmallow.post_load decorator on self.make_endpoint()
        """
        config_yaml = config_file.read_text()
        config_dict = yaml.safe_load(config_yaml)
        return self.load(config_dict)

    @ma.post_load
    def make_endpoint(self, data: dict):
        return Endpoint(**data)
