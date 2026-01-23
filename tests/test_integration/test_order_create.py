# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

import re

from django.contrib.auth.models import User
from django.urls import reverse
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration
from django_prov.generator import ProvenanceGenerator
from example.models import Student, Librarian, Book, Borrowing

from tests.utils.configs import FULL_PROVENANCE, PROVENANCE_NO_BOOK, PROVENANCE_NO_BORROWING, \
    PROVENANCE_NO_AUTH_NO_BORROWING, PROVENANCE_NO_STUDENT_NO_LIBRARIAN, PROVENANCE_STUDENT_AND_LIBRARIAN_AGENT
from tests.utils.regex_patterns import order_create_pattern, order_create_pattern_no_borrowing, \
    order_create_pattern_no_auth_no_borrowing, order_create_pattern_no_book, \
    order_create_pattern_no_student_no_librarian, order_create_pattern_student_and_librarian_agent


class OrderCreateTest(TestCase):
    """
    Tests that the Create Order functionality of the example app results in the correct ProvDocument.
    """
    def setUp(self) -> None:
        self.default_student_user = User.objects.create_user(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.default_librarian_user = User.objects.create_user(username="Librarian", password="l")
        self.default_librarian = Librarian.objects.create(person=self.default_librarian_user)
        self.book1 = Book.objects.create(isbn="9781627052214", title="Provenance: An Introduction to PROV", author="Luc Moreau", pub_year=2013)
        self.book2 = Book.objects.create(isbn="978140885589", title="Harry Potter and the Philosopher's Stone", author="J.K. Rowling", pub_year=1997)
        self.borrowing = Borrowing.objects.create(student=self.default_student)
        self.borrowing.ordered_books.add(self.book1, self.book2)

    def tearDown(self):
        User.objects.all().delete()
        Book.objects.all().delete()
        Student.objects.all().delete()
        Borrowing.objects.all().delete()
        Librarian.objects.all().delete()

    @given(st.sampled_from([
        ("Full Provenance", FULL_PROVENANCE, order_create_pattern),
        ("No Borrowing", PROVENANCE_NO_BORROWING, order_create_pattern_no_borrowing),
        ("No Auth, no Borrowing", PROVENANCE_NO_AUTH_NO_BORROWING, order_create_pattern_no_auth_no_borrowing),
        ("No Book", PROVENANCE_NO_BOOK, order_create_pattern_no_book),
        ("No Student, No Librarian", PROVENANCE_NO_STUDENT_NO_LIBRARIAN, order_create_pattern_no_student_no_librarian),
        ("Student and Librarian Agent", PROVENANCE_STUDENT_AND_LIBRARIAN_AGENT,
         order_create_pattern_student_and_librarian_agent)
    ]))
    @settings(deadline=None)
    def test_order_create(self, given_data):
        """
        Tests that for different versions of the ProvenanceGeneratorConfiguration the 'order create' functionality generates correct records.
        """
        name, config, regex_pattern = given_data

        prov_configuration = ProvenanceGeneratorConfiguration(config)
        generator = ProvenanceGenerator.reset_settings(prov_configuration)



        self.client.login(username='Student', password='s')
        order_create_data = {"ordered_books": [self.book1.id, self.book2.id]}
        response = self.client.post(reverse('order.create'), data=order_create_data)
        self.assertEqual(response.status_code, 302)

        borrowing = Borrowing.objects.get(id=2)
        self.assertEqual(len(borrowing.ordered_books.all()), 2)


        for out, pattern in zip([], regex_pattern):
            assert re.fullmatch(pattern, out), f"{out!r} did not match {pattern!r}"

