.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

.. _config-activities:

How to record activities
========================

The W3C defines activities as follows: *An activity is something that occurs over a period of time and acts upon or with entities; it may include consuming, processing, transforming, modifying, relocating, using, or generating entities.*

In opposition to entities and agents, you do not define activities in your configuration. You need to manually specify an activity for each function or method whose execution should be recorded. In addition, recording the execution of Djangos class-based views is done differently, too.

Getting the instance of the ProvenanceGenerator
-----------------------------------------------

To be able to track the correct flow of multiple executing activities, each activity has to provide data for the same ProvenanceGenerator instance.
This is only possible, because the ProvenanceGenerator implements the Singleton pattern.
Using this pattern, there can always be only one instance of a ProvenanceGenerator existing.
Each activity will then contribute to the same ProvenanceGenerator instance.

You can get an instance of the ProvenanceGenerator using the class method ``get()`` at the top of the module where you want to record an activity:

.. code-block:: python

    from django_prov.generator import ProvenanceGenerator
    generator_instance = ProvenanceGenerator.get()


How to record functions
-----------------------

To record each execution of a function, you need to wrap it with the `ProvenanceGenerator.activity()` decorator:

.. code-block:: python

    @generator_instance.activity(name="my_activity_name")
    def return_a_borrowing(request, pk=None):
        ...

You can specify a useful name for your function. If you don't specify a name, the ProvenanceGenerator will record the original function name in the provenance documents.

If a function is calling another function that got decorated too, the ProvenanceGenerator is able to correctly relate them using a `Communication`_

How to record classes
---------------------

For ordinary Python classes, apply the ``activity()`` decorator to a class to record
construction and public methods:

The following examples use plain Python versions of the library workflows of the
``example`` application. Borrowings use the status codes: ``O`` (ordered), ``B``
(borrowed), and ``R`` (returned).

.. code-block:: python

    @generator_instance.activity(name="Borrowing")
    class Borrowing:
        def __init__(self):
            self.status = "O"

        def start_borrowing(self):
            self.status = "B"
            return self.status

The resulting activities will be named ``Borrowing.__init__`` and
``Borrowing.start_borrowing``. The decorator returns the original class, preserving
``isinstance`` checks and inheritance. Public inherited methods, static methods,
and class methods are included. Private methods, properties, and special methods
(except ``__init__()``) are not recorded. Parent classes are not modified.

If you don't want to trace all methods of a class. you can still decorate individual methods instead. An explicit method decorator
will be recorded over the class decorator and is not wrapped a second time:

.. code-block:: python

    class Borrowing:
        def __init__(self):
            self.status = "B"

        @generator_instance.activity(name="return_borrowing", fields=["status"])
        def return_borrowing(self):
            self.status = "R"
            return self.status

Recording selected instance states
----------------------------------

The optional ``fields`` argument records the listed attributes as entity
snapshots before and after function or class / dataclass calls. Without ``fields``, the decorator records the
activity only. With ``fields=[]``, records will only contain the object's type.

An existing state is linked to the activity through usage. A changed state is a
new entity, linked to its previous version through derivation and to the activity
through generation. Unchanged states will be reused within the current document, without
creating additional generation relations. Construction records only the initialized state of the specified fields.
If the values of recorded fields are bigger than the specified output size, they will be cut short.

The first function parameter supplies the instance, including when passed by
keyword. If you specify fields that don't exist, the generator will raise an Exception.
Be careful, because attribute getters may run, which can result in additional runtime.
Objects that get decorated with the ``activity()`` don't need to be added to the explicit Django model configuration.

.. code-block:: python

    from dataclasses import dataclass

    @generator_instance.activity(fields=["status"])
    @dataclass
    class Borrowing:
        status: str = "O"

        def start_borrowing(self):
            self.status = "B"

        def return_borrowing(self):
            self.status = "R"

    @generator_instance.activity(name="borrow_and_return")
    def borrow_and_return():
        borrowing = Borrowing()
        borrowing.start_borrowing()
        borrowing.return_borrowing()

    borrow_and_return()

The example shows, how you can use the ``activity()`` decorator.

Place the decorator above ``@dataclass`` so it sees the generated
constructor. The outermost executed activty will export and reset the latest Provenance document.
You can wrap a workflow in another activity to record several calls and their versions together.
Direct attribute assignments outside decorated calls will not be intercepted.

.. _activities-django-views-label:

How to record Django class-based views
--------------------------------------

For Django class-based views, it is proposed to decorate ``dispatch()`` with Django's ``method_decorator``.
Whole-class decoration is intended for ordinary Python classes.
Django models will be recorded using the existing configuration and connected signals:

.. code-block:: python

    @method_decorator(generator.activity(name="django_activity",), name='dispatch')
    class BorrowStartView(UpdateView):
        model = Borrowing
        template_name = 'order_form.html'

Since you usually don't access the `dispatch()` method in your code, you need to wrap the ProvenanceGenerator.activity() in a ``method_decorator()``.
Using this decorator, you define the name of the method you want to decorate, in this case it is ``name=dispatch``.

It is still possible to manually decorate other methods, but django-prov works best when decorating the ``dispatch()`` method.

.. seealso::

    Information on the method flowchart of Djangos class-based views can be found here: `Django - Base Views`_

.. _Django - Base Views: https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#view

.. _Communication: https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-Communication
