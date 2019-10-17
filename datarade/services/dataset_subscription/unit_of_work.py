"""
This is the unit of work for the Dataset Subscription service. It is politely borrowed almost whole cloth from the book
linked below.

Original Source: https://github.com/python-leap/code/blob/master/src/allocation/unit_of_work.py
"""
import abc
from typing import TYPE_CHECKING

from datarade import repositories

if TYPE_CHECKING:
    from datarade.services.dataset_subscription import message_bus
    from datarade import abstract_repositories


class AbstractUnitOfWork(abc.ABC):

    _dataset_containers = None
    bus = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def commit(self):
        self._commit()
        self.publish_events()

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def set_bus(self, bus: 'message_bus.MessageBus'):
        self.bus = bus

    def init_repositories(self, dataset_containers: 'abstract_repositories.AbstractDatasetContainerRepository'):
        self._dataset_containers = dataset_containers

    @property
    def dataset_containers(self) -> 'abstract_repositories.AbstractDatasetContainerRepository':
        return self._dataset_containers

    def publish_events(self):
        for dataset_container in self.dataset_containers.seen:
            while dataset_container.events:
                event = dataset_container.events.pop(0)
                self.bus.handle(event)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError


class StatelessUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.init_repositories(dataset_containers=repositories.StatelessDatasetContainerRepository())

    def rollback(self):
        pass

    def _commit(self):
        pass
