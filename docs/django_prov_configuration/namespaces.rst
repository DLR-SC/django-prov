.. _config-namespaces:

How to set correct namespaces
=============================

Namespaces are a way associate names with a specific context by mapping them to a unique identifier, so that it is possible to use the same name in different contexts without conflicts.

A namespace maps a prefix to a URI, allowing compact names to represent full unique resource identifiers. In code, a namespace is integrated by creating qualified names that combine a prefix with a local name.
This allows to resolve the qualified name to a full URI later on.


Supported namespaces for your Django app
----------------------------------------
The Configuration you use to record provenance needs to have at least two namespaces to work.

Namespaces are declared in the :code:`"NAMESPACES"` section in the configuration dictionary of your Django app. This section also needs to be divided in to two further sections:

1. :code:`"DEFAULT"`: contains your default URI which is used to resolve other prefixes to URIs. Recommendation: Use the name of your Django project, e.g. :code:`"example.org/"`.

2. :code:`"EXTRA"`: contains the prefixes of every app of your project that you want to track. It depends on your use case to decide which of the namespaces you actually need. Recommendation: Use the name of the app that you want to track, e.g. :code:`"example"`.

    Furthermore, there are three optional namespace prefixes supported:

    - :code:`"auth"`: includes the recording of models from the Django authentication app, e.g. Users.
    - :code:`"django"`: includes the recording of Djangos class-based views. For more information, see :ref:`activities-django-views-label`
    - :code:`"sys"`: includes the recording of system information for every activity that is tracked. For more information, see: :ref:`extras-sys-info-label`


Example configuration
---------------------

.. code-block:: python

    PROVENANCE = {
    ...
    "NAMESPACES": {
        "DEFAULT": f"example.org/",
        "EXTRA": [
            "auth",
            "django",
            "sys",
            "example",
        ]
    },
    ...
    }
