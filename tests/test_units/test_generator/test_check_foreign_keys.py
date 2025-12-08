from unittest.mock import patch, call

from django.contrib.auth.models import User

import prov.model as prov
from django.test import TestCase

from example.models import Student, Book, Borrowing
from tests.utils.utils import get_clean_generator_no_init


class CheckForeignKeyTest(TestCase):
    """
    Tests the check_foreign_key() method of ProvenanceGenerator.
    """
    def setUp(self):
        self.default_student_user = User.objects.create(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)
        self.borrowing = Borrowing.objects.create(student=self.default_student)

        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")

        self.borrowing_entity = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                      [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                       ('example:id', '1'),
                                       ])

        self.book_entity = self.document.entity("example:Book-1-2025-01-01_02-00-00",
                                           [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"),
                                            ('example:id', '1'),
                                            ])

    @patch("django_prov.generator.ProvenanceGenerator.create_many_to_many_record")
    @patch("django_prov.generator.ProvenanceGenerator.create_foreign_key_entry")
    @patch("django_prov.generator.ProvenanceGenerator.filter_prov_objects")
    def test_check_foreign_keys_previous_prov_obj(self, mock_filter_prov_objects, mock_create_foreign_key_entry,
                                            mock_create_m2m):
        """
        Tests that the correct ForeignKey and ManyToMany ProvRecords are created for a ProvRecord of an object.
        Assumes that there is an existing ProvRecord for the original object already.
        """
        generator = get_clean_generator_no_init()

        mock_filter_prov_objects.return_value = [self.borrowing_entity]

        generator.check_foreign_keys("identifier", Borrowing, self.borrowing)
        assert mock_create_foreign_key_entry.call_count == 1
        mock_create_foreign_key_entry.assert_called_with(self.borrowing_entity, Student, 1)

        assert mock_create_m2m.call_count == 2
        assert mock_create_m2m.call_args_list == [
            call(self.borrowing_entity, self.borrowing, Borrowing.ordered_books.field),
            call(self.borrowing_entity, self.borrowing, Borrowing.borrowed_books.field),
        ]


    @patch("django_prov.generator.ProvenanceGenerator.create_many_to_many_record")
    @patch("django_prov.generator.ProvenanceGenerator.create_foreign_key_entry")
    @patch("django_prov.generator.ProvenanceGenerator.filter_prov_objects")
    def test_check_foreign_keys_no_previous_prov_obj(self, mock_filter_prov_objects, mock_create_foreign_key_entry,
                                                     mock_create_m2m):
        """
        Tests that the correct ForeignKey and ManyToMany ProvRecords are created for a ProvRecord of an object.
        Assumes that there is no already existing ProvRecord for the original object.
        """

        generator = get_clean_generator_no_init()

        mock_filter_prov_objects.return_value = []

        generator.check_foreign_keys(self.borrowing_entity, Borrowing, self.borrowing)

        assert mock_create_foreign_key_entry.call_count == 1
        mock_create_foreign_key_entry.assert_called_with(self.borrowing_entity, Student, 1)

        # two calls because even if the m2m_fields are empty, they are crawled
        assert mock_create_m2m.call_count == 2
        assert mock_create_m2m.call_args_list == [
            call(self.borrowing_entity, self.borrowing, Borrowing.ordered_books.field),
            call(self.borrowing_entity, self.borrowing, Borrowing.borrowed_books.field),
        ]

    @patch("django_prov.generator.ProvenanceGenerator.create_many_to_many_record")
    @patch("django_prov.generator.ProvenanceGenerator.create_foreign_key_entry")
    @patch("django_prov.generator.ProvenanceGenerator.filter_prov_objects")
    def test_check_foreign_keys_with_m2m_object(self, mock_filter_prov_objects, mock_create_foreign_key_entry,
                                            mock_create_m2m):
        """
        Tests that when the ManyToMany Field of an object already holds objects, the corresponding ProvRecords for those are created.
        Assumes that there is no existing ProvRecord for the original object.
        """

        generator = get_clean_generator_no_init()

        self.borrowing.ordered_books.add(self.book)

        mock_filter_prov_objects.return_value = []
        mock_create_m2m.return_value = "m2m_identifier"

        generator.check_foreign_keys(self.borrowing_entity, Borrowing, self.borrowing)

        # one more call because the added book is one more foreign key
        assert mock_create_foreign_key_entry.call_count == 2
        assert mock_create_foreign_key_entry.call_args_list == [
            call(self.borrowing_entity, Student, 1),
            call(mock_create_m2m.return_value, Book, 1),
        ]

        assert mock_create_m2m.call_count == 2
        assert mock_create_m2m.call_args_list == [
            call(self.borrowing_entity, self.borrowing, Borrowing.ordered_books.field),
            call(self.borrowing_entity, self.borrowing, Borrowing.borrowed_books.field),
        ]

    @patch("django_prov.generator.ProvenanceGenerator.create_many_to_many_record")
    @patch("django_prov.generator.ProvenanceGenerator.create_foreign_key_entry")
    @patch("django_prov.generator.ProvenanceGenerator.filter_prov_objects")
    def test_check_foreign_keys_no_foreign_keys(self, mock_filter_prov_objects, mock_create_foreign_key_entry,
                                                mock_create_m2m):
        """
        Tests that no ProvRecords are created when an object doesn't have ForeignKeys or ManyToManyFields.
        """

        generator = get_clean_generator_no_init()

        mock_filter_prov_objects.return_value = []

        generator.check_foreign_keys(self.book_entity, Book, self.book)
        assert mock_create_foreign_key_entry.call_count == 0
        assert mock_create_m2m.call_count == 0
