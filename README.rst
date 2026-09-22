.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

Django Provenance
=================

.. install-start

> Django-prov is no longer being actively developed. The repository archives the status of version 2.0.2, which was actively developed in GitLab.
For more information, please contact carina.haupt@dlr.de.

Django-prov is a Django app to capture Provenance related data in your Django project. It complies to the `W3C PROV Data Model`_.

.. _W3C PROV Data Model: https://www.w3.org/TR/2013/REC-prov-dm-20130430/

Installation
------------

django-prov is tested on Python 3.12 and depends on the libraries `Django`_ (`BSD-3-Clause License`_) and `prov`_ (`MIT License`_)

.. _Django: https://www.djangoproject.com/
.. _BSD-3-Clause License: https://github.com/django/django/blob/main/LICENSE
.. _prov: https://prov.readthedocs.io/en/latest/index.html
.. _MIT License: https://github.com/DLR-SC/django-prov/-/blob/main/LICENSES/MIT.txt

You can install it with the following command:

.. code-block:: shell

    git clone https://github.com/DLR-SC/django-prov.git
    cd django-prov/
    pip install -e .

.. install-end

**Important**

If you want to generate graphical output like SVG or PNG files, you also need to have graphviz installed:

.. code-block:: shell

        apt install -y graphviz graphviz-dev

**See also**

- **Development Installation:** `Development installation`_

.. _Development installation: https://github.com/DLR-SC/django-prov/blob/main/docs/general/installation.rst

.. usage-start

Usage
-----

Django-prov is thought to be wrapped around your own Django project:

.. image:: https://raw.githubusercontent.com/DLR-SC/django-prov/main/docs/workflow.svg
    :width: 40%
    :align: center
    :target: https://raw.githubusercontent.com/DLR-SC/django-prov/main/docs/workflow.svg

You need to follow three steps to start recording provenance in your app:

1. Provide a configuration, e.g. via your settings.py.

   - Define namespaces, output path and formats.
   - Define the models that you want to track, either as entities or agents. The ProvenanceGenerator will then use `Djangos built-in signals`_ to record changes of your models objects in the database.

2. Define activities that you want to track.

   - Functions, classes or Djangos class-based views are supported.

3. Instantiate a ProvenanceGenerator object in your apps.py to start the tracking.

.. usage-end

**See also**

- **Configuration options:** `Configuration options`_

.. _Configuration options: https://github.com/DLR-SC/django-prov/blob/main/docs/django_prov_configuration/configuration_general.rst


Documentation
-------------

The documentation of Django Provenance is available here: `Official Documentation`_

.. _Official Documentation: https://github.com/DLR-SC/django-prov/blob/main/docs/


Changes
-------

Please see the `CHANGELOG file`_ for notable changes.

.. _CHANGELOG file: https://github.com/DLR-SC/django-prov/blob/main/docs/CHANGELOG.rst

Contributors
--------------------------

- Benjamin Bauer <Benjamin.Bauer@dlr.de>

Contributing
------------

The project is no longer actively maintained. For more information, please contact carina.haupt@dlr.de.

License
-------

This project is `MIT`_ licensed.
Copyright © 2026 German Aerospace Center (DLR) and individual contributors.

.. _MIT: https://github.com/DLR-SC/django-prov/blob/main/LICENSE.rst
