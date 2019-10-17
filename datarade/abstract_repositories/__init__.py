"""
This module contains all of the abstract repositories for the application. It should get called by the service layer
to do work and the repository/orm layer to implement concrete versions of these repositories to save state at runtime.
"""
from .datasets import AbstractDatasetRepository
from .dataset_containers import AbstractDatasetContainerRepository
