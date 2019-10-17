from typing import TYPE_CHECKING

from datarade import abstract_repositories
from datarade.services.dataset_subscription import unit_of_work

if TYPE_CHECKING:
    from datarade.domain import models


class FakeDatasetContainerRepository(abstract_repositories.AbstractDatasetContainerRepository):

    def __init__(self):
        super().__init__()
        self._dataset_containers = set()

    def _get(self, dataset_container_id: str) -> 'models.DatasetContainer':
        return next(db for db in self._dataset_containers if db.dataset_container_id == dataset_container_id)

    def _add(self, dataset_container: 'models.DatasetContainer'):
        self._dataset_containers.add(dataset_container)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        self.init_repositories(FakeDatasetContainerRepository())
