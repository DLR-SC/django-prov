import re
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase

from django_prov.configuration import ProvenanceGeneratorConfiguration
from django_prov.generator import ProvenanceGenerator
from example.models import Student, Librarian, Book, Borrowing

from tests.utils.configs import FULL_PROVENANCE, PROVENANCE_NO_BOOK, PROVENANCE_NO_BORROWING, \
    PROVENANCE_NO_AUTH_NO_BORROWING, PROVENANCE_NO_STUDENT_NO_LIBRARIAN, PROVENANCE_STUDENT_AND_LIBRARIAN_AGENT
from tests.utils.regex_patterns import borrowing_return_pattern, borrowing_return_pattern_no_borrowing, \
    borrowing_return_pattern_no_auth_no_borrowing, borrowing_return_pattern_no_book, \
    borrowing_return_pattern_no_student_no_librarian, borrowing_return_pattern_student_and_librarian_agent


class BorrowingReturnTest(TestCase):
    """
    Tests that the Return Borrowing functionality of the example app results in the correct ProvDocument.
    """
    def setUp(self) -> None:
        self.default_student_user = User.objects.create_user(username="Student", password="s")
        self.default_student = Student.objects.create(matrikelnr=1234567, person=self.default_student_user)
        self.default_librarian_user = User.objects.create_user(username="Librarian", password="l")
        self.default_librarian = Librarian.objects.create(person=self.default_librarian_user)
        self.book1 = Book.objects.create(isbn="9781627052214", title="Provenance: An Introduction to PROV", author="Luc Moreau", pub_year=2013)
        self.book2 = Book.objects.create(isbn="978140885589", title="Harry Potter and the Philosopher's Stone", author="J.K. Rowling", pub_year=1997)
        self.borrowing = Borrowing.objects.create(student=self.default_student)
        self.borrowing.ordered_books.add(self.book1, self.book2)

    def tearDown(self):
        User.objects.all().delete()
        Book.objects.all().delete()
        Student.objects.all().delete()
        Borrowing.objects.all().delete()
        Librarian.objects.all().delete()

    @given(st.sampled_from([
        ("Full Provenance", FULL_PROVENANCE, borrowing_return_pattern),
        ("No Borrowing", PROVENANCE_NO_BORROWING, borrowing_return_pattern_no_borrowing),
        ("No Auth, no Borrowing", PROVENANCE_NO_AUTH_NO_BORROWING, borrowing_return_pattern_no_auth_no_borrowing),
        ("No Book", PROVENANCE_NO_BOOK, borrowing_return_pattern_no_book),
        ("No Student, No Librarian", PROVENANCE_NO_STUDENT_NO_LIBRARIAN,
         borrowing_return_pattern_no_student_no_librarian),
        ("Student and Librarian Agent", PROVENANCE_STUDENT_AND_LIBRARIAN_AGENT,
         borrowing_return_pattern_student_and_librarian_agent)
    ]))
    @settings(deadline=None)
    def test_borrowing_return(self, given_data):
        """
        Tests that for different versions of the ProvenanceGeneratorConfiguration the 'return borrowing' functionality generates correct records.
        """
        with patch("sys.stdout.write") as mock_stdout, \
                patch("sys.stderr", new=StringIO()) as mock_stderr:
            name, config, regex_pattern = given_data

            # Preparations
            borrowing = Borrowing.objects.get(id=1)
            borrowing.borrowed_books.add(self.book1, self.book2)
            borrowing.responsible_librarian = self.default_librarian
            borrowing.status = "B"
            borrowing.save()

            prov_configuration = ProvenanceGeneratorConfiguration(config)
            generator = ProvenanceGenerator.reset_settings(prov_configuration)

            mock_stdout.reset_mock()

            self.client.login(username='Librarian', password='l')
            before = Borrowing.objects.get(id=1)

            response = self.client.post(reverse('return-borrowing', args=[1]))
            self.assertEqual(response.status_code, 302)
            after = Borrowing.objects.get(id=1)

            assert before.bor_returned_date != after.bor_returned_date
            assert before.status == "B"
            assert after.status == "R"

            book1 = Book.objects.get(id=1)
            book2 = Book.objects.get(id=2)

            assert book1.is_borrowed == book2.is_borrowed == False

            output = mock_stdout.call_args_list[0].args[0].strip().splitlines(keepends=True)
            print(output)
            for out, pattern in zip(output, regex_pattern):
                assert re.fullmatch(pattern, out), f"{out!r} did not match {pattern!r}"
