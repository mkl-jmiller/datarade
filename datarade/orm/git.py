"""
This is the ORM for obtaining datasets out of a git repo. It combines marshmallow with a home-grown, bare bones git
'session'.
"""
from io import BytesIO

import marshmallow as ma
import requests
import yaml
from requests_ntlm import HttpNtlmAuth

from datarade.domain import models


class FieldSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a datarade Field object
    """
    name = ma.fields.Str(required=True)
    description = ma.fields.Str(required=False)
    type = ma.fields.Str(required=True)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> models.Field:
        return models.Field(**data)


class DatabaseSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a datarade Database object
    """
    driver = ma.fields.Str(required=True)
    database_name = ma.fields.Str(required=True)
    host = ma.fields.Str(required=True)
    port = ma.fields.Int(required=False)
    schema_name = ma.fields.Str(required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> models.Database:
        return models.Database(**data)


class DatasetSchema(ma.Schema):
    """
    A marshmallow schema corresponding to a datarade Dataset object
    """
    name = ma.fields.Str(required=True)
    description = ma.fields.Str(required=False)
    fit_for_use = ma.fields.Str(required=False)
    definition = ma.fields.Str(required=True)
    fields = ma.fields.Nested(FieldSchema, required=True, many=True)
    database = ma.fields.Nested(DatabaseSchema, required=False)

    @ma.post_load()
    def post_load(self, data: dict, **kwargs) -> models.Dataset:
        return models.Dataset(**data)


class GitSession:
    """
    This is a wrapper around a git repo that allows file access. It can be handed a github url or git-tfs url.

    Args:
        repository: the url to the git repo
        catalog: the name of the directory containing the target files (analogous to a table, with datasets being
        the records)
        username: the username for the repo
        password: the password for the repo

    .. Note:
        This was intended to be indifferent to the rest of this package, in the sense that it wouldn't 'know' about any
        datarade concepts. This would be similar to how a sqlalchemy session can be defined prior to associating model
        classes with sqlalchemy tables. However, this turns out not to be the case, as is evident with the get_dataset()
        method and catalog parameter.
    """
    def __init__(self, repository: str, catalog: str, username: str = None, password: str = None):
        self.repository = repository
        self.catalog = catalog
        self.username = username
        self.password = password

    def get_file(self, file_path: str) -> BytesIO:
        """
        This will return a specific file within the catalog.

        Args:
            file_path: the relative path to the file within <repository>/<catalog>/

        Returns: a file as a BytesIO object
        """
        if 'github' in self.repository:
            return self._get_github_file(file_path)
        if '/tfs/' in self.repository:
            return self._get_git_tfs_file(file_path)

    def get_dataset(self, dataset_name: str) -> models.Dataset:
        """
        This will return a dataset from the dataset catalog.

        Args:
            dataset_name: the name of the dataset

        Returns: a datarade Dataset object
        """
        return get_dataset(self, dataset_name)

    def _get_github_file(self, file_path: str) -> BytesIO:
        """
        This is the github version of the get_file() function.

        Args:
            file_path: the relative path to the file within <repository>/<catalog>/

        Returns: a file as a BytesIO object
        """
        url = f'{self.repository}/{self.catalog}/{file_path}'
        response = requests.get(url=url)
        return response.content

    def _get_git_tfs_file(self, file_path: str) -> BytesIO:
        """
        This is the git-tfs version of the get_file() function.

        Args:
            file_path: the relative path to the file within <repository>/<catalog>/

        Returns: a file as a BytesIO object
        """
        url = f'{self.repository}/items/{self.catalog}/{file_path}'
        if self.username and self.password:
            auth = HttpNtlmAuth(username=self.username, password=self.password)
            response = requests.get(url=url, auth=auth)
        else:
            response = requests.get(url=url)
        return response.content


def get_dataset(session: 'GitSession', dataset_name: str) -> models.Dataset:
    """
    This method returns a Dataset object given a name. It collects all of the required files from the repository,
    puts the contents in a configuration dictionary, passes that dictionary up to the abstract repository for
    validation, and returns the resulting Dataset instance.

    Args:
        session: the session for the catalog containing the dataset
        dataset_name: the name of the dataset, which should be the name of the directory containing the files

    Returns: a Dataset object
    """
    config_yaml = session.get_file(f'{dataset_name}/config.yaml')
    config_dict = yaml.safe_load(config_yaml)
    definition = session.get_file(f'{dataset_name}/definition.sql')
    config_dict['definition'] = definition
    dataset_schema = DatasetSchema()
    return dataset_schema.load(config_dict)
