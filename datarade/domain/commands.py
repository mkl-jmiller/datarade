"""
This module contains the domain commands that occur throughout processing requests.
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from datarade.domain import models


class Command:
    pass


@dataclass(frozen=True)
class CreateDatasetContainer(Command):
    """
    This command results from the service layer or api layer requesting a new dataset container.
    """
    dataset_container_id: str
    dataset_repository_url: str
    dataset_catalog: str
    driver: str
    database_name: str
    host: str
    port: int = None
    schema_name: str = None


@dataclass(frozen=True)
class CreateDataset(Command):
    """
    This command results from the service layer or api layer associating a dataset with a dataset container.
    """
    dataset_container_id: str
    dataset_name: str
    username: str = field(default=None, repr=False)
    password: str = field(default=None, repr=False)


@dataclass(frozen=True)
class RefreshDataset(Command):
    """
    This command results from the service layer or api layer requesting a data reload for a dataset into a dataset
    container.
    """
    dataset_container_id: str
    dataset_name: str
    username: str = field(default=None, repr=False)
    password: str = field(default=None, repr=False)


@dataclass(frozen=True)
class WriteDatasetFromDatabaseToDatabase(Command):
    """
    This command results from the domain layer processing a RefreshDataset request.
    """
    source_database: 'models.Database'
    target_database: 'models.Database'
    dataset: 'models.Dataset'
    table_name: str
    fields: 'List[models.Field]'
    username: str = field(default=None, repr=False)
    password: str = field(default=None, repr=False)
