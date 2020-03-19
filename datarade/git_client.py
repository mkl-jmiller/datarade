"""
This client allows a user to access files stored in a git-compliant source control repository.
It supports publicly available repos hosted on GitHub and public or private git-compliant repos hosted on Azure Repos.
"""
import abc
from typing import Generator

import requests
from azure.devops.connection import Connection
from azure.devops.v6_0.git.models import GitVersionDescriptor
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.git.git_client import GitClient as AzureReposGitClient


class AbstractGitClient(abc.ABC):

    @abc.abstractmethod
    def get_file_contents(self, file_path: str) -> str:
        """
        This returns the contents of a file in the repo.

        Args:
            file_path: the relative path to the file within the repo

        Returns: the file contents as a string
        """
        raise NotImplementedError


class GitHubClient(AbstractGitClient):
    """
    This client grants access to files on a public repo hosted on GitHub. The current implementation just goes right
    to the raw file to get the contents.

    Args:
        repository: the name of the repo (e.g. https://github.com/<organization>/<repository>)
        organization: the user or organization that owns the repo (see repository example)
        branch: the name of the branch to use
    """
    def __init__(self, repository: str, organization: str, branch: str):
        self.base_url = f'https://raw.githubusercontent.com/{organization}'
        self.repository = repository
        self.branch = branch

    def get_file_contents(self, file_path: str) -> str:
        """
        This performs a basic get on the raw contents on GitHub. It's not ideal, but does the job.

        Args:
            file_path: the relative path to the file within the repo

        Returns: the contents of the file as a string
        """
        url = f'{self.base_url}/{self.repository}/{self.branch}/{file_path}'
        try:
            response = requests.get(url=url)
        except Exception as e:
            print(f'File does not exist at: {url}')
            raise e
        else:
            return response.content


class AzureReposClient(AbstractGitClient):
    """
    This client grants access to files on a public or private git-compliant repo hosted on Azure Repos. It uses
    Microsoft's azure-devops package, which is currently in beta for versions 5.0 and 6.0.

    Args:
        repository: the name of the repo (e.g. https://dev.azure.com/<organization>/<project>/_git/<repository>)
        organization: the organization that owns the Azure DevOps instance (see repository example)
        project: the project within the organization that contains the repo (see repository example)
        branch: the name of the branch to use
        username: the username for the repo
        password: the password for the repo
    """
    def __init__(self, repository: str, organization: str, project: str, branch: str,
                 username: str, password: str):
        self.client: 'AzureReposGitClient' = self._get_client(organization=organization, username=username,
                                                              password=password)
        self.project = project
        self.repository = repository
        self.version_descriptor = GitVersionDescriptor(version=branch)

    @staticmethod
    def _get_client(organization: str, username: str, password: str) -> 'AzureReposGitClient':
        """
        This method configures this client to connect to Azure Repos.

        Args:
            organization: the organization within the Azure DevOps instance
            username: the username for the organization
            password: this can be a password for no MFA, or the git credentials password that overrides MFA

        Returns: an instance of the azure-devops v6.0 GitClient
        """
        base_url = f'https://dev.azure.com/{organization}'
        credentials = BasicAuthentication(username=username, password=password)
        connection = Connection(base_url=base_url, creds=credentials)
        client_type = 'azure.devops.v6_0.git.git_client.GitClient'
        return connection.get_client(client_type=client_type)

    def get_file_contents(self, file_path: str) -> str:
        """
        This uses get_item_content() to get the file contents from Azure Repos.

        Args:
            file_path: the relative path to the file within the repo

        Returns: the contents of the file as a string
        """
        try:
            content: 'Generator' = self.client.get_item_content(repository_id=self.repository,
                                                                project=self.project,
                                                                path=file_path,
                                                                version_descriptor=self.version_descriptor,
                                                                download=True)
        except Exception as e:
            path_to_file = f'{self.project}/{self.repository}/{self.version_descriptor.version}/{file_path}'
            print(f'File does not exist at: {path_to_file}')
            raise e
        else:
            file = ''
            for item in content:
                file += item.decode('utf-8')
            return file
