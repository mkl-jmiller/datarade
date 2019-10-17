from typing import TYPE_CHECKING

from datarade import abstract_repositories, orm

if TYPE_CHECKING:
    from datarade.domain import models


class GitDatasetRepository(abstract_repositories.AbstractDatasetRepository):
    """
    This repository allows the user to store their datasets in a git-compliant source control repository. The structure
    should look like this:

    .. code-block:: none

        repository
        |
        |--- catalog
            |
            |--- my_dataset
                |
                |--- config.yaml
                |--- definition.sql
            |--- my_other_dataset
                |
                |--- config.yaml
                |--- definition.sql

    This repository can be connected to a repo on github or to a git-tfs on-prem repo.
    """
    def __init__(self):
        super().__init__()

    def _get(self, dataset_name: str, dataset_repository_url: str, dataset_catalog: str, username: str = None,
             password: str = None) -> 'models.Dataset':
        session = orm.GitSession(repository=dataset_repository_url,
                                 catalog=dataset_catalog,
                                 username=username,
                                 password=password)
        return session.get_dataset(dataset_name=dataset_name)

    def _add(self, dataset: 'models.Dataset'):
        pass
