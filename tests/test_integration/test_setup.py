# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from io import StringIO
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.conf import settings as django_settings
from prov.model import ProvDocument

from django_prov.configuration import ProvenanceGeneratorConfiguration, ProvenanceGeneratorConfigurationException
from django_prov.generator import ProvenanceGenerator
from tests.utils.configs import DEFAULT_PROVENANCE
from tests.utils.utils import clean_test_settings, get_clean_generator_init


class ProvenanceGeneratorSetupTest(TestCase):
    """
    Tests that the ProvenanceGenerator is set up correctly.
    """
    def setUp(self):
        self.default_student_user = User.objects.create_user(username="Student", password="s")


    @patch("sys.stdout", new_callable=StringIO)
    def test_init_success_django_settings(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator is set up correctly when using the Django Settings.
        """
        expected_output = [
            "Initialized Generator",
            "Connected pre <class 'example.models.Book'>",
            "Connected post <class 'example.models.Book'>",
            "Connected pre <class 'example.models.Borrowing'>",
            "Connected post <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
        ]

        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': True, 'example.Borrowing': True }

        with override_settings(PROVENANCE=prov_settings):
            generator = get_clean_generator_init()
            output = mock_stdout.getvalue().strip().split("\n")
            self.assertIsInstance(generator, ProvenanceGenerator)
            self.assertEqual(generator.config.default_namespace.uri, "example.org/")
            self.assertEqual(output, expected_output)
            for namespace in generator.document.namespaces:
                self.assertIn(namespace.prefix, django_settings.PROVENANCE["NAMESPACES"]["EXTRA"])

    @patch("sys.stdout", new_callable=StringIO)
    def test_init_success_non_django_settings(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator is set up correctly when the configuration is passed via a dictionary.
        """
        expected_output = [
            "Initialized Generator",
            "Connected pre <class 'example.models.Book'>",
            "Connected post <class 'example.models.Book'>",
            "Connected pre <class 'example.models.Borrowing'>",
            "Connected post <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
        ]

        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': True, 'example.Borrowing': True}

        generator = get_clean_generator_init(prov_settings)
        output = mock_stdout.getvalue().strip().split("\n")

        self.assertIsInstance(generator, ProvenanceGenerator)
        self.assertEqual(generator.config.default_namespace.uri, "example.org/")
        self.assertEqual(output, expected_output)
        for namespace in generator.document.namespaces:
            self.assertIn(namespace.prefix, django_settings.PROVENANCE["NAMESPACES"]["EXTRA"])

    @patch("sys.stdout", new_callable=StringIO)
    def test_init_success_generator_config_settings(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator is set up correctly when the configuration is passed via a ProvenanceGeneratorConfiguration object.
        """
        expected_output = [
            "Initialized Generator",
            "Connected pre <class 'example.models.Book'>",
            "Connected post <class 'example.models.Book'>",
            "Connected pre <class 'example.models.Borrowing'>",
            "Connected post <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
        ]

        prov_settings = clean_test_settings(DEFAULT_PROVENANCE)
        prov_settings["ENTITIES"] = {'example.Book': True, 'example.Borrowing': True}

        config = ProvenanceGeneratorConfiguration(prov_settings)
        generator = get_clean_generator_init(config)
        output = mock_stdout.getvalue().strip().split("\n")

        self.assertIsInstance(generator, ProvenanceGenerator)
        self.assertEqual(generator.config.default_namespace.uri, "example.org/")
        self.assertEqual(output, expected_output)
        for namespace in generator.document.namespaces:
            self.assertIn(namespace.prefix, django_settings.PROVENANCE["NAMESPACES"]["EXTRA"])

    @staticmethod
    def test_init_type_error():
        """
        Tests that a ProvenanceGeneratorConfigurationException is raised when the ProvenanceGenerator is initialized incorrectly.
        """
        with pytest.raises(ProvenanceGeneratorConfigurationException):
            generator = get_clean_generator_init("wrong")

    @staticmethod
    def test_create_new_document():
        """
        Tests that the ProvenanceGenerator correctly creates a new ProvDocument with Namespaces.
        """
        prov_configuration = ProvenanceGeneratorConfiguration(DEFAULT_PROVENANCE)

        generator = get_clean_generator_init(prov_configuration)

        generator.create_new_document()

        assert generator.document == ProvDocument()
        assert generator.document.default_ns_uri == DEFAULT_PROVENANCE["NAMESPACES"]["DEFAULT"]
        assert len(generator.document.namespaces) == len(DEFAULT_PROVENANCE["NAMESPACES"]["EXTRA"])

