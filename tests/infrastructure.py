from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from tests.conftest import models


class TestSchema:

    def __init__(self, dataset_container: 'models.DatasetContainer'):
        self.name = dataset_container.metadata.schema
        self.database = dataset_container.database.database_name
        self.engine = dataset_container.metadata.bind

    def create(self):
        if self.schema_exists():
            self.drop()
        self.engine.execute(f'create schema {self.name}')

    def drop(self):
        for table in self.get_list_of_tables():
            self.drop_table(table[0])
        self.engine.execute(f'drop schema {self.name}')

    def get_list_of_tables(self) -> List[str]:
        list_of_tables_sql = f'''
            select t.name
            from sys.tables t
            join sys.schemas s
                on s.schema_id = t.schema_id
            where s.name = '{self.name}'
        '''
        list_of_tables = self.engine.execute(list_of_tables_sql).fetchall()
        return list_of_tables

    def drop_table(self, table_name: str):
        self.engine.execute(f'drop table {self.name}.{table_name}')

    def table_exists(self, table_name: str) -> bool:
        find_table_sql = f'''
            select t.name
            from sys.tables t
            join sys.schemas s
                on s.schema_id = t.schema_id
            where s.name = '{self.name}'
            and t.name = '{table_name}'
        '''
        table_exists = self.engine.execute(find_table_sql).fetchall()
        return table_exists != []

    def schema_exists(self) -> bool:
        find_schema_sql = f'''
            select s.name
            from sys.schemas s
            where s.name = '{self.name}'
        '''
        schema_exists = self.engine.execute(find_schema_sql).fetchall()
        return schema_exists != []

    def get_table_record_count(self, table_name: str) -> int:
        record_count_sql = f'select count(*) as record_count from {self.name}.{table_name}'
        table_record_count = self.engine.execute(record_count_sql).fetchone()
        return table_record_count.record_count

    def create_user(self, name: str, password: str):
        self.engine.execute(f"create login {name} with password=N'{password}', default_database=master")
        self.engine.execute(f'create user {name} for login {name}')
        self.engine.execute(f'grant select on schema :: {self.name} to {name}')

    def drop_user(self, name: str):
        self.engine.execute(f'drop user {name}')
        self.engine.execute(f'drop login {name}')
