from setuptools import setup


with open('README.md') as f:
    readme = f.read()

setup(
    name='query_tools',
    version='0.1.2',
    description='Tools for moving data between data stores',
    long_description=readme,
    author='Mike Alfare',
    author_email='alfare@gmail.com',
    url='https://github.com/mikealfare/query_tools',
    packages=['query_tools'],
    keywords=['QueryTools'],
    tests_require=['pytest', 'pytest-cov']
)
