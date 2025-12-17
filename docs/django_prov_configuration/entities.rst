.. _config-entities:

How to record entities
======================

The W3C defines entities as follows: *An entity is a physical, digital, conceptual, or other kind of thing with some fixed aspects; entities may be real or imaginary.*

You can declare which of your own models you want to track as an entity by using the ``"ENTITIES"`` section in the configuration dictionary of your Django app.
The ``"ENTITIES"`` section has to be a dictionary. Each model that you want to track has to be a key in the dictionary.

There are two different ways to track your models:

1. **Track all fields of the model:** When you set ``True`` as the value of a model key, all fields of the specified model will be recorded.

    .. code-block:: python

       "ENTITIES": {"example.Borrowing": True, "example.Student": True}

2. **Track specific fields of the model:** You can also specify which fields should be tracked by setting a list of field names as the value of a model key.

    .. code-block:: python

       "ENTITIES": {"example.Book": ["isbn", "title", "is_borrowed"]}

You can also mix both ways, which allows more specific recording of properties that you actually need.

ForeignKey fields
------------------

ForeignKey fields are handled differently than standard Django fields.

If a ForeignKey field of a model is specified explicitly or by setting the value to ``True``, the ProvenanceGenerator tries to follow the key to the related model.

If the related model is specified to be tracked too, the ProvenanceGenerator will create a new record for the ForeignKey and link it to back to the original model.
If the related model is specified as an entity, the link will be a `Membership`_. If the related model is specified as an agent, the link will be an `Attribution`_.

ManyToMany fields
-----------------

ManyToMany fields are handled differently than standard Django fields and ForeignKeys.

Since ManyToMany fields are stored in a different attribute of an object, the ProvenanceGenerator will always try to follow them if the model is specified in the configuration in any way.
For each ManyToMany field, the ProvenanceGenerator creates an entity and links it to the original model via a `Membership`_.

If a ManyToMany field contains objects, the ProvenanceGenerator will create a new record for every object inside a ManyToMany field, if the related model is specified to be tracked too.
For each new record, the ProvenanceGenerator will link it back to the record of the ManyToMany field via a `Membership`_..

Edge cases
----------

In the example app, the models Student and Librarian form an edge case:

Do objects of these classes belong to entities, because they are digital objects or do these objects belong to agents because they are associated to real persons that take responsibility for actions that took place.

In such cases you need to decide yourself, which handling is more appropriate to your use case.


Example configuration
---------------------

.. code-block:: python

    PROVENANCE = {
    ...
    "ENTITIES": {
        "example.Borrowing": True,
        "example.Book": ["isbn", "title", "is_borrowed"]
    },
    ...
    }


.. _Membership: https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-membership
.. _Attribution: https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-attribution
