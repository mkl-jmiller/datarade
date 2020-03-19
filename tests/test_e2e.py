from tests.conftest import services
from tests.infrastructure import TestSchema

test_dataset_catalog = services.get_dataset_catalog(
    repository='datarade_test_catalog',
    organization='fivestack',
    platform='github',
    branch='e2e'
)
test_dataset_container = services.get_dataset_container(
    driver='mssql',
    database_name='datarade',
    host=r'localhost\DATARADE',
    schema_name='e2e'
)

test_schema = TestSchema(name='e2e', dataset_container=test_dataset_container)


def setup_function():
    test_schema.create()


def teardown_function():
    test_schema.drop()


def test_write_dataset():
    dataset_name = 'list_of_tables'
    dataset = services.get_dataset(dataset_catalog=test_dataset_catalog, dataset_name=dataset_name)
    assert not test_schema.table_exists(table_name=dataset_name)
    services.write_dataset(dataset=dataset, dataset_container=test_dataset_container)
    assert test_schema.table_exists(table_name=dataset_name)
    assert test_schema.get_table_record_count(table_name=dataset_name) > 0
