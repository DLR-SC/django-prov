.. _config-activities:

How to record activities
========================

The W3C defines activities as follows: *An activity is something that occurs over a period of time and acts upon or with entities; it may include consuming, processing, transforming, modifying, relocating, using, or generating entities.*

In opposition to entities and agents, you do not define activities in your configuration. You need to manually specify an activity for each function or method whose execution should be recorded. In addition, recording the execution of Djangos View classes is done differently, too.

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


How to record functions?
------------------------

To record each execution of a function, you need to wrap it with the `ProvenanceGenerator.activity()` decorator:

.. code-block:: python

    @generator_instance.activity(name="my_activity_name")
    def return_a_borrowing(request, pk=None):
        ...

You can specify a useful name for your function. If you don't specify a name, the ProvenanceGenerator will record the original function name in the provenance documents.

If a function is calling another function that got decorated too, the ProvenanceGenerator is able to correctly relate them using a `Communication`_

How to record classes?
----------------------

Decorating a single class and all of its methods with a single decorator is currently not supported.

It is still possible to decorate each method itself, using the same decorator as in decorating functions:

.. code-block:: python

    class Returning:
    ...
        @generator_instance.activity(name="my_activity_name")
        def return_a_borrowing(request, pk=None):
            ...

        @generator_instance.activity(name="my_other_activity_name")
        def return_all_borrowings(request):
            ...


.. _activities-django-views-label:

How to record Django class-based views?
---------------------------------------

Similarly to normal classes, it is not possible to decorate a Django class-based view with a single decorator. Additionally, django-prov is tested decorating the ``dispatch()`` method of a Django class-based-view:

.. code-block:: python

    @method_decorator(generator.activity(name="django_activity",), name='dispatch')
    class BorrowStartView(UpdateView):
        model = Borrowing
        template_name = 'order_form.html'

Since you usually don't access the `dispatch()` method in your code, you need to wrap the ProvenanceGenerator.activity() in a ``method_decorator()``.
Using this decorator, you define the name of the method you want to decorate, in this case it is ``name=dispatch``.

It is still possible to manually decorate other methods, but django-prov works best when decorating the ``dispatch()`` method.


.. _Communication: https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-Communication
