# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from unittest.mock import patch, call

import prov.model as prov
from django.test import TestCase

from tests.utils.utils import get_clean_generator_no_init


class CheckIsAlreadyExistingTest(TestCase):
    """
    Tests the check_is_already_existing() method of ProvenanceGenerator.
    """
    def setUp(self):
        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")

        self.borrowing_entity1 = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                      [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                       ('example:id', '1'),
                                       ('example:student_id', '1'),
                                       ('example:responsible_librarian_id', 'None'),
                                       ('example:status', 'O')
                                       ])

        self.attributes_1 =[(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                                      ('example:id', '1'),
                                                      ('example:student_id', '1'),
                                                      ('example:responsible_librarian_id', 'None'),
                                                      ('example:status', 'O')
                                                      ]
        self.attributes_2 = [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                                       ('example:id', '1'),
                                                       ('example:student_id', '1'),
                                                       ('example:responsible_librarian_id', 'None'),
                                                       ('example:status', 'B')
                                                       ]


    def test_check_is_already_existing_true(self):
        """
        Tests that check_is_already_existing() returns True if a records attributes are equal to a list of attributes.
        """
        generator = get_clean_generator_no_init()

        return_val = generator.check_is_already_existing(self.borrowing_entity1, self.attributes_1)

        assert return_val == True

    def test_check_is_already_existing_false(self):
        """
        Tests that check_is_already_existing() returns False if a records attributes are not equal to a list of attributes.
        """
        generator = get_clean_generator_no_init()

        return_val = generator.check_is_already_existing(self.borrowing_entity1, self.attributes_2)

        assert return_val == False
