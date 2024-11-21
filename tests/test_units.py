import tempfile
import os

from io import StringIO

import prov.model as prov
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from unittest.mock import patch

from django_prov.generator import ProvenanceGenerator
from example.models import Book, Borrowing, Student, Librarian
from tests.regex_patterns import *


def get_generator(path=None, serialize=None, graphic=None):
    if serialize is None:
        serialize = []
    if graphic is None:
        graphic = []
    settings.PROVENANCE["OUTPUT"] = {"PATH": path, "SERIALIZE": serialize, "GRAPHIC": graphic}
    generator = ProvenanceGenerator.get("")
    generator.create_new_document()
    return generator

class ProvenanceGeneratorTest(TestCase):
    def setUp(self) -> None:
        # kann vllt weg
        self.entity = prov.ProvEntity("example:Student-1",
                                    ((prov.PROV_TYPE, "libbackend: <class 'libbackend.models.Student'>"),
                                            ('example:id', "1"), ('example:person', "1"),
                                            ('example:other_attributes', "..."))
                                    )

        self.default_student_user = User.objects.create(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.default_librarian_user = User.objects.create(username="Librarian", password="l")
        self.book = Book.objects.create(isbn="1234567891234", title="test-book", author="Test-Writer", pub_year=2024)
        self.borrowing = Borrowing.objects.create(student=self.default_student)

        """self.borrowing = Borrowing.objects.create(student=self.default_student)
        self.borrowing.ordered_books.add(self.book)"""

    @patch("sys.stdout", new_callable=StringIO)
    def test_init(self, mock_stdout):
        expected_output = [
            "Initialized Generator",
            "Connected pre <class 'example.models.Book'>",
            "Connected post <class 'example.models.Book'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected m2m <class 'example.models.Borrowing'>",
            "Connected pre <class 'example.models.Borrowing'>",
            "Connected post <class 'example.models.Borrowing'>",
            "Connected pre <class 'example.models.Student'>",
            "Connected post <class 'example.models.Student'>",
            "Connected pre <class 'example.models.Librarian'>",
            "Connected post <class 'example.models.Librarian'>",
        ]

        generator = ProvenanceGenerator("test-generator/")
        output = mock_stdout.getvalue().strip().split("\n")
        self.assertIsInstance(generator, ProvenanceGenerator)
        self.assertEqual(generator.default_namespace, "test-generator/")
        self.assertEqual(output, expected_output)
        for namespace in generator.document.namespaces:
            self.assertIn(namespace.prefix, settings.PROVENANCE["NAMESPACES"]["EXTRA"])

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_init_wrong_setting(self, mock_stderr, mock_stdout):
            settings.PROVENANCE["ENTITIES"] = ["example.NotExistingModel"]
            with self.assertRaises(SystemExit) as raised:
                generator = ProvenanceGenerator("test-generator")
            self.assertEqual(raised.exception.code, -1)
            err = mock_stderr.getvalue()
            self.assertEqual("Model example.NotExistingModel not existing. Please remove it from the settings.\n", err)

    @patch('sys.stderr', new_callable=StringIO)
    def test_init_no_default_namespace(self, mock_stderr):
        with self.assertRaises(SystemExit) as raised:
            generator = ProvenanceGenerator(None)
        self.assertEqual(raised.exception.code, -1)
        err = mock_stderr.getvalue()
        self.assertEqual("No default namespace added. Please add one to the settings.\n", err)

    def test_singleton(self):
        generator = get_generator()
        self.assertIsInstance(generator, ProvenanceGenerator)
        self.assertEqual(generator.default_namespace, settings.PROVENANCE["NAMESPACES"]["DEFAULT"])

        entity = generator.document.entity("example:Student-1",
                                           ((prov.PROV_TYPE, "libbackend: <class 'libbackend.models.Student'>"),
                                            ('example:id', "1"), ('example:person', "1"),
                                            ('example:other_attributes', "..."))
                                           )

        generator2 = ProvenanceGenerator.get("")
        self.assertIn(entity, generator2.document.records)
        self.assertEqual(generator, generator2)

    @patch("sys.stdout", new_callable=StringIO)
    def test_new_prov_document(self, mock_stdout):
        generator = ProvenanceGenerator.get("")
        entity = generator.document.entity("example:Student-1")

        self.assertIn(entity, generator.document.records)

        generator.create_new_document()

        self.assertNotIn(entity, generator.document.records)
        self.assertEqual(generator.document.records, [])
        print("Hi")

    def test_output_document_valid_format_with_path(self):
        generator = get_generator()
        settings.PROVENANCE["OUTPUT"]["SERIALIZE"] = ["n", "xml", "json", "rdf"]
        settings.PROVENANCE["OUTPUT"]["GRAPHIC"] = ["png", "svg", "pdf"]
        formats = settings.PROVENANCE["OUTPUT"]["SERIALIZE"] + settings.PROVENANCE["OUTPUT"]["GRAPHIC"]

        entity = generator.document.entity("example:Student-1")
        with tempfile.TemporaryDirectory() as temp:
            settings.PROVENANCE["OUTPUT"]["PATH"] = temp + "/"
            generator.print_document()
            for file in os.listdir(temp):
                file_type = file.split(".")[1]
                if file_type in formats:
                    formats.remove(file_type)
                elif file_type == "txt" and "n" in formats:
                    formats.remove("n")
            self.assertEqual(formats, [])


    @patch("sys.stdout", new_callable=StringIO)
    def test_serialized_document_valid_format_no_path(self, mock_stdout=None):
        generator = get_generator()
        settings.PROVENANCE["OUTPUT"]["PATH"] = None
        settings.PROVENANCE["OUTPUT"]["SERIALIZE"] = ["n", "xml", "json", "rdf"]

        expected_json = '{"prefix": {"auth": "example.org/auth/", "django": "example.org/django/", "sys": "example.org/sys/", "example": "example.org/example/", "django_prov": "example.org/django_prov/", "default": "example.org/"}, "entity": {"example:Student-1": {}}}'
        expected_rdf = '@prefix example: <example.org/example/> .\n@prefix prov: <http://www.w3.org/ns/prov#> .\n\n{\n    example:Student-1 a prov:Entity .\n}\n\n'
        expected_provn = 'document\n  default <example.org/>\n  prefix auth <example.org/auth/>\n  prefix django <example.org/django/>\n  prefix sys <example.org/sys/>\n  prefix example <example.org/example/>\n  prefix django_prov <example.org/django_prov/>\n  \n  entity(example:Student-1)\nendDocument'
        expected_xml1 = "<?xml version='1.0' encoding='ASCII'?>\n"
        expected_xml2 = '<prov:document xmlns:auth="example.org/auth/" xmlns:django="example.org/django/" xmlns:sys="example.org/sys/" xmlns:example="example.org/example/" xmlns:django_prov="example.org/django_prov/" xmlns="example.org/" xmlns:prov="http://www.w3.org/ns/prov#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <prov:entity prov:id="example:Student-1"/>\n</prov:document>'

        entity = generator.document.entity("example:Student-1")
        generator.print_document()
        output = mock_stdout.getvalue()
        print("Hi")

        self.assertIn(expected_rdf, output)
        self.assertIn(expected_json, output)
        self.assertIn(expected_provn, output)
        self.assertIn(expected_xml1, output)
        self.assertIn(expected_xml2, output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_serialized_document_invalid_format(self, mock_stderr, mock_stdout):
        generator = get_generator()
        settings.PROVENANCE["OUTPUT"]["PATH"] = "*"
        settings.PROVENANCE["OUTPUT"]["SERIALIZE"] = ["foo", "foo123", "json"]
        settings.PROVENANCE["OUTPUT"]["GRAPHIC"] = ["graphic", "pdf"]
        expected_output0 = "[WinError 123] Die Syntax für den Dateinamen, Verzeichnisnamen oder die Datenträgerbezeichnung ist falsch: '*'"
        expected_output1 = "'foo' is not a valid serialization format. Please adapt your settings.py."
        expected_output2 = "'foo123' is not a valid serialization format. Please adapt your settings.py."
        expected_output3 = "'graphic' is not a valid graphical output format. Please adapt your settings.py."
        expected_output4 = "'Without a path, no graphic can be printed. Please adapt your settings.py"

        expected_json = '{"prefix": {"auth": "example.org/auth/", "django": "example.org/django/", "sys": "example.org/sys/", "example": "example.org/example/", "django_prov": "example.org/django_prov/", "default": "example.org/"}, "entity": {"example:Student-1": {}}}'


        entity = generator.document.entity("example:Student-1")
        generator.print_document()
        err = mock_stderr.getvalue()
        output = mock_stdout.getvalue()
        self.assertIn(expected_output0, err)
        self.assertIn(expected_output1, err)
        self.assertIn(expected_output2, err)
        self.assertIn(expected_output3, err)
        self.assertIn(expected_output4, err)
        self.assertIn(expected_json, output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_handle_m2m_changed(self, mock_stderr, mock_stdout):
        generator = get_generator()
        settings.PROVENANCE["OUTPUT"]["SERIALIZE"] = ["n"]
        before = Borrowing.objects.get(id=1)
        before.ordered_books.add(self.book)
        after = Borrowing.objects.get(id=1)
        generator.print_document()

        output = mock_stdout.getvalue()
        err = mock_stderr.getvalue()
        self.assertRegex(output, test_handle_m2m_changed_pattern)

    @patch("sys.stdout", new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_create_prov_record_student(self, mock_stderr, mock_stdout):
        generator = get_generator()
        value = generator.create_prov_record(self.default_student._meta.model, Student.objects.get(id=1))
        self.assertRegex(value, "example:Student-1-.*")

        generated_records = generator.document.get_records()
        for i in range(len(generated_records)):
            self.assertRegex(str(generated_records[i]), test_create_prov_record_student_pattern[i])


    def test_save(self):
        generator = get_generator()
        book = Book.objects.create(isbn="1234567891234", title="Test", author="Tester", pub_year=1980)
        book.title = "Updated title"
        book.save()
        generator.print_document()
        generator.create_new_document()
