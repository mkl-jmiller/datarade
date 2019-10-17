"""
This module contains exceptions for the application.
"""


class DatasetDoesNotExist(Exception):
    """
    This exception can occur when a dataset is requested to be reloaded, but it isn't already associated with the
    dataset container.
    """
    pass


class DatasetAlreadyExists(Exception):
    """
    This exception can occur when a dataset is added to a dataset container, but the dataset container already has
    said dataset.
    """
    pass
