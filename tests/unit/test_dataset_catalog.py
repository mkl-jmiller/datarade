from datarade.services.dataset_catalog import services
from datarade.domain import models, events

from .fakes_dataset_catalog import FakeUnitOfWork

uow = FakeUnitOfWork()


def create_fake_dataset_by_name(dataset_name: str) -> models.Dataset:
    fake_str_field = models.Field(name=f'{dataset_name}_string', type='String')
    fake_int_field = models.Field(name=f'{dataset_name}_integer', type='Integer')
    fake_dataset = models.Dataset(name=dataset_name,
                                  definition='select * from table',
                                  fields=[fake_str_field, fake_int_field])
    return fake_dataset


def test_get_dataset_from_repo():
    dataset_name = 'my_dataset'
    other_dataset_name = 'my_other_dataset'
    uow.datasets.add(create_fake_dataset_by_name(dataset_name=dataset_name))
    uow.datasets.add(create_fake_dataset_by_name(dataset_name=other_dataset_name))
    dataset = services.get_dataset(dataset_name=dataset_name,
                                   dataset_repository_url='',
                                   dataset_catalog='',
                                   username='',
                                   password='',
                                   uow=uow)
    assert dataset.name == dataset_name


def test_get_dataset_produces_dataset_requested_event():
    dataset_name = 'my_dataset'
    uow.datasets.add(create_fake_dataset_by_name(dataset_name=dataset_name))
    dataset = services.get_dataset(dataset_name=dataset_name,
                                   dataset_repository_url='',
                                   dataset_catalog='',
                                   username='',
                                   password='',
                                   uow=uow)
    dataset_obj = uow.datasets.get(dataset_name=dataset.name,
                                   dataset_repository_url='',
                                   dataset_catalog='',
                                   username='',
                                   password='')
    expected = events.DatasetRequested(dataset_name=dataset_name, dataset_repository_url='', dataset_catalog='')
    assert expected == dataset_obj.events[-1]
