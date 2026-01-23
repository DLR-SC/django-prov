# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from unittest.mock import patch

from django.contrib.auth.models import User

import prov.model as prov
from django.test import TestCase
from prov.identifier import Namespace

from django_prov.configuration import ProvenanceGeneratorConfiguration
from example.models import Student, Borrowing
from tests.utils.utils import get_clean_generator_no_init


class CreateForeignKeyEntryTest(TestCase):
    """
    Tests the create_foreign_key() method of ProvenanceGenerator.
    """
    def setUp(self):
        self.default_student_user = User.objects.create(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.borrowing = Borrowing.objects.create(student=self.default_student)

        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")

        self.borrowing_entity = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                      [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                       ('example:id', '1'),
                                       ])

        self.student_entity = self.document.entity("example:Student-1-2025-01-01_02-00-00",
                                      [(prov.PROV_TYPE, "example:<class 'example.models.Student'>"),
                                       ('example:id', '1'),
                                       ])


    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    @patch("django_prov.generator.ProvenanceGenerator.create_prov_record")
    def test_create_foreign_key_entry_entities(self, mock_create_prov_record, mock_create_relation):
        """
        Tests that the correct ProvRecord is created when a model is listed in the 'ENTITIES' section in the config.
        """
        generator = get_clean_generator_no_init()
        generator.config = ProvenanceGeneratorConfiguration()
        generator.config.entities = {"example.Student": "irrelevant"}
        mock_create_prov_record.return_value = self.student_entity.identifier

        generator.create_foreign_key_entry(self.borrowing_entity, Student, 1)

        assert mock_create_prov_record.call_count == 1
        mock_create_prov_record.assert_called_with(Student, self.default_student)
        assert mock_create_relation.call_count == 1
        mock_create_relation.assert_called_with(self.borrowing_entity, self.student_entity.identifier, prov.ProvMembership)

    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    @patch("django_prov.generator.ProvenanceGenerator.create_prov_record")
    def test_create_foreign_key_entry_agents(self, mock_create_prov_record, mock_create_relation):
        """
        Tests that the correct ProvRecord is created when a model is listed in the 'AGENTS' section in the config.
        """
        generator = get_clean_generator_no_init()
        generator.config = ProvenanceGeneratorConfiguration()
        generator.config.agents = {"auth.User": "irrelevant"}
        identifier = "auth:user-1-2025-01-01_02-00-00"
        mock_create_prov_record.return_value = identifier

        generator.create_foreign_key_entry(self.student_entity, User, 1)

        assert mock_create_prov_record.call_count == 1
        mock_create_prov_record.assert_called_with(User, self.default_student_user)
        assert mock_create_relation.call_count == 1
        mock_create_relation.assert_called_with(str(self.student_entity.identifier), identifier, prov.ProvAttribution)

    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    @patch("django_prov.generator.ProvenanceGenerator.create_prov_record")
    def test_create_foreign_key_entry_auth_namespace(self, mock_create_prov_record, mock_create_relation):
        """
        Tests that the correct ProvRecord is created when a model (e.g. User) is part of djangos 'auth' module.
        """

        generator = get_clean_generator_no_init()
        generator.config = ProvenanceGeneratorConfiguration()
        generator.config.namespaces = [Namespace("auth", "example.org/auth")]
        identifier = "auth:user-1-2025-01-01_02-00-00"
        mock_create_prov_record.return_value = identifier

        generator.create_foreign_key_entry(self.student_entity, User, 1)

        assert mock_create_prov_record.call_count == 1
        mock_create_prov_record.assert_called_with(User, self.default_student_user)
        assert mock_create_relation.call_count == 1
        mock_create_relation.assert_called_with(str(self.student_entity.identifier), identifier, prov.ProvAttribution)
