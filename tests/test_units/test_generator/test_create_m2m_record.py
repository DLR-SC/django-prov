from unittest.mock import patch, call

from django.contrib.auth.models import User

import prov.model as prov
from django.test import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration
from example.models import Student, Book, Borrowing
from tests.utils.utils import get_clean_generator_no_init


class CreateManyToManyRecordTest(TestCase):
    """
    Tests the create_many_to_many_record() method of ProvenanceGenerator.
    """
    def setUp(self):
        self.default_student_user = User.objects.create(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)
        self.borrowing = Borrowing.objects.create(student=self.default_student)

        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")

        self.borrowing_entity1 = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                      [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                       ('example:id', '1'),
                                       ])

        self.borrowing_entity2 = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                                     [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                                      ('example:id', '1'),
                                                      ])

        self.book_entity = self.document.entity("example:Book-1-2025-01-01_03-00-00",
                                           [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"),
                                            ('example:id', '1'),
                                            ])

        self.book_entity2 = self.document.entity("example:Book-1-2025-01-01_03-00-00",
                                                [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"),
                                                 ('example:id', '1'),
                                                 ])

    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    def test_create_many_to_many_record_success(self, mock_create_relation):
        """
        Tests that the create_many_to_many() function creates the correct entity and relations.
        """

        config = ProvenanceGeneratorConfiguration()
        config.entities = ["example.Borrowing"]
        generator = get_clean_generator_no_init(config)
        generator.document = self.document

        identifier = generator.create_many_to_many_record(self.borrowing_entity1, self.borrowing, self.borrowing._meta.many_to_many[0])

        record = list(generator.document.get_records())[-1]

        assert mock_create_relation.call_count == 1
        assert record.attributes[1][1] == "<class 'example.models.Borrowing'>"
        assert record.attributes[2][1] == "1"
        assert record.attributes[3][1] == "<class 'example.models.Book'>"
        mock_create_relation.assert_called_with(self.borrowing_entity1, identifier, prov.ProvMembership)

    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    def test_create_many_to_many_record_not_tracked(self, mock_create_relation):
        """
        Tests that the create_many_to_many() function does not create a record when the underlying model is not tracked.
        """
        config = ProvenanceGeneratorConfiguration()
        config.entities = ["example.NoTrackedModel"]
        generator = get_clean_generator_no_init(config)
        generator.document = self.document

        identifier = generator.create_many_to_many_record(self.borrowing_entity1, self.borrowing,
                                                          self.borrowing._meta.many_to_many[0])

        assert mock_create_relation.call_count == 0
        assert identifier is None
