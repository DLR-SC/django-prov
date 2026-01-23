# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from hypothesis.extra.django import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration
from example.models import Student, Librarian, Book, Borrowing

from tests.utils.configs import DEFAULT_PROVENANCE
from tests.utils.utils import clean_test_settings, get_clean_generator_init


class ExampleViewAccessTest(TestCase):
    """
    Tests that the access rights for the example app work correctly.
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

    @patch("sys.stdout.write")
    @patch('sys.stderr', new_callable=StringIO)
    def test_index_view(self, mock_stderr, mock_stdout):
        """
        Tests that the index view works correctly.
        """
        result = self.client.login(username='Student', password='s')
        self.assertTrue(result)
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Hi Student !")

    @patch("sys.stdout.write")
    @patch('sys.stderr', new_callable=StringIO)
    def test_access_rights_student(self, mock_stderr, mock_stdout):
        """
        Tests that the student is able to order books, but not to borrow them by himself.
        """
        result = self.client.login(username='Student', password='s')
        response = self.client.get(reverse('order.create'))
        self.assertEqual(response.status_code, 200)
        forbidden = self.client.get(reverse('borrow.start', args=[1]))
        self.assertEqual(forbidden.status_code, 403)

    @patch("sys.stdout.write")
    @patch('sys.stderr', new_callable=StringIO)
    def test_access_rights_librarian(self, mock_stderr, mock_stdout):
        """
        Tests that the librarian is not able to order books, but to start borrowings of students.
        """
        result = self.client.login(username='Librarian', password='l')
        forbidden = self.client.get(reverse('order.create'))
        self.assertEqual(forbidden.status_code, 403)
        response = self.client.get(reverse('borrow.start', args=[1]))
        self.assertEqual(response.status_code, 200)
