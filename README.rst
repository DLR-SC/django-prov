Django Provenance
=================

.. install-start

Django-prov is a Django app to capture Provenance related data in your Django project. It complies to the `W3C PROV Data Model`_.

.. _W3C PROV Data Model: https://www.w3.org/TR/2013/REC-prov-dm-20130430/

Installation
------------

django-prov is tested on Python 3.12 and depends on the libraries `Django`_ and `prov`_

.. _Django: https://www.djangoproject.com/
.. _prov: https://prov.readthedocs.io/en/latest/index.html

You can install it from PyPi hosted on artifacts.dlr.de with the following command:

.. code-block:: shell

    pip install django-prov \
       --index-url https://<artifactory_user>:<artifactory_local_token>@artifacts.dlr.de/artifactory/api/pypi/bacardi-pypi-local-release/simple \
       --extra-index-url https://<artifactory_user>:<artifactory_remote_token>@artifacts.dlr.de/artifactory/api/pypi/bacardi-pypi-remote/simple

- The extra argument :code:`--index-url` uses the bacardi-pypi-local-release which contains internal packages like django-prov.
- The extra argument :code:`--extra-index-url` uses the bacardi-pypi-remote which contains mirrored external packages like Django and prov.

.. important::

    If you want to generate graphical output like SVG or PNG files, you also need to have graphviz installed:

    .. code-block:: shell

        apt install -y graphviz graphviz-dev

.. seealso::

   - **Development Installation:** :ref:`development-installation`

.. install-end

**Important**

If you want to generate graphical output like SVG or PNG files, you also need to have graphviz installed:

.. code-block:: shell

        apt install -y graphviz graphviz-dev

**See also**

- **Development Installation:** `Development installation`_

.. _Development installation: ./docs/general/installation.rst

.. usage-start

Usage
-----

Django-prov is thought to be wrapped around your own Django project:

.. image:: ../docs/workflow.svg
    :width: 40%
    :align: center

You need to follow three steps to start recording provenance in your app:

1. Provide a configuration, e.g. via your settings.py.

   - Define namespaces, output path and formats.
   - Define the models that you want to track, either as entities or agents. The ProvenanceGenerator will then use `Djangos built-in signals`_ to record changes of your models objects in the database.

2. Define activities that you want to track.

   - Functions, classes or Djangos class-based views are supported.

3. Instantiate a ProvenanceGenerator object in your apps.py to start the tracking.

.. seealso::

   - **Configuration options:** :ref:`config-toc-label`


.. _Djangos built-in signals: https://docs.djangoproject.com/en/5.2/topics/signals/

.. usage-end

**See also**

- **Configuration options:** `Configuration options`_

.. _Configuration options: ./docs/django_prov_configuration/configuration_general.rst


Documentation
-------------

The documentation of Django Provenance is available here: `Official Documentation`_

.. _Official Documentation: https://ssa.pages.gitlab.dlr.de/django-prov/

.. build-start

Build Status
----------------

The pipeline and coverage status is indicative of the :code:`main` branch.

.. image:: https://gitlab.dlr.de/ssa/django-prov/badges/main/pipeline.svg
    :target: https://gitlab.dlr.de/ssa/django-prov/commits/main
    :alt: Build status main branch

.. image:: https://gitlab.dlr.de/ssa/django-prov/badges/main/coverage.svg
    :target: https://gitlab.dlr.de/ssa/django-prov/main/coverage/
    :alt: Coverage percentage main branch

.. build-end

Changes
-------

Please see the `CHANGELOG file`_ for notable changes.

.. _CHANGELOG file: ./docs/CHANGELOG.rst

Contributors
--------------------------

- Benjamin Bauer <Benjamin.Bauer@dlr.de>

License
-------

See the `LICENSE file`_ for information about how the package is licensed

.. _LICENSE file: ./LICENSE.rst


