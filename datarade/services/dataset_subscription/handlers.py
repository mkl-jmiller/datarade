"""
This module contains all of the handlers for the Dataset Subscription service. It provides methods to associate
datasets with dataset containers and materialize said datasets into dataset containers.
"""
from typing import TYPE_CHECKING

from bcp import DataFile
from sqlalchemy import Table

from datarade.services.dataset_catalog.api import get_dataset

from datarade.domain import models
from datarade.services.dataset_subscription import utils

if TYPE_CHECKING:
    from datarade.services.dataset_subscription import unit_of_work
    from datarade.domain import commands


def create_dataset_container(cmd: 'commands.CreateDatasetContainer', uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    This will register a dataset container object in this application

    Args:
        cmd: parameters required to register a dataset container object
        uow: the implementation required to register the dataset container object
    """
    with uow:
        new_dataset_container = models.DatasetContainer(dataset_container_id=cmd.dataset_container_id,
                                                        dataset_repository_url=cmd.dataset_repository_url,
                                                        dataset_catalog=cmd.dataset_catalog,
                                                        driver=cmd.driver,
                                                        database_name=cmd.database_name,
                                                        host=cmd.host,
                                                        port=cmd.port,
                                                        schema_name=cmd.schema_name)
        uow.dataset_containers.add(new_dataset_container)
        uow.commit()


def add_dataset(cmd: 'commands.CreateDataset', uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    This will associate a dataset with a dataset container

    Args:
        cmd: parameters required to associate a dataset to a dataset container
        uow: the implementation required to associate the dataset to the dataset container
    """
    with uow:
        dataset_container = uow.dataset_containers.get(cmd.dataset_container_id)
        dataset = get_dataset(dataset_name=cmd.dataset_name,
                              dataset_repository_url=dataset_container.dataset_repository_url,
                              dataset_catalog=dataset_container.dataset_catalog,
                              username=cmd.username,
                              password=cmd.password)
        dataset_container.add_dataset(dataset)
        uow.commit()


def refresh_dataset(cmd: 'commands.RefreshDataset', uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    This will trigger a refresh of a dataset in a dataset container

    Args:
        cmd: parameters required to refresh a dataset
        uow: the implementation required to refresh a dataset
    """
    with uow:
        dataset_container = uow.dataset_containers.get(cmd.dataset_container_id)
        dataset_container.refresh_dataset(dataset_name=cmd.dataset_name,
                                          username=cmd.username,
                                          password=cmd.password)
        uow.commit()


def write_dataset_from_database_to_database(cmd: 'commands.WriteDatasetFromDatabaseToDatabase',
                                            uow: 'unit_of_work.AbstractUnitOfWork'):
    """
    This will execute a refresh of a dataset in a dataset container

    Args:
        cmd: parameters required to refresh a dataset
        uow: the implementation required to refresh a dataset
    """
    with uow:
        metadata = utils.get_sqlalchemy_metadata(database=cmd.target_database,
                                                 username=cmd.username,
                                                 password=cmd.password)
        field_args = [utils.get_sqlalchemy_column(field) for field in cmd.fields]
        table = Table(cmd.table_name.split('.')[-1], metadata, extend_existing=True, *field_args)
        table.drop(checkfirst=True)
        table.create()
        data_file = DataFile(delimiter='|~|')
        dataset = cmd.dataset
        source_bcp = utils.get_bcp(database=cmd.source_database,
                                   username=cmd.username,
                                   password=cmd.password)
        source_bcp.dump(query=dataset.definition, output_file=data_file)
        target_bcp = utils.get_bcp(database=cmd.target_database,
                                   username=cmd.username,
                                   password=cmd.password)
        target_bcp.load(input_file=data_file, table=cmd.table_name)
        data_file.file.unlink()
        uow.commit()
