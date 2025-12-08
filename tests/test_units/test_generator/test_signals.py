from io import StringIO
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.test import TestCase

import django_prov.generator
from django_prov.configuration import ProvenanceGeneratorConfiguration
from django_prov.generator import ProvenanceGenerator, ProvenanceGeneratorException
from tests.utils.utils import get_clean_generator_init, get_clean_generator_no_init

from example.models import Book, Borrowing, Student


class SignalsTest(TestCase):
    """
    Tests the Django Signal Connection logic of ProvenanceGenerator.
    """


    @patch("sys.stdout", new_callable=StringIO)
    def test_connect_signals_success(self, mock_stdout):
        """
        Tests that for each model that is defined in the settings, signals are connected accordingly.
        """
        expected_output = [
            "Connected pre <class 'example.models.Book'>",
            "Connected post <class 'example.models.Book'>",
            "Connected pre <class 'example.models.Borrowing'>",
            "Connected post <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected pre <class 'example.models.Student'>",
            "Connected post <class 'example.models.Student'>",
            "Connected pre <class 'example.models.Librarian'>",
            "Connected post <class 'example.models.Librarian'>",
        ]

        generator_config = ProvenanceGeneratorConfiguration()
        generator_config.entities = {"example.Book": "test", "example.Borrowing": "Test"}
        generator_config.agents = {"example.Student": "test", "example.Librarian": "Test"}

        generator = get_clean_generator_no_init(generator_config)

        generator.connect_signals()

        output = mock_stdout.getvalue().strip().split("\n")

        assert output == expected_output

    @staticmethod
    def test_connect_signals_lookup_error():
        """
        Tests that for a not existing model, a ProvenanceGeneratorException is raised.
        """
        generator_config = ProvenanceGeneratorConfiguration()
        key = "example.NotExistingModel"
        generator_config.entities = {key: "test"}

        generator = get_clean_generator_no_init(generator_config)

        with pytest.raises(ProvenanceGeneratorException,
                           match=f"Model {key} not existing. Please remove it from the settings."):
                generator.connect_signals()


    @patch("django_prov.generator.ProvenanceGenerator.handle_post_save")
    @patch("django_prov.generator.ProvenanceGenerator.handle_pre_save")
    def test_save_call_tracked(self, pre_mock, post_mock):
        """
        Tests that for a model that is tracked the correct handlers are called.
        """
        generator_config = ProvenanceGeneratorConfiguration()
        generator_config.entities = {"example.Book": "tracked"}

        generator = get_clean_generator_no_init(generator_config)

        generator.connect_signals()

        book = Book.objects.create(isbn="1234567891234", title="test-book", author="Test-Writer", pub_year=2024)

        args, kwargs = pre_mock.call_args_list[0]
        assert pre_mock.call_count == 1
        assert kwargs["sender"] == Book
        assert kwargs["instance"] == book

        args, kwargs = post_mock.call_args_list[0]
        assert post_mock.call_count == 1
        assert kwargs["sender"] == Book
        assert kwargs["instance"] == book

    @patch("django_prov.generator.ProvenanceGenerator.handle_post_save")
    @patch("django_prov.generator.ProvenanceGenerator.handle_pre_save")
    def test_save_call_not_tracked(self, pre_mock, post_mock):
        """
        Tests that for a model that is not tracked no handlers are called.
        """
        generator_config = ProvenanceGeneratorConfiguration()
        generator_config.entities = {"example.Borrowing": "not_tracked"}

        generator = get_clean_generator_no_init(generator_config)

        generator.connect_signals()

        book = Book.objects.create(isbn="1234567891234", title="test-book", author="Test-Writer", pub_year=2024)

        assert pre_mock.call_count == 0
        assert post_mock.call_count == 0

    @patch("django_prov.generator.ProvenanceGenerator.handle_m2m_changed")
    @patch("django_prov.generator.ProvenanceGenerator.handle_post_save")
    @patch("django_prov.generator.ProvenanceGenerator.handle_pre_save")
    def test_m2m_call_add(self,pre_mock, post_mock, m2m_mock):
        """
        Tests that for a model with ManyToManyFields the correct handlers are called when objects are added to the fields.
        """
        generator_config = ProvenanceGeneratorConfiguration()
        generator_config.entities = {"example.Borrowing": "tracked"}

        generator = get_clean_generator_no_init(generator_config)

        generator.connect_signals()

        user = User.objects.create(username="testuser")
        student = Student.objects.create(matrikelnr=1234567, person=user)
        book = Book.objects.create(isbn="1234567891234", title="test-book", author="Test-Writer", pub_year=2024)
        borrowing = Borrowing.objects.create(student=student)
        assert pre_mock.call_count == 1
        assert post_mock.call_count == 1

        borrowing.ordered_books.add(book)
        # pre and post add
        assert m2m_mock.call_count == 2
        args, kwargs = m2m_mock.call_args_list[0]
        assert kwargs["instance"] == borrowing
        assert kwargs["sender"] == Book.ordered_books.through
        assert kwargs["action"] == "pre_add"

        args, kwargs = m2m_mock.call_args_list[1]
        assert kwargs["instance"] == borrowing
        assert kwargs["sender"] == Book.ordered_books.through
        assert kwargs["action"] == "post_add"

    @patch("django_prov.generator.ProvenanceGenerator.handle_m2m_changed")
    @patch("django_prov.generator.ProvenanceGenerator.handle_post_save")
    @patch("django_prov.generator.ProvenanceGenerator.handle_pre_save")
    def test_m2m_call_remove(self, pre_mock, post_mock, m2m_mock):
        """
        Tests that for a model with ManyToManyFields the correct handlers are called when objects are removed from the fields.
        """
        generator_config = ProvenanceGeneratorConfiguration()
        generator_config.entities = {"example.Borrowing": "tracked"}

        generator = get_clean_generator_no_init(generator_config)

        generator.connect_signals()

        user = User.objects.create(username="testuser")
        student = Student.objects.create(matrikelnr=1234567, person=user)
        book = Book.objects.create(isbn="1234567891234", title="test-book", author="Test-Writer", pub_year=2024)
        borrowing = Borrowing.objects.create(student=student)
        assert pre_mock.call_count == 1
        assert post_mock.call_count == 1

        borrowing.ordered_books.add(book)
        m2m_mock.reset_mock()
        borrowing.ordered_books.remove(book)
        # pre and post add
        assert m2m_mock.call_count == 2
        args, kwargs = m2m_mock.call_args_list[0]
        assert kwargs["instance"] == borrowing
        assert kwargs["sender"] == Book.ordered_books.through
        assert kwargs["action"] == "pre_remove"

        args, kwargs = m2m_mock.call_args_list[1]
        assert kwargs["instance"] == borrowing
        assert kwargs["sender"] == Book.ordered_books.through
        assert kwargs["action"] == "post_remove"

    @patch("django_prov.generator.ProvenanceGenerator.handle_m2m_changed")
    @patch("django_prov.generator.ProvenanceGenerator.handle_post_save")
    @patch("django_prov.generator.ProvenanceGenerator.handle_pre_save")
    def test_m2m_call_not_tracked(self, pre_mock, post_mock, m2m_mock):
        """
        Tests that the m2m handlers are not called when ManyToManyFields of not tracked models change.
        """
        generator_config = ProvenanceGeneratorConfiguration()
        generator_config.entities = {"example.Librarian": "tracked"}

        generator = get_clean_generator_no_init(generator_config)

        generator.connect_signals()

        user = User.objects.create(username="testuser")
        student = Student.objects.create(matrikelnr=1234567, person=user)
        book = Book.objects.create(isbn="1234567891234", title="test-book", author="Test-Writer", pub_year=2024)
        borrowing = Borrowing.objects.create(student=student)
        assert pre_mock.call_count == 0
        assert post_mock.call_count == 0

        borrowing.ordered_books.add(book)
        assert m2m_mock.call_count == 0
