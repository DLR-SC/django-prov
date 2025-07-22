import datetime
import tempfile
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.utils.encoding import escape_uri_path

from example.models import Student, Librarian, Book, Borrowing

from tests.test_units import get_generator
from tests.regex_patterns import order_create_pattern, borrowing_start_pattern

class ExampleViewTests(TestCase):
    def setUp(self) -> None:
        self.default_student_user = User.objects.create_user(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.default_librarian_user = User.objects.create_user(username="Librarian", password="l")
        self.default_librarian = Librarian.objects.create(person=self.default_librarian_user)
        self.book1 = Book.objects.create(isbn="9781627052214", title="Provenance: An Introduction to PROV", author="Luc Moreau", pub_year=2013)
        self.book2 = Book.objects.create(isbn="978140885589", title="Harry Potter and the Philosopher's Stone", author="J.K. Rowling", pub_year=1997)
        self.order_create_data = {
            "ordered_books": [self.book1.id, self.book2.id]
        }
        self.borrow_start_data = {
            "student" : self.default_student,

            "ordered_books": [self.book1.id, self.book2.id],
            "borrowed_books": [self.book1.id, self.book2.id],
            "date_of_order": datetime.date.today,
            "bor_start_date" : "",
            "bor_auto_end_date": "",
            "bor_returned_date": "",
            "status": "O"
        }
        self.borrowing = Borrowing.objects.create(student=self.default_student)
        self.borrowing.ordered_books.add(self.book1, self.book2)

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_index_view(self, mock_stderr, mock_stdout):
        result = self.client.login(username='Student', password='s')
        self.assertTrue(result)
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Hi Student !")

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_access_rights_student(self, mock_stderr, mock_stdout):
        result = self.client.login(username='Student', password='s')
        response = self.client.get(reverse('order.create'))
        self.assertEqual(response.status_code, 200)
        forbidden = self.client.get(reverse('borrow.start', args=[1]))
        self.assertEqual(forbidden.status_code, 403)

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_access_rights_librarian(self, mock_stderr, mock_stdout):
        result = self.client.login(username='Librarian', password='l')
        forbidden = self.client.get(reverse('order.create'))
        self.assertEqual(forbidden.status_code, 403)
        response = self.client.get(reverse('borrow.start', args=[1]))
        self.assertEqual(response.status_code, 200)

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_order_create(self, mock_stderr, mock_stdout):
        generator = get_generator(serialize=["n"])
        self.client.login(username='Student', password='s')
        response = self.client.post(reverse('order.create'), data=self.order_create_data)
        self.assertEqual(response.status_code, 302)

        err = mock_stderr.getvalue()
        output = mock_stdout.getvalue()
        self.assertRegex(output, order_create_pattern)
        borrowing = Borrowing.objects.get(id=1)
        self.assertEqual(len(borrowing.ordered_books.all()), 2)

    """@patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_borrowing_start(self, mock_stderr, mock_stdout):
            self.client.login(username='Librarian', password='l')
            before = Borrowing.objects.get(id=1)
            generator = get_generator(serialize=["n"])
            response = self.client.post(reverse('borrow.start', args=[1]), data=self.borrow_start_data)
            self.assertEqual(response.status_code, 302)
            after = Borrowing.objects.get(id=1)
            output = mock_stdout.getvalue()
            self.assertRegex(output, borrowing_start_pattern)"""

    """@patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_borrowing_return_single(self, mock_stderr, mock_stdout):
        pass"""
