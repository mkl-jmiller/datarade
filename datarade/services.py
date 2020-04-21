"""
These services allow a user to interact with datasets stored in a git-compliant source control repository. This layer
should be treated as the interface to this library. In other words, breaking changes may be introduced at lower levels,
but this layer should remain relatively stable as the library matures.
"""
from typing import Optional

from bcp import DataFile
import yaml

from datarade import models, schemas


def get_dataset_catalog(repository: str, organization: str, platform: str, project: str = None,
                        branch: 'Optional[str]' = 'master',
                        username: str = None, password: str = None) -> 'models.DatasetCatalog':
    """
    A factory function that provides a DatasetCatalog instance

    The structure of the files in the dataset catalog should look like this:

    .. code-block:: none

        repository
        |
        |--- catalog
            |
            |--- my_dataset
                |
                |--- config.yaml
                |--- definition.sql
            |--- my_other_dataset
                |
                |--- config.yaml
                |--- definition.sql

    The repository can be hosted on Git Hub or on Azure Repos. Multiple branches can be used for managing related
    dataset catalogs. For instance, you may want to maintain a uat branch and a production branch for managing
    environments. Or you may want one repo for all of your catalogs, but you want to provide some organization to
    your datasets.

    Args:
        repository: the name of the repository
        organization: the name of the organization (or user for GitHub) that owns the repository
        platform: that platform that hosts the repo ['github', 'azure-devops']
        project: the name of the project that contains the repository, only used for Azure Repos
        branch: the branch to use in the repository, defaults to 'master'
        username: the username with read access to the repository, only used for Azure Repos
        password: the password with read access to the repository, only used for Azure Repos, can also be the one-time
            git credentials password that bypasses MFA

    Returns: a DatasetCatalog instance
    """
    return models.DatasetCatalog(repository=repository, organization=organization, platform=platform,
                                 project=project, branch=branch, username=username, password=password)


def get_dataset_container(driver: str, database_name: str, host: str, port: int = None, schema_name: str = None,
                          username: str = None, password: str = None) -> 'models.DatasetContainer':
    """
    A factory function that provides a DatasetContainer instance

    Args:
        driver: the type of database, currently only 'mssql' is supported
        database_name: name of the database
        host: the name of the server, including the instance
        port: the port that the database is listening to on the server
        schema_name: the name of the schema
        username: a user with create table and insert permissions on the schema
        password: the password for the user

    Returns: a DatasetContainer instance
    """
    database = models.Database(driver=driver, database_name=database_name, host=host, port=port,
                               schema_name=schema_name)
    return models.DatasetContainer(database=database, username=username, password=password)


def get_dataset(dataset_catalog: 'models.DatasetCatalog', dataset_name: str) -> 'models.Dataset':
    """
    Returns a datarade Dataset object using the identified configuration in the dataset catalog

    It collects all of the required files from the dataset catalog repository, puts the contents in a configuration
    dictionary, passes that dictionary up to the abstract repository for validation, and returns the resulting Dataset
    instance.

    Args:
        dataset_catalog: dataset catalog that contains the dataset
        dataset_name: the name of the dataset, which is also the name of the directory containing the files in the
            repository

    Returns: a Dataset object
    """
    config_yaml = dataset_catalog.git.get_file_contents(f'catalog/{dataset_name}/config.yaml')
    definition = dataset_catalog.git.get_file_contents(f'catalog/{dataset_name}/definition.sql')
    dataset_dict = yaml.safe_load(config_yaml)
    dataset_dict['definition'] = definition
    dataset_schema = schemas.DatasetSchema()
    return dataset_schema.load(dataset_dict)


def write_dataset(dataset: 'models.Dataset', dataset_container: 'models.DatasetContainer',
                  username: str = None, password: str = None):
    """
    Writes the supplied dataset to the dataset container

    The supplied dataset is exported using the provided credentials. If no credentials are supplied, Windows AD is
    used for the account running this script. Data is written out to ~/bcp/data and logs are written out to ~/bcp/logs.
    Data is then imported into the supplied dataset container using credentials in that dataset container. Again, if no
    credentials were supplied, Windows AD is used. Error records are written out to ~/bcp/data and logs are written out
    to ~/bcp/logs. On a successful write, the data file is deleted to avoid leaving copies of data behind on the
    application machine.

    Args:
        dataset: the dataset to be written
        dataset_container: the database to store the dataset in
        username: a user with select/execute permissions on the source database objects
        password: the password for the user
    """
    dataset_container.create_table(dataset=dataset)
    if username is None and dataset.user is not None:
        username = dataset.user.username
    data_file = DataFile(delimiter='|~|')
    source_bcp = dataset.database.bcp(username=username, password=password)
    source_bcp.dump(query=dataset.definition, output_file=data_file)
    dataset_container.bcp.load(input_file=data_file, table=dataset_container.database.full_table_name(dataset.name))
    data_file.file.unlink()
