.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

Django Provenance documentation
===============================

Welcome to the documentation of Django Provenance (django-prov).

.. include:: ../README.rst
    :start-after: .. install-start
    :end-before: .. install-end

.. only:: sphinx

    .. important::

        If you want to generate graphical output like SVG or PNG files, you also need to have graphviz installed:

        .. code-block:: shell

            apt install -y graphviz graphviz-dev

    .. seealso::

       - **Development Installation:** :ref:`development-installation`


.. include:: ../README.rst
    :start-after: .. usage-start
    :end-before: .. usage-end

.. seealso::

   - **Configuration options:** :ref:`config-toc-label`


.. _Djangos built-in signals: https://docs.djangoproject.com/en/5.2/topics/signals/


**Contents**

.. toctree::
   :maxdepth: 2

   general/toc.rst
   django_prov_configuration/toc.rst
   code_docs/toc.rst
   CHANGELOG.rst
