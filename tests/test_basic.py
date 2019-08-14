import pathlib
import yaml
import pytest

from .context import endpoints, querysets, datasets, STATIC_FILES_DIR


test_schema = 'pytest'


def get_dict_from_file(file_name: str) -> dict:
    file_path = STATIC_FILES_DIR / pathlib.Path(f'{file_name}')
    file_yaml = file_path.read_text()
    file_dict = yaml.safe_load(file_yaml)
    return file_dict


def check_table_exists(engine, table_name) -> str:
    get_one_table_sql = f'''
        select t.name
        from sys.tables t
        join sys.schemas s
            on s.schema_id = t.schema_id
        where s.name = '{test_schema}'
        and t.name = '{table_name}'
    '''
    table = engine.execute(get_one_table_sql).fetchone()
    return table[0]


def create_test_schema(engine):
    engine.execute(f'create schema {test_schema}')


def drop_test_schema(engine):
    list_of_tables_sql = f'''
        select t.name
        from sys.tables t
        join sys.schemas s
            on s.schema_id = t.schema_id
        where s.name = '{test_schema}'
    '''
    tables = engine.execute(list_of_tables_sql).fetchall()
    for table in tables:
        table_name = table[0]
        drop_table_sql = f'drop table {test_schema}.{table_name}'
        engine.execute(drop_table_sql)
    engine.execute(f'drop schema {test_schema}')


@pytest.fixture
def endpoint_dict() -> dict:
    return get_dict_from_file('endpoint.yaml')


@pytest.fixture
def dataset_container_dict() -> dict:
    return get_dict_from_file('dataset_container.yaml')


def get_list_of_tables_queryset() -> querysets.Queryset:
    config_dict = get_dict_from_file('list_of_tables.yaml')
    sql_file = STATIC_FILES_DIR / pathlib.Path('list_of_tables.sql')
    config_dict['definition'] = sql_file.read_text()
    queryset_schema = querysets.QuerysetSchema()
    queryset, errors = queryset_schema.load(config_dict)
    return queryset


@pytest.fixture
def list_of_tables_queryset() -> querysets.Queryset:
    return get_list_of_tables_queryset()


@pytest.fixture
def list_of_tables_dataset() -> datasets.Dataset:
    list_of_tables_queryset = get_list_of_tables_queryset()
    dataset_endpoint = endpoints.Endpoint(driver='mssql+pymssql', host='host01', port=21612,
                                          database='SANDBOX')
    table_name = 'list_of_tables'
    dataset = datasets.Dataset(list_of_tables_queryset, dataset_endpoint, table_name, test_schema)
    return dataset


class TestEndpoint:

    endpoint = endpoints.Endpoint(driver='mssql', host='beta', port=1234, database='gamma', schema='delta')
    endpoint_schema = endpoints.EndpointSchema()

    def test_create_endpoint(self):
        assert 'mssql' == self.endpoint.driver
        assert 'beta' == self.endpoint.host
        assert 1234 == self.endpoint.port
        assert 'gamma' == self.endpoint.database
        assert '<Endpoint(host=beta)>' == f'{self.endpoint}'

    def test_endpoint_engine_creation(self):
        engine = self.endpoint.engine()
        assert 'pyodbc' == engine.driver

    def test_endpoint_metadata_creation(self):
        metadata = self.endpoint.metadata()
        assert 'delta' == metadata.schema

    def test_endpoint_bcp_connection_creation(self):
        bcp_connection = self.endpoint.bcp_connection()
        assert 'beta,1234' == bcp_connection.host

    def test_get_driver_from_endpoint_yaml(self, endpoint_dict):
        endpoint, errors = self.endpoint_schema.load(endpoint_dict)
        assert 'mssql' == endpoint.driver
        assert 'host01' == endpoint.host
        assert 21612 == endpoint.port
        assert 'DATABASE' == endpoint.database
        assert 'data' == endpoint.schema

    def test_create_endpoint_load_from_files(self):
        config_file = STATIC_FILES_DIR / pathlib.Path('endpoint.yaml')
        endpoint, errors = self.endpoint_schema.load_from_files(config_file)
        assert 'mssql' == endpoint.driver
        assert 'host01' == endpoint.host
        assert 21612 == endpoint.port
        assert 'DATABASE' == endpoint.database
        assert 'data' == endpoint.schema
        assert '<Endpoint(host=host01)>' == f'{endpoint}'


