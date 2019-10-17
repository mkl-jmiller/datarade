from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT.absolute()))

from typing import List

from sqlalchemy.engine import Engine


class TestSchema:

    def __init__(self, name: str, engine: Engine):
        self.name = name
        self.engine = engine

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
