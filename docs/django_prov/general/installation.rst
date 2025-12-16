Installation
============

django-prov is tested on Python 3.12 and depends on the libraries `Django`_ and `prov`_

.. _Django: https://www.djangoproject.com/
.. _prov: https://prov.readthedocs.io/en/latest/index.html

You can install it from PyPi hosted on artifacts.dlr.de with the following command:

.. code-block:: shell

    pip install django-prov --index-url https://<artifactory_user>:<artifactory_local_token>@artifacts.dlr.de/artifactory/api/pypi/bacardi-pypi-local-release/simple
       --extra-index-url https://<artifactory_user>:<artifactory_remote_token>@artifacts.dlr.de/artifactory/api/pypi/bacardi-pypi-remote/simple

- The extra argument :code:`--index-url` uses the bacardi-pypi-local-release which contains internal packages like django-prov.
- The extra argument :code:`--extra-index-url` uses the bacardi-pypi-remote which contains mirrored external packages like Django and prov.


Development installation
------------------------

If you want to contribute to django-prov, you can clone it and install it with development and testing options:

.. code-block:: shell

    git clone https://gitlab.dlr.de/ssa/django-prov.git
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
