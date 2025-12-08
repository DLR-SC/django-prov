from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration, ProvenanceGeneratorConfigurationException
from django_prov.generator import ProvenanceGeneratorException, ProvenanceGeneratorWarning
from example.models import Book
from tests.utils.configs import DEFAULT_PROVENANCE
from tests.utils.utils import get_clean_generator_init, clean_test_settings


class GetFieldsToRecordTest(TestCase):
    """
    Tests the get_fields_to_record() method of ProvenanceGenerator.
    """

    @patch("sys.stdout.write")
    def test_get_specific_fields_to_record(self, mock_stdout):
        """
        Tests if the method returns the specific fields of an object which are listed in settings.py
        """
        book = Book(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)
        config = clean_test_settings(DEFAULT_PROVENANCE)
        config["ENTITIES"] = {'example.Book': ['id', 'title', 'isbn'],}
        prov_configuration = ProvenanceGeneratorConfiguration(config)
        generator = get_clean_generator_init(prov_configuration)

        fields = generator.get_fields_to_record(book)

        self.assertEqual(len(fields[0]), len(generator.config.entities['example.Book']))

    @patch("sys.stdout.write")
    def test_get_all_fields_to_record(self, mock_stdout):
        """
        Tests if the method returns all fields of an object if it is set to True in settings.py
        """
        book = Book(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)
        user = User(username="TestUser")
        config = clean_test_settings(DEFAULT_PROVENANCE)
        config["ENTITIES"] = {'example.Book': True, }
        config["AGENTS"] = {'auth.User': True, }
        prov_configuration = ProvenanceGeneratorConfiguration(config)
        generator = get_clean_generator_init(prov_configuration)

        fields = generator.get_fields_to_record(book)

        self.assertEqual(len(fields[0]), len(book._meta.fields))

    @patch("sys.stdout.write")
    def test_get_fields_to_record_model_not_existing(self, mock_stdout):
        """
        Tests if the method raises an Exception when a model is not declared correctly in settings.py
        """
        book = Book(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)
        config = clean_test_settings(DEFAULT_PROVENANCE)
        config["ENTITIES"] = {}
        prov_configuration = ProvenanceGeneratorConfiguration(config)
        generator = get_clean_generator_init(prov_configuration)

        fields = generator.get_fields_to_record(book)

        assert fields == ([], None)
