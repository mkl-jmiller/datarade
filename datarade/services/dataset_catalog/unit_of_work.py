"""
This is the unit of work for the Dataset Catalog service. It is politely borrowed almost whole cloth from the book
linked below.

Original Source: https://github.com/python-leap/code/blob/master/src/allocation/unit_of_work.py

Since the Dataset Catalog service is read-only, there is currently no reason to implement commit or rollback. This will
change in the future as things like logging and monitoring are added.
"""
import abc
from typing import TYPE_CHECKING

from datarade import repositories

if TYPE_CHECKING:
    from datarade.services.dataset_catalog import message_bus
    from datarade import abstract_repositories


class AbstractUnitOfWork(abc.ABC):

    _datasets = None
    bus = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()
        self.publish_events()

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def set_bus(self, bus: 'message_bus.MessageBus'):
        self.bus = bus

    def init_repositories(self, datasets: 'abstract_repositories.AbstractDatasetRepository'):
        self._datasets = datasets

    @property
    def datasets(self) -> 'abstract_repositories.AbstractDatasetRepository':
        return self._datasets

    def publish_events(self):
        for dataset in self.datasets.seen:
            while dataset.events:
                event = dataset.events.pop(0)
                self.bus.handle(event)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError


class GitUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.init_repositories(datasets=repositories.GitDatasetRepository())

    def rollback(self):
        pass

    def _commit(self):
        pass
