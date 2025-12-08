import os
import re
import tempfile
from pathlib import Path
from unittest.mock import patch

import prov.model as prov
import pytest
from django.test import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration
from django_prov.generator import ProvenanceGeneratorWarning
from tests.utils.utils import get_clean_generator_init


class PrintDocumentTest(TestCase):
    """
    Tests the print_document() method of ProvenanceGenerator.
    """
    def setUp(self):
        self.document = prov.ProvDocument()
        self.document.set_default_namespace("example.org")
        self.document.add_namespace("example", "example.org/example/")

        self.borrowing_entity = self.document.entity("example:Borrowing-1-2025-01-01_02-00-00",
                                                 [(prov.PROV_TYPE, "example:<class 'example.models.Borrowing'>"),
                                                  ('example:id', '1'),
                                                  ])


    def test_print_document_all_formats(self,):
        """
        Tests that the ProvenanceGeneratorConfiguration creates the correct output files if specified.
        """
        generator = get_clean_generator_init()
        generator.config = ProvenanceGeneratorConfiguration()
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]
        valid_graphic_formats = ["png", "svg", "pdf"]


        with tempfile.TemporaryDirectory() as d:
            generator.config.output = {"PATH": d, "SERIALIZE": valid_serialize_formats,
                                       "GRAPHIC": valid_graphic_formats}

            assert len(os.listdir(d)) == 0

            generator.document = self.document
            generator.print_document()

            assert len(os.listdir(d)) == len(valid_serialize_formats) + len(valid_graphic_formats)


    def test_print_document_no_path(self, ):
        """
        Tests that the ProvenanceGenerator prints documents to the cli when not path is provided.
        """
        generator = get_clean_generator_init()
        generator.config = ProvenanceGeneratorConfiguration()
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]

        with patch("sys.stdout.write") as mock_stdout:
            generator.config.output = {"PATH": None, "SERIALIZE": valid_serialize_formats, "GRAPHIC": []}

            generator.document = self.document
            generator.print_document()

            all_output = mock_stdout.call_args_list
            all_output = [c for c in all_output if not (c.args == ("\n",))]
            assert len(all_output) == len(valid_serialize_formats)

            regex_pattern = [
                r'document\n',
                r'  default <example.org>\n',
                r'  prefix example <example\.org/example/>\n',
                r'  \n',
                r'  entity\(example:Borrowing-1-.*, .*\)\n',
                r'endDocument'
            ]
            output = all_output[0].args[0].strip().splitlines(keepends=True)
            for out, pattern in zip(output, regex_pattern):
                assert re.fullmatch(pattern, out), f"{out!r} did not match {pattern!r}"

    def test_print_document_no_path_graphic_warning(self):
        """
        Tests that the ProvenanceGenerator warns when graphical formats are specified but no path is provided.
        """
        generator = get_clean_generator_init()
        generator.config = ProvenanceGeneratorConfiguration()
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]
        valid_graphic_formats = ["png", "svg", "pdf"]


        with pytest.warns(ProvenanceGeneratorWarning,
                           match="Without a path, no graphic can be printed. Please adapt your configuration."):
            generator.config.output = {"PATH": None, "SERIALIZE": valid_serialize_formats, "GRAPHIC": valid_graphic_formats}

            generator.document = self.document
            generator.print_document()
