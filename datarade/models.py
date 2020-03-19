"""
This module contains all models for datarade.
"""
from typing import List
from urllib.parse import quote_plus

from bcp import BCP, Connection
from sqlalchemy import MetaData, create_engine, schema, types, Table

from datarade import git_client


class DatasetCatalogNotSupportedException(Exception):
    """Occurs when an invalid platform is supplied to a DatasetCatalog instance."""
    print('Supported platforms include: github, azure-devops')


class DriverNotSupportedException(Exception):
    """Occurs when an invalid driver is supplied to a Database instance."""
    print('Supported drivers include: mssql')


class Field:
    """
    Represents a column in a dataset

    Args:
        name: name of the field
        type: field type, one of: [Boolean, Date, DateTime, Time, Float, Integer, Numeric, String, Text]
        description: non-functional, short description of the field, can include notes about
            what the field is or how it's populated
    """
    def __init__(self, name: str, type: str, description: str = None):
        self.name = name
        self.type = type
        self.description = description

    @property
    def sqlalchemy_column(self) -> 'schema.Column':
        """
        Converts a datarade Field object into a sqlalchemy Column object

        Returns: a sqlalchemy Column object
        """
        type_lookup = {
            'Boolean': types.Boolean,
            'Date': types.Date,
            'DateTime': types.DateTime,
            'Time': types.Time,
            'Float': types.Float,
            'Integer': types.Integer,
            'Numeric': types.Numeric(18, 2),
            'String': types.String,
            'Text': types.Text,
        }
        try:
            return schema.Column(self.name, type_lookup[self.type], comment=self.description)
        except KeyError as e:
            print(f'Not a valid column type: {self.type}')
            raise e


class Database:
    """
    Represents a database, either as a source for a Dataset, or as a target in a DatasetContainer

    Args:
        driver: the type of database, currently only 'mssql' is supported
        database_name: the name of the database
        host: the name of the server, including the instance
        port: the port that the database is listening to on the server
        schema_name: the name of the schema
    """
    def __init__(self, driver: str, database_name: str, host: str, port: int = None, schema_name: str = None):
        self.driver = driver
        self.database_name = database_name
        self.host = host
        self.port = port
        self.schema_name = schema_name

    def sqlalchemy_metadata(self, username: str = None, password: str = None) -> 'MetaData':
        """
        Takes credentials and returns a sqlalchemy MetaData object for this database

        Args:
            username: the username for the database
            password: the password for the database

        Returns: a sqlalchemy MetaData object
        """
        driver = '{' + self._odbc_driver_name + '}'
        if self.port:
            server = f'{self.host}:{self.port}'
        else:
            server = self.host
        base_url = f'DRIVER={driver};SERVER={server};DATABASE={self.database_name};'
        if username and password:
            auth = f'UID={username};PWD={password}'
        else:
            auth = 'Trusted_Connection=Yes'
        url = base_url + auth
        try:
            engine = create_engine(f'{self._sqlalchemy_driver_name}:///?odbc_connect={quote_plus(url)}')
        except Exception as e:
            print(f'Unable to create an engine using these parameters: {quote_plus(url)}')
            raise e
        if self.schema_name is not None:  # sqlalchemy treats schema=None and not returning schema differently
            return MetaData(bind=engine, schema=self.schema_name)
        else:
            return MetaData(bind=engine)

    def bcp(self, username: str = None, password: str = None) -> 'BCP':
        """
        Takes credentials and returns a BCP object for this database

        Args:
            username: the username for the database
            password: the password for the database

        Returns: a BCP object
        """
        conn = Connection(driver=self.driver,
                          host=self.host,
                          port=self.port,
                          username=username,
                          password=password)
        return BCP(conn)

    def full_table_name(self, table_name: str) -> str:
        """
        A utility method that is needed for MS SQL Server databases which have schemas

        Args:
            table_name: the one part name of the table

        Returns: the three part name of the table, if the schema is present
        """
        if self.schema_name is not None:
            return f'{self.database_name}.{self.schema_name}.{table_name}'
        else:
            return table_name

    @property
    def _sqlalchemy_driver_name(self) -> str:
        """
        Selects the sqlalchemy package to use given the database driver

        Returns: the sqlalchemy driver in '<database driver>+<sqlalchemy package>' format
        """
        if self.driver == 'mssql':
            return 'mssql+pyodbc'
        else:
            print(f'This driver is not supported: {self.driver}')
            raise DriverNotSupportedException

    @property
    def _odbc_driver_name(self) -> str:
        """
        Finds the appropriate ODBC driver on the machine given the database driver

        Returns: the latest SQL Server Native Client for MS SQL Server databases
        """
        if self.driver == 'mssql':
            import pyodbc

            installed_drivers = pyodbc.drivers()
            sql_server_native_clients = [client
                                         for client in installed_drivers
                                         if 'SQL Server Native Client' in client]
            try:
                latest_client = sorted(sql_server_native_clients)[0]
            except IndexError as e:
                print('There is no version of the SQL Server Native Client driver installed.')
                raise e
            return latest_client
        else:
            print(f'This driver is not supported: {self.driver}')
            raise DriverNotSupportedException


