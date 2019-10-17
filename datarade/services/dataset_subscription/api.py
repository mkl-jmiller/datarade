"""
This is the datarade api to be used when this package is used as a python library.
"""
from datarade.services.dataset_subscription import unit_of_work, message_bus
from datarade.domain import commands

uow = unit_of_work.StatelessUnitOfWork()
bus = message_bus.MessageBus(uow=uow)
uow.set_bus(bus=bus)


def register_dataset_container(dataset_container_id: str,
                               dataset_repository_url: str,
                               dataset_catalog: str,
                               driver: str,
                               database_name: str,
                               host: str,
                               port: int = None,
                               schema_name: str = None) -> bool:
    """
    Use this to register a dataset container in-memory, to be referenced later. It associates a dataset catalog
    with a database.

    Args:
        dataset_container_id: a user provided unique identifier
        dataset_repository_url: the url to the git repo containing the dataset catalog
        dataset_catalog: the directory within the git repo containing the datasets
        driver: the type of database (currently only MS SQL Server is supported)
        database_name: the name of the database
        host: the name of the server
        port: the port for the server
        schema_name: the name of the schema for a MS SQL Server database
    """
    cmd = commands.CreateDatasetContainer(dataset_container_id=dataset_container_id,
                                          dataset_repository_url=dataset_repository_url,
                                          dataset_catalog=dataset_catalog,
                                          driver=driver,
                                          database_name=database_name,
                                          host=host,
                                          port=port,
                                          schema_name=schema_name)
    bus.handle(cmd)
    return True


def add_dataset(dataset_container_id: str,
                dataset_name: str,
                dataset_username: str = None,
                dataset_password: str = None) -> bool:
    """
    Use this to associate a particular dataset with a dataset container. It will obtain the dataset metadata from the
    dataset catalog and store it with the dataset container.

    Args:
        dataset_container_id: the unique identifier of the dataset container
        dataset_name: the name of the dataset in the dataset container's dataset catalog
        dataset_username: the username for the dataset catalog
        dataset_password: the password for the dataset catalog
    """
    cmd = commands.CreateDataset(dataset_container_id=dataset_container_id,
                                 dataset_name=dataset_name,
                                 username=dataset_username,
                                 password=dataset_password)
    bus.handle(cmd)
    return True


def refresh_dataset(dataset_container_id: str,
                    dataset_name: str,
                    dataset_container_username: str = None,
                    dataset_container_password: str = None) -> bool:
    """
    Use this to reload a particular dataset into a dataset container. The dataset must already be associated with the
    dataset container (via add_dataset()).

    Args:
        dataset_container_id: the unique identifier of the dataset container
        dataset_name: the name of the dataset in the dataset container's dataset catalog
        dataset_container_username: the username for both the source database and the target database
        dataset_container_password: the password for both the source database and the target database

    .. note:
        The same username and password are used for both the source database and the target database. This is done in an
        attempt to maintain data access traceability from source to target. In other words, we want to ensure that if an
        account was able to get data to the target, it's because it also had access to the source. This forces the user
        to explicitly grant access to the same account on both databases.
    """
    cmd = commands.RefreshDataset(dataset_container_id=dataset_container_id,
                                  dataset_name=dataset_name,
                                  username=dataset_container_username,
                                  password=dataset_container_password)
    bus.handle(cmd)
    return True
