The example application
=======================

The django-prov tool is tested using an example django application. The example app represents a universities library consisting of the following models:

- Book
- Borrowing
- Student
- Librarian

Students are able to order books within a borrowing, which is then passed to a librarian to approve the request.
After a period of time, the borrowing will be returned by either the student who borrowed it or any librarian.
After that, the books can be ordered by another student.

The example app can be found here: `Django Provenance - Example application`_

.. _Django Provenance - Example application: https://gitlab.dlr.de/provenance/django-prov/-/tree/main/example

.. _example-questions:

Integration of django-prov
--------------------------

With the usage of django-prov wrapped around the example app, users can answer certain question without actually having to look at the code or the database itself.

1. What does the information flow during the borrowing process look like?
2. Which person started, approved or returned a borrowing?
3. What is the most recent state of a book? Is it borrowed or available?
4. Which fields of an object change during a borrowing?
5. What actions led to a corrupted state of a book?
