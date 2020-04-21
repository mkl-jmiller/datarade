import pytest

from tests.conftest import services, schemas
from tests.infrastructure import TestSchema

ORGANIZATION = 'fivestack'
PROJECT = 'FiveStack'
REPOSITORY = 'datarade_test_catalog'

# use the 'create git credentials' function on the clone screen of the test catalog repo to generate your credentials
AZURE_REPOS_REPOSITORY_USERNAME = ''
AZURE_REPOS_REPOSITORY_PASSWORD = ''

# setup creates this user with select permissions on the test schema
DB_READ_USERNAME = 'pytest_user'
DB_READ_PASSWORD = 'admin'

test_database_config = {
    'driver': 'mssql',
    'database_name': 'datarade',
    'host': r'localhost\DATARADE',
    'schema_name': 'pytest',
}


github_default_branch = {
    'dataset_catalog': {'repository': REPOSITORY, 'organization': ORGANIZATION, 'platform': 'github'},
    'dataset': {'name': 'my_github_dataset', 'database': 'my_github_database'}
}
github_named_branch = github_default_branch.copy()
github_named_branch['dataset_catalog']['branch'] = 'integration'
github_named_branch['dataset']['database'] = 'my_github_integration_database'
azure_repos_default_branch = {
    'dataset_catalog': {'repository': REPOSITORY, 'organization': ORGANIZATION, 'platform': 'azure-devops',
                        'project': PROJECT,
                        'username': AZURE_REPOS_REPOSITORY_USERNAME, 'password': AZURE_REPOS_REPOSITORY_PASSWORD},
    'dataset': {'name': 'my_azure_repos_dataset', 'database': 'my_azure_repos_database'}
}
azure_repos_named_branch = azure_repos_default_branch.copy()
azure_repos_named_branch['dataset_catalog']['branch'] = 'integration'
azure_repos_named_branch['dataset']['database'] = 'my_azure_repos_integration_database'


@pytest.mark.parametrize('dataset_config', [
    github_default_branch, github_named_branch, azure_repos_default_branch, azure_repos_named_branch])
def test_get_dataset_from_dataset_catalog(dataset_config: dict):
    dataset_catalog = services.get_dataset_catalog(**dataset_config['dataset_catalog'])
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name=dataset_config['dataset']['name'])
    assert dataset.database.database_name == dataset_config['dataset']['database']


def test_get_dataset_with_user():
    dataset_config = github_named_branch.copy()
    dataset_config['dataset'] = {'name': 'my_github_dataset_with_user', 'user': 'pytest_user'}
    dataset_catalog = services.get_dataset_catalog(**dataset_config['dataset_catalog'])
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name=dataset_config['dataset']['name'])
    assert dataset.user.username == dataset_config['dataset']['user']



dataset_base = {
    'name': 'my_fake_dataset',
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
dataset_user = dataset_base.copy()
dataset_user['user'] = {'username': DB_READ_USERNAME}
dataset_user['password'] = DB_READ_PASSWORD


class TestSQLServer:

    dataset_container = services.get_dataset_container(**test_database_config)
    schema = TestSchema(dataset_container=dataset_container)

    def setup_method(self):
        self.schema.create()
        self.schema.create_user(name=DB_READ_USERNAME, password=DB_READ_PASSWORD)

    def teardown_method(self):
        self.schema.drop_user(name=DB_READ_USERNAME)
        self.schema.drop()

    @pytest.mark.parametrize('dataset_config', [dataset_base, dataset_user])
    def test_write_dataset(self, dataset_config: dict):
        table_name = dataset_config['name']
        password = dataset_config.pop('password', None)
        fake_dataset = schemas.DatasetSchema().load(dataset_config)
        assert not self.schema.table_exists(table_name=table_name)
        services.write_dataset(dataset=fake_dataset, dataset_container=self.dataset_container, password=password)
        assert self.schema.table_exists(table_name=table_name)
        assert self.schema.get_table_record_count(table_name=table_name) > 0
