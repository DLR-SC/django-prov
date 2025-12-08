from unittest.mock import patch

from django.test import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration
from example.models import Book
from tests.utils.configs import DEFAULT_PROVENANCE
from tests.utils.utils import clean_test_settings, get_clean_generator_init


class SingleObjectsIntegrationTest(TestCase):
    """
    Tests that the ProvenanceGenerator creates the correct records for simple cases.
    """
    @patch("sys.stdout.write")
    def test_prov_record_not_all_fields_specified(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator creates a record that contains all specified fields + the id of a models object.
        """
        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': ['id', 'title', 'isbn', 'author', 'pub_year'],}

        prov_configuration = ProvenanceGeneratorConfiguration(prov_settings)
        generator = get_clean_generator_init(prov_configuration)

        book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)

        record = generator.document.get_records()[0]
        assert len(record.attributes) == len(prov_settings["ENTITIES"]["example.Book"]) + 1

    @patch("sys.stdout.write")
    def test_prov_record__all_fields_specified(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator creates a record that contains all fields of a models object.
        """
        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': True, }

        prov_configuration = ProvenanceGeneratorConfiguration(prov_settings)
        generator = get_clean_generator_init(prov_configuration)

        book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)

        record = generator.document.get_records()[0]
        assert len(record.attributes) == len(Book._meta.fields) + 1
