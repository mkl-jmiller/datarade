from typing import TYPE_CHECKING

from datarade import abstract_repositories

if TYPE_CHECKING:
    from datarade.domain import models


class StatelessDatasetContainerRepository(abstract_repositories.AbstractDatasetContainerRepository):
    """
    This repository is an in-memory collection of dataset containers. It is used when directly importing this package.
    Saving dataset containers is not necessary when using this package as a library, so it functions very much like a
    fake repository. That is why there is no ORM hooked up to it.
    """
    def __init__(self):
        super().__init__()
        self._dataset_containers = set()

    def _get(self, dataset_container_id: str) -> 'models.DatasetContainer':
        return next(d for d in self._dataset_containers if d.dataset_container_id == dataset_container_id)

    def _add(self, dataset_container: 'models.DatasetContainer'):
        self._dataset_containers.add(dataset_container)
