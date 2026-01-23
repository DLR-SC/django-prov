# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from unittest.mock import patch, call

import prov.model as prov
from django.test import TestCase

from tests.utils.utils import get_clean_generator_no_init


class CheckDerivationTest(TestCase):
    """
    Tests the check_derivation() method of ProvenanceGenerator.
    """
    def setUp(self):
        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")

        self.borrowing_entity1 = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                      [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                       ('example:id', '1'),
                                       ])

        self.borrowing_entity2 = self.document.entity("example:Borrowing-1-2025-01-01_03-00-00",
                                                     [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                                      ('example:id', '1'),
                                                      ])
        self.borrowing_entity3 = self.document.entity("example:Borrowing-1-2025-01-01_04-00-00",
                                                      [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                                       ('example:id', '1'),
                                                       ])

    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    @patch("django_prov.generator.ProvenanceGenerator.filter_prov_objects")
    def test_check_derivation_success(self, mock_filter_prov_objects, mock_create_relation):
        """
        Tests that check_derivation() creates the correct ProvDerivations between ProvRecords of the same object.
        """
        generator = get_clean_generator_no_init()
        generator.document = self.document
        mock_filter_prov_objects.return_value = [self.borrowing_entity1, self.borrowing_entity2, self.borrowing_entity3]

        generator.check_derivation("example", "Borrowing", 1)

        assert mock_create_relation.call_count == 2
        assert mock_create_relation.call_args_list == [
            call(self.borrowing_entity2.identifier._str, self.borrowing_entity1.identifier._str, prov.ProvDerivation),
            call(self.borrowing_entity3.identifier._str, self.borrowing_entity2.identifier._str, prov.ProvDerivation),
            ]

    @patch("django_prov.generator.ProvenanceGenerator.create_relation")
    @patch("django_prov.generator.ProvenanceGenerator.filter_prov_objects")
    def test_check_derivation_already_existing(self, mock_filter_prov_objects, mock_create_relation):
        """
        Tests that the check_derivation() function does not create another ProvDerivation
         when the relationship between two records is already existing.
        """
        generator = get_clean_generator_no_init()
        generator.document = self.document

        self.document.wasDerivedFrom(self.borrowing_entity2, self.borrowing_entity1)
        self.document.wasDerivedFrom(self.borrowing_entity3, self.borrowing_entity2)
        mock_filter_prov_objects.return_value = [self.borrowing_entity1, self.borrowing_entity2, self.borrowing_entity3]

        generator.check_derivation("example", "Borrowing", 1)

        assert mock_create_relation.call_count == 0
