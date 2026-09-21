.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

.. _Changelog:

Changelog
=========

Version 0.2.2 (16.09.2026)
--------------------------

Adds ordinary Python class support.

New features
^^^^^^^^^^^^
- Added support for tracking ordinary Python classes
    - classes or dataclasses can be tracked using the activity decorator
    - class attributes can be tracked as entities

Documentation
^^^^^^^^^^^^^
- Added documentation for recording ordinary Python classes

Patches
^^^^^^^

- fixed ordering of same-named Provenance objects with the same timestamp

Version 0.2.1 (17.12.2025)
---------------------------

Adds documentation pages and minor patches.

Documentation
^^^^^^^^^^^^^

- Added documentation built with sphinx, consisting of:
    - general information
    - configuration information
    - code documentation

Patches
^^^^^^^

- fixed record creation for agent objects that have ManyToMany fields
- fixed record creation for agent objects in ManyToMany fields

Version 0.2 (2025-12-08)
------------------------

Introduces an improved ProvenanceGenerator, the new ProvenanceGeneratorConfiguration and patches.

ProvenanceGenerator
^^^^^^^^^^^^^^^^^^^

- The ProvenanceGenerator is now configured using a ProvenanceGeneratorConfiguration
- Fields of Django objects can be specified for reducing the overhead
- System information recording can be specified
- added unit and integration tests

ProvenanceGeneratorConfiguration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Specifies entities, agents, namespaces, output and extras
- Validates given configurations
- Added unit and integration tests

Patches
^^^^^^^

- Improved edge case and Exception handling
  - Improved relations between two agents
  - Improved backward connection of existing ProvRecords
- Improved internal object representation
  - Improved namespace handling
  - Improved output handling
- Made maximum field value length settable 

Version 0.1.1 (2025-07-23)
--------------------------

Patches, example application and initial Artifactory release.

Patches
^^^^^^^
- Refactored time representation in the object identifier
- Improved edge case and Exception handling
- Improved internal object representation

Example application
^^^^^^^^^^^^^^^^^^^
- Added an example application
- Added unit and integration tests

Documentation
^^^^^^^^^^^^^
- Added an instruction for configuring the django-prov tool.

Artifactory
^^^^^^^^^^^
- This version is the first version of django-prov to get published to the artifactory

Version 0.1
-----------
The version 0.1 of django-prov collected all important features and progress made before a release process was established.
