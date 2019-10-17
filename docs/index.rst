.. Datarade documentation master file, created by
   sphinx-quickstart on Wed May 15 15:38:21 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Datarade's documentation!
====================================

The source repository is located
`here <https://github.com/mikealfare/datarade>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

API
===

Dataset Catalog
---------------

.. automodule:: datarade.services.dataset_catalog.api
   :members:
   :private-members:

Dataset Subscription
--------------------

.. automodule:: datarade.services.dataset_subscription.api
   :members:
   :private-members:

Services
========

Dataset Catalog
---------------

.. automodule:: datarade.services.dataset_catalog.services
   :members:
   :private-members:

.. automodule:: datarade.services.dataset_catalog.unit_of_work
   :members:
   :private-members:

.. automodule:: datarade.services.dataset_catalog.message_bus
   :members:
   :private-members:

Dataset Subscription
--------------------

.. automodule:: datarade.services.dataset_subscription.handlers
   :members:
   :private-members:

.. automodule:: datarade.services.dataset_subscription.utils
   :members:
   :private-members:

.. automodule:: datarade.services.dataset_subscription.unit_of_work
   :members:
   :private-members:

.. automodule:: datarade.services.dataset_subscription.message_bus
   :members:
   :private-members:

Domain
======

Models
------

.. automodule:: datarade.domain.models
   :members:
   :private-members:

Commands
--------

.. automodule:: datarade.domain.commands
   :members:
   :private-members:

Events
------

.. automodule:: datarade.domain.events
   :members:
   :private-members:

Exceptions
----------

.. automodule:: datarade.domain.exceptions
   :members:
   :private-members:

Repositories
============

Abstract Repositories
---------------------

.. automodule:: datarade.abstract_repositories.datasets
   :members:
   :private-members:

.. automodule:: datarade.abstract_repositories.dataset_containers
   :members:
   :private-members:

Implemented Repositories
------------------------

.. automodule:: datarade.repositories.datasets_git
   :members:
   :private-members:

.. automodule:: datarade.repositories.dataset_containers_stateless
   :members:
   :private-members:

ORMs
====

Git
---

.. automodule:: datarade.orm.git
   :members:
   :private-members:
