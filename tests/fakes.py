from tests.conftest import git_client, models


class FakeGitClient(git_client.AbstractGitClient):

    files = {}

    def get_file_contents(self, file_path: str) -> str:
        return self.files[file_path]

    def add(self, file_path: str, file_contents: str):
        self.files.update({file_path: bytes(file_contents, encoding='utf8')})

    def reset(self):
        self.files = {}


class FakeDatasetCatalog(models.DatasetCatalog):

    def _get_git_client(self, platform: str = None) -> 'FakeGitClient':
        return FakeGitClient()

    def add(self, dataset: dict):
        dataset_name = dataset['name']
        config_file = str(dataset['config'])
        definition_file = str(dataset['definition'])
        self.git.add(file_path=f'catalog/{dataset_name}/config.yaml', file_contents=config_file)
        self.git.add(file_path=f'catalog/{dataset_name}/definition.sql', file_contents=definition_file)

    def reset(self):
        self.git.reset()
