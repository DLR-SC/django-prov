.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

How to configure the ProvenanceGenerator
========================================

This section deals with configuring the ProvenanceGenerator for your use case.

Accepted configurations
-----------------------
There are two possible ways to configure the ProvenanceGenerator:

1. **Settings.py:** You can define the configuration in your apps ``settings.py``. On initialization, the ProvenanceGenerator searches for a ``PROVENANCE`` dictionary in your ``settings.py``, if you don't explicitly pass in another configuration:

    .. code-block:: python
       :caption: settings.py

       PROVENANCE = {...}


    .. code-block:: python
       :caption: apps.py

       class YourAppConfig:
           def ready(self):
               self.generator_instance = ProvenanceGenerator.get()


2. **Explicitly passing a dictionary:** You can define a dictionary anywhere and pass it to the ProvenanceGenerator or create a ProvenanceGeneratorConfiguration beforehand:

    .. code-block:: python
       :caption: config.py

       CONFIG = {...}

       # or create a ProvenanceGeneratorConfiguration
       GENERATOR_CONFIG = ProvenanceGeneratorConfiguration(CONFIG)


    .. code-block:: python
       :caption: apps.py

       from config import CONFIG, GENERATOR_CONFIG

       class YourAppConfig:
           def ready(self):
               self.generator_instance = ProvenanceGenerator.get(CONFIG)

               # or use the already created GENERATOR_CONFIG
               self.generator_instance = ProvenanceGenerator.get(GENERATOR_CONFIG)

.. important::

       The ProvenanceGenerator implements the Singleton pattern. Using this pattern, there can always be only one instance of a ProvenanceGenerator existing.
       Whenever you want to instantiate a ProvenanceGenerator, you need to use the ``ProvenanceGenerator.get()`` method to always get the same instance.
       This ensures that the ProvenanceGenerator always creates correct relations between provenance records later on.


Configuration sections
----------------------

A valid configuration dictionary must contain at least the following sections, which have to be dictionaries themselves:

- ``ENTITIES``
- ``NAMESPACES`` consisting of a ``DEFAULT`` namespace and at least one ``EXTRA`` namespace
- ``OUTPUT`` consisting of at least one serialization format in section ``SERIALIZE``

Additionally it is possible to add the following optional sections:

- ``AGENTS`` (type: dictionary)
- ``PATH`` (type: string) in the ``OUTPUT`` dictionary
- ``GRAPHIC`` (type: dictionary) in the ``OUTPUT`` dictionary
- ``OTHER`` (type: dictionary)

.. seealso::

    For further information about each section, please see the respective documents:

    - ``ENTITIES`` - :ref:`config-entities`
    - ``AGENTS`` - :ref:`config-agents`
    - ``NAMESPACES`` - :ref:`config-namespaces`
    - ``OUTPUT`` - :ref:`config-output`
    - ``OTHER`` - :ref:`config-other`

    Activities are not defined in the configuration, more information can be found here: :ref:`config-activities`
