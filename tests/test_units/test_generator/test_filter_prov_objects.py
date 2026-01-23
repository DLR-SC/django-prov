# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from unittest.mock import patch

import prov.model as prov
from django.test import TestCase

from tests.utils.utils import get_clean_generator_init


class FilterProvObjectsTest(TestCase):
    """
    Tests the filter_prov_objects() method of ProvenanceGenerator.
    """

    def setUp(self):
        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")
        self.entity_1 = self.document.entity("example:Book-1-2025-01-01_00-00-00",
                                   [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"), ('example:id', '1'),
                                    ('example:title', 'Test1')])
        self.entity_2 = self.document.entity("example:Book-1-2025-01-01_01-00-00",
                                   [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"), ('example:id', '1'),
                                    ('example:title', 'AlteredTitle')])
        self.entity_3 = self.document.entity("example:Book-1-2025-01-01_02-00-00",
                                   [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"), ('example:id', '1'),
                                    ('example:title', 'AlteredTitle2')])
        self.entity_4 = self.document.entity("example:Book-2-2025-01-01_04-00-00",
                                   [(prov.PROV_TYPE, "example:<class 'example.models.Book'>"), ('example:id', '2'),
                                    ('example:title', 'OtherTitle')])
        self.entity_5 = self.document.entity("example:Student-1-2025-01-01_02-00-00",
                        [(prov.PROV_TYPE, "example:<class 'example.models.Student'>"), ('example:id', '1'),
                         ('example:name', 'Test1')])

    @patch("sys.stdout.write")
    def test_filter_prov_objects_list(self, mock_stdout):
        """
        Tests if
        """
        generator = get_clean_generator_init()
        generator.document = self.document

        prov_objects_1 = generator.filter_prov_objects("example", "Book", 1, prov.ProvEntity)
        self.assertEqual(len(prov_objects_1), 3)

        prov_objects_2 = generator.filter_prov_objects("example", "Student", 1, prov.ProvEntity)
        self.assertEqual(len(prov_objects_2), 1)

        prov_objects_3 = generator.filter_prov_objects("example", "Book", 3, prov.ProvEntity)
        self.assertEqual(len(prov_objects_3), 0)

    @patch("sys.stdout.write")
    def test_check_derivation(self, mock_stdout):
        """
        Tests that the ProvenanceGenerator generates the correct number of derivations for entities
        """

        generator = get_clean_generator_init()
        generator.document = self.document

        generator.check_derivation("example", "Book", 1)

        derivations = list(generator.document.get_records(prov.ProvDerivation))
        self.assertEqual(len(derivations), 2)

        self.assertEqual(self.entity_2.identifier, derivations[0].args[0])
        self.assertEqual(self.entity_1.identifier, derivations[0].args[1])

        self.assertEqual(self.entity_3.identifier, derivations[1].args[0])
        self.assertEqual(self.entity_2.identifier, derivations[1].args[1])


    def test_check_derivation_one_derivation_existing_already(self):
        """
        Tests that even if there is a derivation existing already, the overall count of derivations stays correct.
        """
        generator = get_clean_generator_init()
        generator.document = self.document
        generator.document.wasDerivedFrom(self.entity_2, self.entity_1)

        generator.check_derivation("example", "Book", 1)

        derivations = list(generator.document.get_records(prov.ProvDerivation))
        self.assertEqual(len(derivations), 2)

        self.assertEqual(self.entity_2.identifier, derivations[0].args[0])
        self.assertEqual(self.entity_1.identifier, derivations[0].args[1])

        self.assertEqual(self.entity_3.identifier, derivations[1].args[0])
        self.assertEqual(self.entity_2.identifier, derivations[1].args[1])
