.. _config-other:

Supported extra options
=======================

You can specify several extras. This part of configuration belongs to the ``"OTHER"`` section in the configuration dictionary of your Django app.
The ``"OTHER"`` section has to be a dictionary itself. It may have the following keys, but no key is mandatory:

1. ``"MAX_ARG_LENGTH"``
2. ``"MAX_FIELD_VALUE_LENGTH"``
3. ``"GET_SYSTEM_INFO"``

MAX_ARG_LENGTH - Reducing the overload of activities
----------------------------------------------------

Due to the process of tracking activities, the tracked args and kwargs may overload the record of an activity if e.g. a long string gets passed into the original function.

To prevent the generated provenance documents from getting to large, you can reduce the length of the passed args and kwargs by setting the ``"MAX_ARG_LENGTH"`` key in the ``"OTHER"`` section in your configuration dictionary:

.. code-block:: python

    PROVENANCE = {
    ...
    "OTHER":{
        "MAX_ARG_LENGTH": 100
      }
    ...
    }


MAX_FIELD_VALUE_LENGTH - Reducing the overload of entities and agents
---------------------------------------------------------------------

Due to the process of tracking models specified as entities or agents, the tracked fields may overload the generated provenance records if e.g. a long string is stored in an objects field.

To prevent the generated provenance documents from getting to large, you can reduce the length of the recorded fields by setting the ``"MAX_FIELD_VALUE_LENGTH"`` key in the ``"OTHER"`` section in your configuration dictionary:

.. code-block:: python

    PROVENANCE = {
    ...
    "OTHER":{
        "MAX_FIELD_VALUE_LENGTH": 20
      }
    ...
    }


.. _extras-sys-info-label:

GET_SYSTEM_INFO - Tracking system information
---------------------------------------------

Sometimes you want to be able to trace back the system on which your application was running or even crashing.
If you want to track default system information, you need to add at least the ``"sys"`` prefix to the extra namespaces list.

The default system information includes the following values:

1. Python version
2. OS version
3. OS username

It is also possible to provide your own function for tracking system information. You can do this by adding the ``"GET_SYSTEM_INFO"`` key to the ``"OTHER"`` section in your configuration dictionary:

.. code-block:: python

    PROVENANCE = {
    ...
    "OTHER":{
        "GET_SYTEM_INFO": your_own_sys_info_func
      }
    ...
    }

The provided value needs to be a callable that returns a list of tuples. A valid system information recording function looks like this:

.. code-block:: python
    :caption: utils.py

    def your_own_sys_info_func(label="sys"):
        attributes = [(f'{label}:python_version', sys.version),
                      (f'{label}:os', platform.platform()),
                      (f'{label}:os_username', getpass.getuser())]
        return attributes

Each tuple has to be of length 2 and consist of:

1. An identifier consisting of a prefix and a name
2. The actual value that should be recorded.
