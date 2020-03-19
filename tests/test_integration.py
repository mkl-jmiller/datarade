from tests.conftest import services, schemas
from tests.infrastructure import TestSchema

ORGANIZATION = 'fivestack'
PROJECT = 'FiveStack'
REPOSITORY = 'datarade_test_catalog'

# use the 'create git credentials' function on the clone screen of the test catalog repo to generate your credentials
AZURE_REPOS_REPOSITORY_USERNAME = ''
AZURE_REPOS_REPOSITORY_PASSWORD = ''

test_database_config = {
    'driver': 'mssql',
    'database_name': 'datarade',
    'host': r'localhost\DATARADE',
    'schema_name': 'pytest',
}
test_dataset_container = services.get_dataset_container(**test_database_config)
test_schema = TestSchema(name=test_dataset_container.metadata.schema, dataset_container=test_dataset_container)


def setup_function():
    test_schema.create()


def teardown_function():
    test_schema.drop()


def test_get_dataset_from_github():
    dataset_catalog = services.get_dataset_catalog(repository=REPOSITORY, organization=ORGANIZATION, platform='github')
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name='my_github_dataset')
    assert dataset.database.database_name == 'my_github_database'


def test_get_dataset_from_github_branch():
    dataset_catalog = services.get_dataset_catalog(repository=REPOSITORY, organization=ORGANIZATION, platform='github',
                                                   branch='integration')
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name='my_github_dataset')
    assert dataset.database.database_name == 'my_github_integration_database'


def test_get_dataset_from_azure_repos():
    dataset_catalog = services.get_dataset_catalog(repository=REPOSITORY, organization=ORGANIZATION,
                                                   platform='azure-devops', project=PROJECT,
                                                   username=AZURE_REPOS_REPOSITORY_USERNAME,
                                                   password=AZURE_REPOS_REPOSITORY_PASSWORD)
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name='my_azure_repos_dataset')
    assert dataset.database.database_name == 'my_azure_repos_database'


def test_get_dataset_from_azure_repos_branch():
    dataset_catalog = services.get_dataset_catalog(repository=REPOSITORY, organization=ORGANIZATION,
                                                   platform='azure-devops', project=PROJECT, branch='integration',
                                                   username=AZURE_REPOS_REPOSITORY_USERNAME,
                                                   password=AZURE_REPOS_REPOSITORY_PASSWORD)
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name='my_azure_repos_dataset')
    assert dataset.database.database_name == 'my_azure_repos_integration_database'


def test_write_dataset_to_sql_server():
    table_name = 'my_fake_dataset'
    fake_dataset_config = {
        'name': table_name,
        'definition': '''
            select
                s.name as schema_name,
                t.name as table_name
            from sys.schemas s
            join sys.tables t
                on t.schema_id = s.schema_id 
            ''',
        'fields': [
            {'name': 'schema_name', 'type': 'String'},
            {'name': 'table_name', 'type': 'String'},
        ],
        'database': test_database_config,
    }
    fake_dataset = schemas.DatasetSchema().load(fake_dataset_config)
    assert not test_schema.table_exists(table_name=table_name)
    services.write_dataset(dataset=fake_dataset, dataset_container=test_dataset_container)
    assert test_schema.table_exists(table_name=table_name)
    assert test_schema.get_table_record_count(table_name=table_name) > 0
