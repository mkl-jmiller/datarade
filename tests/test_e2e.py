from tests.conftest import services
from tests.infrastructure import TestSchema

dataset_catalog = services.get_dataset_catalog(
    repository='datarade_test_catalog',
    organization='fivestack',
    platform='github',
    branch='e2e'
)
dataset_container = services.get_dataset_container(
    driver='mssql',
    database_name='datarade',
    host=r'localhost\DATARADE',
    schema_name='e2e'
)
schema = TestSchema(dataset_container=dataset_container)


def setup_function():
    schema.create()


def teardown_function():
    schema.drop()


def test_write_dataset():
    dataset_name = 'list_of_tables'
    dataset = services.get_dataset(dataset_catalog=dataset_catalog, dataset_name=dataset_name)
    assert not schema.table_exists(table_name=dataset_name)
    services.write_dataset(dataset=dataset, dataset_container=dataset_container)
    assert schema.table_exists(table_name=dataset_name)
    assert schema.get_table_record_count(table_name=dataset_name) > 0
