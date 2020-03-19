import pytest

from tests.conftest import services, git_client
from tests.fakes import FakeDatasetCatalog


def generate_dataset(dataset_name: str):
    return {
        'name': dataset_name,
        'config': {
            'name': dataset_name,
            'fields': []
        },
        'definition': f'select {dataset_name}'
    }


def test_get_dataset_catalog_github():
    dataset_catalog = services.get_dataset_catalog(repository='datarade_test_catalog', organization='fivestack',
                                                   platform='github')
    assert isinstance(dataset_catalog.git, git_client.GitHubClient)


@pytest.mark.skip('This test requires authentication to get the client, which seems excessive for a unit test. '
                  'This is tested in integration testing anyway.')
def test_get_dataset_catalog_azure_devops():
    dataset_catalog = services.get_dataset_catalog(repository='datarade_test_catalog', organization='fivestack',
                                                   platform='azure-devops')
    assert isinstance(dataset_catalog.git, git_client.AzureReposClient)


def test_get_dataset_container():
    dataset_container = services.get_dataset_container(driver='mssql', database_name='my_db', host='my_host')
    assert dataset_container.bcp.connection.host == 'my_host'


def test_get_dataset():
    fake_dataset_catalog = FakeDatasetCatalog(repository='', organization='', platform='')
    dataset_1 = generate_dataset(dataset_name='my_dataset')
    dataset_2 = generate_dataset(dataset_name='my_other_dataset')
    fake_dataset_catalog.add(dataset=dataset_1)
    fake_dataset_catalog.add(dataset=dataset_2)
    dataset = services.get_dataset(dataset_name=dataset_1['name'], dataset_catalog=fake_dataset_catalog)
    assert dataset.name == dataset_1['name']
    dataset = services.get_dataset(dataset_name=dataset_2['name'], dataset_catalog=fake_dataset_catalog)
    assert dataset.name == dataset_2['name']