class Dataset:
    """
    Represents a dataset as metadata

    Args:
        name: an identifier for the dataset that is unique within the DatasetCatalog
        definition: the sql defining the dataset
        fields: a list of Field objects in the dataset
        description: non-functional, short description of the dataset, can include notes about
            what the dataset is or how it's populated
        database: a Database object that contains the data for the dataset
    """
    def __init__(self, name: str, definition: str, fields: 'List[Field]', description: str = None,
                 database: 'Database' = None):
        self.name = name
        self.definition = definition
        self.fields = fields
        self.description = description
        self.database = database


class DatasetCatalog:
    """
    Represents a git repo that hosts datasets in a predetermined structure

    This can be thought of as a place to host datasets for data pipelines. But it can also be thought of as a place to
    advertise datasets to a broad audience since it only contains metadata and not the underlying data.

    Args:
        repository: the name of the repository
        organization: the name of the organization (or user for GitHub) that owns the repository
        platform: that platform that hosts the repo ['github', 'azure-devops']
        project: the name of the project that contains the repository, only used for Azure Repos
        branch: the branch to use in the repository
        username: the username with read access to the repository, only used for Azure Repos
        password: the password with read access to the repository, only used for Azure Repos, can also be the one-time
            git credentials password that bypasses MFA
    """
    def __init__(self, repository: str, organization: str, platform: str, project: str = None, branch: str = 'master',
                 username: str = None, password: str = None):
        self.repository = repository
        self.organization = organization
        self.project = project
        self.branch = branch
        self.username = username
        self.password = password
        self.git = self._get_git_client(platform=platform)

    def _get_git_client(self, platform: str) -> 'git_client.AbstractGitClient':
        """
        Configures the appropriate git client given the platform

        Args:
            platform: the source control platform, one of 'github' or 'azure-devops'

        Returns: the appropriate git client
        """
        if platform == 'github':
            return git_client.GitHubClient(repository=self.repository, organization=self.organization,
                                           branch=self.branch)
        elif platform == 'azure-devops':
            return git_client.AzureReposClient(repository=self.repository, organization=self.organization,
                                               project=self.project, branch=self.branch,
                                               username=self.username, password=self.password)
        else:
            raise DatasetCatalogNotSupportedException


class DatasetContainer:
    """
    Represents a target data repository that stores datasets, currently a database

    Args:
        database: the database to write datasets to
        username: a user with create table and insert permissions on the schema
        password: the password for the user
    """
    def __init__(self, database: 'Database', username: str = None, password: str = None):
        self.database = database
        self.metadata = self.database.sqlalchemy_metadata(username=username, password=password)
        self.bcp = self.database.bcp(username=username, password=password)

    def create_table(self, dataset: 'Dataset'):
        """
        Creates a table in the DatasetContainer with the correct attributes to store the data

        Args:
            dataset: the dataset to use as a blueprint for the table
        """
        field_args = [field.sqlalchemy_column for field in dataset.fields]
        table = Table(dataset.name, self.metadata, extend_existing=True, *field_args)
        table.drop(checkfirst=True)
        table.create()
