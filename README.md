# Datarade

**This library provides tools that allow datasets to be defined separately from a pipeline.**

---

# Overview

This library separates the 'how' from the 'what' when sourcing datasets and producing data pipelines. The definition of
a dataset is stored in a git repository and referenced by name in the client application. This allows the definition to
be source controlled independently from the client application. Also, by adding branch support, a dataset catalog can
hold different 'environments' as branches. This allows you to promote your dataset definition and your client
application code using your standard CI/CD process while also giving you an area to perform UAT.

# Requirements

- Python 3.7+
- marshmallow
- pyyaml
- requests
- azure-devops
- sqlalchemy
- pyodbc
- bcp

# Installation

This package is hosted on PyPI:

```shell script
pip install datarade
```

# Examples

Use datarade services to obtain metadata about your datasets from your dataset catalog:
```python
import datarade

repository_url = 'https://raw.githubusercontent.com/fivestack/datarade_test_catalog'
dataset_catalog = datarade.get_dataset_catalog(
    repository=repository_url,
    organization='fivestack',
    platform='github'
)  # no username/password since only public repos are currently supported for github
dataset = datarade.get_dataset(dataset_catalog=dataset_catalog, dataset_name='my_dataset')
print(dataset.name)
print(dataset.definition)
```

Use datarade services to write datasets to a database:
```python
import datarade

repository_url = 'https://raw.githubusercontent.com/mikealfare/dataset_catalog_test/master'
dataset_catalog = datarade.get_dataset_catalog(
    repository=repository_url,
    organization='fivestack',
    platform='azure-devops',
    username='USERNAME_TO_ACCESS_THE_GIT_REPO',
    password='PASSWORD_TO_ACCESS_THE_GIT_REPO'
)
dataset_container = datarade.get_dataset_container(
    driver='mssql',
    database_name='datarade',
    host=r'localhost\DATARADE',
    username='USERNAME_TO_WRITE_TO_THE_DATABASE',
    password='PASSWORD_TO_WRITE_TO_THE_DATABASE'
)

# you can do one off writes like this
dataset = datarade.get_dataset(dataset_catalog=dataset_catalog, dataset_name='my_dataset')
datarade.write_dataset(
    dataset=dataset,
    dataset_container=dataset_container,
    username='USERNAME_TO_READ_THE_DATASET_FROM_THE_SOURCE',
    password='PASSWORD_TO_READ_THE_DATASET_FROM_THE_SOURCE'
)


def write_dataset_wrapper(dataset_name: str, username: str = None, password: str = None):
    """
    But it may be useful to create a function that wraps the configuration like this if you are writing several datasets
    and only using one DatasetCatalog and one DatasetContainer.
    """
    dataset = datarade.get_dataset(dataset_catalog=dataset_catalog, dataset_name=dataset_name)
    datarade.write_dataset(dataset=dataset, dataset_container=dataset_container, username=username, password=password)


write_dataset_wrapper(
    dataset_name='my_other_dataset',
    username='USERNAME_FOR_THIS_SOURCE',
    password='PASSWORD_FOR_THIS_SOURCE'
)
```

# Full Documentation

For the full documentation, please visit: https://datarade.readthedocs.io/en/latest/
