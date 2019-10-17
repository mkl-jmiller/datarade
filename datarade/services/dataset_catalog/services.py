from typing import TYPE_CHECKING

from datarade.domain import events

if TYPE_CHECKING:
    from datarade.services.dataset_catalog import unit_of_work
    from datarade.domain import models


def get_dataset(dataset_name: str,
                dataset_repository_url: str,
                dataset_catalog: str,
                username: str,
                password: str,
                uow: 'unit_of_work.AbstractUnitOfWork') -> 'models.Dataset':
    """
    This will obtain the requested dataset and return it as an object. If username and password are not provided, it
    is assumed that the repo is public to the machine (no auth is passed into the request).

    Args:
        dataset_name: the name of the dataset in the dataset catalog
        dataset_repository_url: the url to the git repo containing the dataset catalog
        dataset_catalog: the directory within the git repo that contains the dataset
        username: the username to use for authentication
        password: the password to use for authentication
        uow: the unit of work to use to process the request

    Returns: a Dataset object
    """
    with uow:
        dataset = uow.datasets.get(dataset_name=dataset_name,
                                   dataset_repository_url=dataset_repository_url,
                                   dataset_catalog=dataset_catalog,
                                   username=username,
                                   password=password)
        if dataset is not None:
            dataset.events.append(events.DatasetRequested(dataset_name=dataset_name,
                                                          dataset_repository_url=dataset_repository_url,
                                                          dataset_catalog=dataset_catalog))
    return dataset
