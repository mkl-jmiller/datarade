from typing import TYPE_CHECKING

from datarade import abstract_repositories
from datarade.services.dataset_catalog import unit_of_work, message_bus

if TYPE_CHECKING:
    from datarade.domain import models


class FakeRepository(abstract_repositories.AbstractDatasetRepository):

    def __init__(self, datasets: list):
        super().__init__()
        self._datasets = set(datasets)

    def _get(self, dataset_name: str, dataset_repository_url: str, dataset_catalog: str, username: str = None,
             password: str = None) -> 'models.Dataset':
        return next((d for d in self._datasets if d.name == dataset_name), None)

    def _add(self, dataset: 'models.Dataset'):
        self._datasets.add(dataset)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        self.init_repositories(FakeRepository([]))

    def rollback(self):
        pass

    def _commit(self):
        pass


class FakeBus(message_bus.MessageBus):

    def __init__(self):
        super().__init__(uow=FakeUnitOfWork())
