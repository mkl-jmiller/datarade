"""
This module contains functionality that can turn Queryset instances into materialized tables in a target database.
"""
import pathlib

import bcp
import marshmallow as ma
import sqlalchemy
import yaml

from query_tools.config import FILE_SERVER
from query_tools.querysets import Queryset, QuerysetSchema
from query_tools.endpoints import Endpoint, EndpointSchema


class Dataset:
    """This class contains all of the functionality required to populate the results of a queryset
    into a dataset container

    Args:
        queryset: the full description of the dataset
        endpoint: the dataset container for the queryset results
        table_name: the name of the table in the dataset container
        schema_name: optional parameter for the schema in the dataset container
    """
    def __init__(self, queryset: Queryset, endpoint: Endpoint, table_name: str, schema_name: str = None):
        self.queryset = queryset
        self.endpoint = endpoint
        self.table_name = table_name
        engine = endpoint.engine()
        self.metadata = sqlalchemy.MetaData(engine, schema=schema_name)

    def refresh(self):
        """This method creates a table in the database and stores the dataset"""
        data_file = FILE_SERVER / pathlib.Path(f'{self.table_name}.dat')
        self._get_queryset_results(data_file)
        self._create_table()
        self._post_queryset_results(data_file)
        data_file.unlink()

    def _create_table(self):
        """This method creates a table in the dataset container to store the queryset results"""
        fields = self.queryset.fields
        field_args = [field.column for field in fields]
        table = sqlalchemy.schema.Table(self.table_name, self.metadata, extend_existing=True, *field_args)
        table.drop(checkfirst=True)
        table.create()

    def _get_full_table_name(self) -> str:
        """This method produces the three part name for mssql bcp"""
        database = self.endpoint.database
        schema = self.metadata.schema
        if database is not None and schema is not None:
            return f'{database}.{schema}.{self.table_name}'
        else:
            return self.table_name

    def _get_queryset_results(self, output_file: pathlib.Path):
        """This method exports the results of this queryset into the output file

        Args:
            output_file: the file that should be created with the query results
        """
        connection = self.queryset.endpoint.bcp_connection()
        export_bcp = bcp.BCP(connection)
        export_bcp.dump(self.queryset.definition, output_file)

    def _post_queryset_results(self, input_file: pathlib.Path):
        """This method imports the results of the queryset from the input file

        Args:
            input_file: the file that contains the query results
        """
        connection = self.endpoint.bcp_connection()
        import_bcp = bcp.BCP(connection)
        table = self._get_full_table_name()
        import_bcp.load(input_file, table)


class DatasetContainer:
    """This is a container for datasets. It facilitates the refresh of multiple tables into the same database/schema.

    Args:
        endpoint: an endpoint that identifies the target data store
        schema: if applicable, the schema within the target database
    """

    def __init__(self, endpoint: Endpoint, schema: str = None):
        self.endpoint = endpoint
        self.schema = schema

    def refresh_dataset(self, queryset: Queryset, table_name: str):
        """This method will refresh the table with the provided queryset definition

        Args:
            queryset: the queryset to be used to get the data
            table_name: the table where the data should be inserted
        """
        dataset = Dataset(queryset, self.endpoint, table_name, self.schema)
        dataset.refresh()

    def refresh_dataset_from_files(self, config_file: pathlib.Path, definition_file: pathlib.Path, table_name: str):
        """This method allows the queryset to be provided via files instead of objects

        Args:
            config_file: the config file for the queryset
            definition_file: the definition file for the queryset
            table_name: the table where the data should be inserted
        """

        config_yaml = config_file.read_text()
        config_dict = yaml.safe_load(config_yaml)
        config_dict['definition'] = definition_file.read_text()
        queryset_schema = QuerysetSchema()
        queryset, errors = queryset_schema.load(config_dict)
        self.refresh_dataset(queryset, table_name)


class DatasetContainerSchema(ma.Schema):
    """
    This schema allows the creation of an DatasetContainer instance from a python dictionary of attributes.
    """
    endpoint = ma.fields.Nested(EndpointSchema, required=True)
    schema = ma.fields.Str(required=True)

    def load_from_files(self, config_file: pathlib.Path) -> dict:
        """This method contains boiler plate code to pull yaml from a file prior to loading into the schema, then
        passes the resulting dictionary to the marshmallow.Schema.load() function as usual

        Args:
            config_file: the configuration file for the DatasetContainer

        Returns: initially returns a validated dictionary, but ultimately returns an DatasetContainer instance due to
            the marshmallow.post_load decorator on self.make_dataset_container()
        """
        config_yaml = config_file.read_text()
        config_dict = yaml.safe_load(config_yaml)
        return self.load(config_dict)

    @ma.post_load
    def make_dataset_container(self, data: dict):
        return DatasetContainer(**data)
