"""
This module contains the domain events that occur throughout processing requests.
"""
from dataclasses import dataclass


class Event:
    pass


@dataclass
class DatasetRequested(Event):
    """
    This event captures the fact that a dataset was requests from a dataset catalog. It can be used for things like
    logging access and dataset popularity/frequency.
    """
    dataset_name: str
    dataset_repository_url: str
    dataset_catalog: str
