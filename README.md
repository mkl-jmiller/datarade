# Datarade

**This library provides tools to allow users to describe data pipelines in yaml format.**

---

# Overview

This library separates the 'how' from the 'what' when sourcing datasets and producing data pipelines.
The definition of a dataset is stored in a git repository and referenced by name in the client application.
This allows the definition to be source controlled independently from the client application.

# Requirements

- Python 3.7+
- sqlalchemy
- marshmallow
- pyyaml
- pyodbc
- pymssql
- bcp
- requests
- requests_ntlm

# Installation

This package is hosted on PyPI:

```shell script
pip install datarade
```

# Examples

Use the dataset catalog services to obtain datasets:
```python
from datarade.services.dataset_catalog import api

dataset_repository_url = 'https://raw.githubusercontent.com/mikealfare/dataset_catalog_test/master'
dataset = api.get_dataset(dataset_name='my_dataset',
                          dataset_repository_url=dataset_repository_url,
                          dataset_catalog='catalog')
print(dataset.definition)
```

Use the dataset subscription services to move datasets to a database:
```python
from datarade.services.dataset_subscription import api

dataset_name = 'test_dataset'
dataset_repository_url = 'https://raw.githubusercontent.com/mikealfare/dataset_catalog_test/master'
api.register_dataset_container(dataset_container_id='test',
                               dataset_repository_url=dataset_repository_url,
                               dataset_catalog='catalog',
                               driver='mssql',
                               database_name='my_db',
                               host='my_host',
                               port=54321,
                               schema_name='my_schema'
                               )
api.add_dataset(dataset_container_id='test',
                dataset_name=dataset_name,
                dataset_username='user',
                dataset_password='password1234')
api.refresh_dataset(dataset_container_id='test', dataset_name=dataset_name)
```

# Full Documentation

For the full documentation, please visit: https://datarade.readthedocs.io/en/latest/