class TestQueryset:

    queryset_schema = querysets.QuerysetSchema()

    def test_create_field(self):
        field = querysets.Field(name='foo', type='bar')
        assert 'foo' == field.name
        assert 'bar' == field.type
        assert None is field.description
        assert '<Field(name=foo)>' == f'{field}'

    def test_create_queryset(self):
        name = 'my_name'
        fit_for_use = 'operational'
        my_endpoint = endpoints.Endpoint(driver='alpha', host='beta', database='gamma')
        field_1 = querysets.Field(name='foo', type='bar')
        field_2 = querysets.Field(name='alpha', type='omega')
        my_definition = 'select foo, alpha from my_table'
        queryset = querysets.Queryset(name=name, fit_for_use=fit_for_use, endpoint=my_endpoint,
                                      fields=[field_1, field_2], definition=my_definition)
        assert 'my_name' == queryset.name
        assert 'operational' == queryset.fit_for_use
        assert 'alpha' == queryset.endpoint.driver
        assert 2 == len(queryset.fields)
        assert 'my_table' in queryset.definition
        assert '<Queryset(name=my_name)>' == f'{queryset}'

    def test_create_queryset_from_files(self, list_of_tables_queryset):
        assert 'list_of_tables' == list_of_tables_queryset.name
        assert 'operational' == list_of_tables_queryset.fit_for_use
        assert 'mssql' == list_of_tables_queryset.endpoint.driver
        assert 2 == len(list_of_tables_queryset.fields)
        assert 'tables' in list_of_tables_queryset.definition
        assert '<Queryset(name=list_of_tables)>' == f'{list_of_tables_queryset}'

    def test_get_field_name_from_yaml(self, list_of_tables_queryset):
        fields = list_of_tables_queryset.fields
        actual = None
        for field in fields:
            if field.name == 'schema_name':
                actual = field.type
        expected = 'String'
        assert expected == actual

    def test_create_queryset_load_from_files(self):
        config_file = STATIC_FILES_DIR / pathlib.Path('list_of_tables.yaml')
        definition_file = STATIC_FILES_DIR / pathlib.Path('list_of_tables.sql')
        queryset, errors = self.queryset_schema.load_from_files(config_file, definition_file)
        assert 'list_of_tables' == queryset.name
        assert 'operational' == queryset.fit_for_use
        assert 'mssql' == queryset.endpoint.driver
        assert 2 == len(queryset.fields)
        assert 'tables' in queryset.definition
        assert '<Queryset(name=list_of_tables)>' == f'{queryset}'


