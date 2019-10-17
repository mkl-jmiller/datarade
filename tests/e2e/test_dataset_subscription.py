from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL

from datarade.services.dataset_subscription import api
from ..conftest import TestSchema
from . import auth

TFS_USERNAME = auth.TFS_USERNAME
TFS_PASSWORD = auth.TFS_PASSWORD
TFS_REPOSITORIES_URL = auth.TFS_REPOSITORIES_URL
TFS_REPOSITORY_ID = auth.TFS_REPOSITORY_ID

DB_HOST = auth.TARGET_DB_HOST
DB_PORT = auth.TARGET_DB_PORT
DB_NAME = auth.TARGET_DB_NAME
DB_SCHEMA = 'pytest'

DB_ENGINE = create_engine(URL(drivername='mssql+pymssql', host=DB_HOST, port=DB_PORT, database=DB_NAME))


class TestDatasetSubscription:

    schema = TestSchema(name=DB_SCHEMA, engine=DB_ENGINE)

    def setup_method(self):
        self.schema.create()

    def teardown_method(self):
        self.schema.drop()

    def test_refresh_dataset_from_git_tfs(self):
        dataset_name = 'test_dataset'
        dataset_repository_url = f'{TFS_REPOSITORIES_URL}/{TFS_REPOSITORY_ID}'
        api.register_dataset_container(dataset_container_id='test',
                                       dataset_repository_url=dataset_repository_url,
                                       dataset_catalog='catalog',
                                       driver='mssql',
                                       database_name=DB_NAME,
                                       host=DB_HOST,
                                       port=DB_PORT,
                                       schema_name=DB_SCHEMA
                                       )
        assert not self.schema.table_exists(dataset_name)
        api.add_dataset(dataset_container_id='test',
                        dataset_name=dataset_name,
                        dataset_username=TFS_USERNAME,
                        dataset_password=TFS_PASSWORD)
        assert not self.schema.table_exists(dataset_name)
        api.refresh_dataset(dataset_container_id='test', dataset_name=dataset_name)
        assert self.schema.table_exists(dataset_name)
