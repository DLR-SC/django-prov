.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

Installation
============

django-prov is tested on Python 3.12 and depends on the libraries `Django`_ and `prov`_

.. _Django: https://www.djangoproject.com/
.. _prov: https://prov.readthedocs.io/en/latest/index.html

You can install it from PyPi with the following command:

.. code-block:: shell

    pip install django-prov

.. important::

    If you want to generate graphical output like SVG or PNG files, you also need to have graphviz installed:

    .. code-block:: shell

        apt install -y graphviz graphviz-dev


.. _development-installation:

Development installation
------------------------

If you want to contribute to django-prov, you can clone it and install it with development and testing options:

.. code-block:: shell

    git clone https://github.com/DLR-SC/django-prov.git
    cd django-prov/
    pip install -e ".[develop, test]"

You can execute the tests using the following command:

.. code-block:: shell

    mkdir -p build
    pytest --cov --cov-report=term --cov-report=html --cov-report=xml --junitxml=build/test-report.xml tests/

You can build the documentation with sphinx using the following command:

.. code-block:: shell

    mkdir -p build/
    sphinx-build -b html docs/ build/docs/

You can run the example app using the following command:

.. code-block:: shell

    python -m example/manage.py runserver

For changing the provenance recording options, please have a look at the options described in :ref:`config-toc-label`