class TestDataset:

    dataset_endpoint = endpoints.Endpoint(driver='mssql+pymssql', host='host01', port=21612,
                                          database='SANDBOX')
    dataset_engine = dataset_endpoint.engine()
    table_name = 'list_of_tables'

    def setup_method(self):
        create_test_schema(self.dataset_engine)

    def teardown_method(self):
        drop_test_schema(self.dataset_engine)

    def test_dataset_table_create(self, list_of_tables_dataset):
        list_of_tables_dataset._create_table()
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table

    def test_dataset_table_create_when_table_already_exists(self, list_of_tables_dataset):
        list_of_tables_dataset._create_table()
        list_of_tables_dataset._create_table()
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table

    def test_dataset_full_table_name(self, list_of_tables_dataset):
        actual = list_of_tables_dataset._get_full_table_name()
        expected = f'{list_of_tables_dataset.endpoint.database}.{test_schema}.{self.table_name}'
        assert expected == actual

    def test_dataset_full_table_name_no_schema(self, list_of_tables_queryset):
        dataset_no_schema = datasets.Dataset(list_of_tables_queryset, self.dataset_endpoint, self.table_name)
        actual = dataset_no_schema._get_full_table_name()
        expected = f'{self.table_name}'
        assert expected == actual

    def test_dataset_get_queryset_results(self, list_of_tables_dataset):
        output_file = pathlib.Path(__file__).parent / pathlib.Path('static_files/dataset_get_queryset_results.dat')
        list_of_tables_dataset._get_queryset_results(output_file)
        file_exists = output_file.exists()
        output_file.unlink()
        assert True is file_exists

    def test_dataset_post_queryset_results(self, list_of_tables_dataset):
        input_file = pathlib.Path(__file__).parent / pathlib.Path('static_files/list_of_tables.dat')
        list_of_tables_dataset._create_table()
        list_of_tables_dataset._post_queryset_results(input_file)
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert list_of_tables_dataset.table_name == created_table

    def test_dataset_refresh(self, list_of_tables_queryset):
        dataset = datasets.Dataset(queryset=list_of_tables_queryset, endpoint=self.dataset_endpoint,
                                   table_name=self.table_name, schema_name=test_schema)
        dataset.refresh()
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table

    def test_dataset_refresh_for_table_that_already_exists(self, list_of_tables_queryset):
        dataset = datasets.Dataset(queryset=list_of_tables_queryset, endpoint=self.dataset_endpoint,
                                   table_name=self.table_name, schema_name=test_schema)
        dataset.refresh()
        dataset.refresh()
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table


class TestDatasetContainer:

    dataset_endpoint = endpoints.Endpoint(driver='mssql+pymssql', host='host01', port=21644,
                                          database='SANDBOX')
    dataset_engine = dataset_endpoint.engine()
    table_name = 'list_of_tables'
    dataset_container = datasets.DatasetContainer(endpoint=dataset_endpoint, schema=test_schema)
    dataset_container_schema = datasets.DatasetContainerSchema()

    def setup_method(self):
        create_test_schema(self.dataset_engine)

    def teardown_method(self):
        drop_test_schema(self.dataset_engine)

    def test_create_dataset_container(self):
        dataset_container = datasets.DatasetContainer(self.dataset_endpoint, 'myschema')
        assert 'host01' == dataset_container.endpoint.host
        assert 'myschema' == dataset_container.schema

    def test_dataset_container_refresh_dataset(self, list_of_tables_queryset):
        self.dataset_container.refresh_dataset(list_of_tables_queryset, self.table_name)
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table

    def test_dataset_container_refresh_dataset_that_already_exists(self, list_of_tables_queryset):
        self.dataset_container.refresh_dataset(list_of_tables_queryset, self.table_name)
        self.dataset_container.refresh_dataset(list_of_tables_queryset, self.table_name)
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table

    def test_dataset_container_refresh_dataset_from_files(self):
        config_file = STATIC_FILES_DIR / pathlib.Path('list_of_tables.yaml')
        definition_file = STATIC_FILES_DIR / pathlib.Path('list_of_tables.sql')
        self.dataset_container.refresh_dataset_from_files(config_file, definition_file, self.table_name)
        created_table = check_table_exists(self.dataset_engine, self.table_name)
        assert self.table_name == created_table

    def test_get_dataset_container_from_yaml(self, dataset_container_dict):
        dataset_container, errors = self.dataset_container_schema.load(dataset_container_dict)
        assert 'mssql' == dataset_container.endpoint.driver
        assert 'my_server' == dataset_container.endpoint.host
        assert 12345 == dataset_container.endpoint.port
        assert 'my_database' == dataset_container.endpoint.database
        assert 'my_schema' == dataset_container.schema

    def test_create_queryset_load_from_files(self):
        config_file = STATIC_FILES_DIR / pathlib.Path('dataset_container.yaml')
        dataset_container, errors = self.dataset_container_schema.load_from_files(config_file)
        assert 'mssql' == dataset_container.endpoint.driver
        assert 'my_server' == dataset_container.endpoint.host
        assert 12345 == dataset_container.endpoint.port
        assert 'my_database' == dataset_container.endpoint.database
        assert 'my_schema' == dataset_container.schema
