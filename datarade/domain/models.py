"""
This module contains all domain models for this application. There are currently four models:

Field:
This can be thought of as a field in a table or view.

Database:
This can be thought of as a collection of tables. For MS SQL Server, this goes down to the schema level, which makes
the name a bit misleading. For other database management systems, it would be very similar to a database.

Dataset:
This can be thought of as a view. It's a definition of a table of data without the actual data.

Dataset Container:
This is the combination of a Database object and a Dataset Catalog. It establishes a connection between the two to
facilitate the movement of data defined in the Dataset Catalog into the Database.
"""
from dataclasses import dataclass
from typing import List, Set

from datarade.domain import commands, exceptions


@dataclass(frozen=True)
class Field:
    """
    This object represents a column in the dataset

    Args:
        name: name of the field
        type: field type, one of: [Boolean, Date, DateTime, Float, Integer, Numeric, String, Text, Time]
        description: non-functional, short description of the field, can include notes about
        what the field is or how it's populated
    """
    name: str
    type: str
    description: str = None

    def __iter__(self):
        yield 'name', self.name
        yield 'type', self.type
        yield 'description', self.description


@dataclass(frozen=True)
class Database:
    """
    This object represents a database

    Args:
        driver: the type of database, currently only mssql is supported
        database_name: the name of the database
        host: the name of the server
        port: the port for the server
        schema_name: the name of the schema for a MS SQL Server database
    """
    driver: str
    database_name: str
    host: str
    port: int = None
    schema_name: str = None

    def __iter__(self):
        yield 'driver', self.driver
        yield 'database_name', self.database_name
        yield 'host', self.host
        yield 'port', self.port
        yield 'schema_name', self.schema_name


class Dataset:
    """
    This object represents a collection of dataset metadata

    Args:
        name: a unique identifier provided by the user
        definition: the sql defining the dataset
        fields: a list of field objects in the dataset
        description: non-functional, short description of the dataset, can include notes about
        what the dataset is or how it's populated
        database: a database object that contains the data for the dataset
    """
    def __init__(self, name: str, definition: str, fields: List[Field], description: str = None,
                 database: Database = None):
        self.name = name
        self.definition = definition
        self.fields = fields
        self.description = description
        self.database = database
        self.events = []

    def __iter__(self):
        yield 'name', self.name
        yield 'definition', self.definition
        yield 'fields', [dict(field) for field in self.fields]
        yield 'description', self.description
        yield 'database', dict(self.database)


class DatasetContainer:
    """
    This object represents a collection of dataset metadata

    Args:
        dataset_container_id: a unique identifier provided to the user
        dataset_repository_url: the url to the git repo containing the dataset catalog
        dataset_catalog: the name of the directory within the git repo containing the particular catalog
        driver: the type of database, currently only mssql is supported
        database_name: the name of the database
        host: the name of the server
        port: the port for the server
        schema_name: the name of the schema for a MS SQL Server database
    """
    def __init__(self, dataset_container_id: str, dataset_repository_url: str, dataset_catalog: str, driver: str,
                 database_name: str, host: str, port: int = None, schema_name: str = None):
        self.dataset_container_id = dataset_container_id
        self.dataset_repository_url = dataset_repository_url
        self.dataset_catalog = dataset_catalog
        self.database = Database(driver=driver,
                                 database_name=database_name,
                                 host=host,
                                 port=port,
                                 schema_name=schema_name)
        self._datasets: Set[Dataset] = set()
        self.events = []

    def add_dataset(self, dataset: Dataset):
        """
        Adds a dataset to the collection of datasets in this dataset container. It will raise an error if the
        dataset already exists in this container.

        Args:
            dataset: the dataset object to be added to the container
        """
        existing_dataset = next((d for d in self._datasets if d.name == dataset.name), None)
        if existing_dataset:
            raise exceptions.DatasetAlreadyExists
        self._datasets.add(dataset)

    def refresh_dataset(self, dataset_name: str,
                        username: str = None,
                        password: str = None):
        """
        Reloads the supplied dataset using the provided credentials. If no credentials are supplied, Windows AD is
        used for the account running this script. The dataset needs to already be associated with this container. An
        error is raised if this is not the case.

        Args:
            dataset_name: the name of the dataset to be relaaded
            username: the username to used for authentication on both the source and target databases
            password: the password to used for authentication on both the source and target databases
        """
        dataset = next((d for d in self._datasets if d.name == dataset_name), None)
        if dataset is None:
            raise exceptions.DatasetDoesNotExist
        source_database = dataset.database
        target_database = self.database
        cmd = commands.WriteDatasetFromDatabaseToDatabase(source_database=source_database,
                                                          target_database=target_database,
                                                          dataset=dataset,
                                                          fields=dataset.fields,
                                                          table_name=self.get_full_table_name(dataset.name),
                                                          username=username,
                                                          password=password)
        self.events.append(cmd)

    def get_full_table_name(self, table_name: str) -> str:
        """
        This is a helper method that is needed for MS SQL Server databases that have schemas.

        Args:
            table_name: the one part name of the table

        Returns: the three part name of the table, if the schema is present (MS SQL Server)
        """
        if self.database.schema_name is not None:
            return f'{self.database.database_name}.{self.database.schema_name}.{table_name}'
        else:
            return table_name
