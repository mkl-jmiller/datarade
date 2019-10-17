import abc
from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from datarade.domain import models


class AbstractDatasetRepository(abc.ABC):
    """
    This repository contains methods to get datasets and add datasets. At runtime, there is no way to add datasets to
    the concrete repository. It was added here to facilitate testing with the fake repository.
    """
    def __init__(self):
        self.seen: 'Set[models.Dataset]' = set()

    def get(self, dataset_name: str, dataset_repository_url: str, dataset_catalog: str, username: str = None,
            password: str = None) -> 'models.Dataset':
        d = self._get(dataset_name=dataset_name,
                      dataset_repository_url=dataset_repository_url,
                      dataset_catalog=dataset_catalog,
                      username=username,
                      password=password)
        if d:
            self.seen.add(d)
        return d

    def add(self, dataset: 'models.Dataset'):
        self._add(dataset)
        self.seen.add(dataset)

    @abc.abstractmethod
    def _get(self, dataset_name: str, dataset_repository_url: str, dataset_catalog: str, username: str = None,
             password: str = None) -> 'models.Dataset':
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, dataset: 'models.Dataset'):
        raise NotImplementedError


