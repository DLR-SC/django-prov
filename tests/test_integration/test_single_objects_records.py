# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

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
    def test_prov_record_all_fields_specified(self, mock_stdout):
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


    @patch("sys.stdout.write")
    def test_prov_record_all_fields_specified_max_field_length(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator creates a record that is shortened if 'MAX_FIELD_VALUE_LENGTH' is specified.
        """
        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': True, }
        max_field_value_length = 5
        prov_settings["OTHER"] = {"MAX_FIELD_VALUE_LENGTH": max_field_value_length}
        prov_configuration = ProvenanceGeneratorConfiguration(prov_settings)
        generator = get_clean_generator_init(prov_configuration)

        book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)

        record = generator.document.get_records()[0]
        assert len(record.attributes) == len(Book._meta.fields) + 1

        for attribute in record.attributes[1:]:
            assert len(attribute[1]) <= max_field_value_length + len("...")

    @patch("sys.stdout.write")
    def test_prov_record_all_fields_specified_no_max_field_length(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator creates a record that is not shortened if 'MAX_FIELD_VALUE_LENGTH' is not specified.
        """
        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': True, }
        prov_configuration = ProvenanceGeneratorConfiguration(prov_settings)
        generator = get_clean_generator_init(prov_configuration)

        book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)

        record = generator.document.get_records()[0]
        assert len(record.attributes) == len(Book._meta.fields) + 1

        for field, attribute_value in zip(book._meta.fields, record.attributes[1:]):
            assert len(str(getattr(book, field.attname))) == len(attribute_value[1])
