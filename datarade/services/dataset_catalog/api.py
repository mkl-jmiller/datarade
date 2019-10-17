"""
This is the datarade api to be used when this package is used as a python library. It currently has read functionality.
"""
from typing import TYPE_CHECKING

from datarade.services.dataset_catalog import services, message_bus, unit_of_work

if TYPE_CHECKING:
    from datarade.domain import models

uow = unit_of_work.GitUnitOfWork()
bus = message_bus.MessageBus(uow=uow)
uow.set_bus(bus=bus)


def get_dataset(dataset_name: str, dataset_repository_url: str, dataset_catalog: str, username: str = None,
                password: str = None) -> 'models.Dataset':
    """
    This will get the identified dataset from the supplied dataset catalog. If no credentials are supplied, it is
    assumed that the git repo is public to the machine (no auth is passed in the request).

    Args:
        dataset_name: the name of the dataset in the dataset catalog
        dataset_repository_url: the url for the git repo containing the dataset catalog
        dataset_catalog: the directory within the git repo containing the dataset catalog
        username: the username for the git repo
        password: the password for the git repo

    Returns: a datarade Dataset object
    """
    return services.get_dataset(dataset_name=dataset_name,
                                dataset_repository_url=dataset_repository_url,
                                dataset_catalog=dataset_catalog,
                                username=username,
                                password=password,
                                uow=bus.uow)
