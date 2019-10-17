import pytest

from datarade.services.dataset_catalog import api
from datarade.domain import models
from . import auth

TFS_USERNAME = auth.TFS_USERNAME
TFS_PASSWORD = auth.TFS_PASSWORD
TFS_REPOSITORIES_URL = auth.TFS_REPOSITORIES_URL
TFS_REPOSITORY_ID = auth.TFS_REPOSITORY_ID

DB_HOST = auth.SOURCE_DB_HOST
DB_PORT = auth.SOURCE_DB_PORT
DB_NAME = auth.SOURCE_DB_NAME
DB_SCHEMA = auth.SOURCE_DB_SCHEMA


@pytest.fixture
def github_expected_dataset() -> models.Dataset:
    definition = '''select
    my_string_field,
    my_integer_field
from my_database.dbo.my_data
'''
    fields = [
        models.Field(name='my_string_field', type='String'),
        models.Field(name='my_integer_field', type='Integer')
    ]
    database = models.Database(driver='mssql',
                               host='my_host',
                               port=12345,
                               database_name='my_database',
                               schema_name='dbo')
    return models.Dataset(name='my_dataset',
                          definition=definition,
                          fields=fields,
                          description='A test dataset for datarade',
                          database=database)


@pytest.fixture
def git_tfs_expected_dataset() -> models.Dataset:
    definition = '''/*
Notes:
*/
SELECT DISTINCT s.name AS schema_name,
                t.name AS table_name,
                c.name AS column_name
FROM sys.schemas s
JOIN sys.tables t
    ON t.schema_id = s.schema_id
JOIN sys.columns c
    ON c.object_id = t.object_id
'''
    fields = [
        models.Field(name='schema_name', type='String'),
        models.Field(name='table_name', type='String'),
        models.Field(name='column_name', type='String')
    ]
    database = models.Database(driver='mssql',
                               host=DB_HOST,
                               port=DB_PORT,
                               database_name=DB_NAME,
                               schema_name=DB_SCHEMA)
    return models.Dataset(name='test_dataset',
                          definition=definition,
                          fields=fields,
                          description=None,
                          database=database)


def test_get_dataset_from_github_repo(github_expected_dataset):
    dataset_repository_url = 'https://raw.githubusercontent.com/mikealfare/dataset_catalog_test/master'
    dataset = api.get_dataset(dataset_name='my_dataset',
                              dataset_repository_url=dataset_repository_url,
                              dataset_catalog='catalog')
    assert isinstance(dataset, models.Dataset)
    assert dict(github_expected_dataset) == dict(dataset)


def test_get_dataset_from_git_tfs_repo(git_tfs_expected_dataset):
    dataset_repository_url = f'{TFS_REPOSITORIES_URL}/{TFS_REPOSITORY_ID}'
    dataset = api.get_dataset(dataset_name='test_dataset',
                              dataset_repository_url=dataset_repository_url,
                              dataset_catalog='catalog',
                              username=TFS_USERNAME,
                              password=TFS_PASSWORD)
    assert isinstance(dataset, models.Dataset)
    assert dict(git_tfs_expected_dataset) == dict(dataset)
