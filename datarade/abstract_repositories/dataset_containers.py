import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datarade.domain import models


class AbstractDatasetContainerRepository(abc.ABC):
    """
    This repository contains methods to get dataset containers and add dataset containers.
    """
    def __init__(self):
        self.seen = set()

    def get(self, dataset_container_id: str) -> 'models.DatasetContainer':
        obj = self._get(dataset_container_id=dataset_container_id)
        if obj:
            self.seen.add(obj)
        return obj

    def add(self, dataset_container: 'models.DatasetContainer'):
        self._add(dataset_container)
        self.seen.add(dataset_container)

    @abc.abstractmethod
    def _get(self, dataset_container_id: str) -> 'models.DatasetContainer':
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, dataset_container: 'models.DatasetContainer'):
        raise NotImplementedError
