# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: MIT

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import patch

import prov.model as prov
from django.test import TestCase

from django_prov.generator import ProvenanceGeneratorException
from tests.utils.configs import DEFAULT_PROVENANCE
from tests.utils.utils import get_clean_generator_init


class ClassActivitiesTest(TestCase):
    """
    Tests that the recording of classes as activities works as intended.
    """
    def setUp(self):
        config = deepcopy(DEFAULT_PROVENANCE)
        config["OUTPUT"]["GRAPHIC"] = []
        self.generator = get_clean_generator_init(config)
        self.documents = []
        self.export = patch.object(self.generator, "print_document",
                                   side_effect=lambda: self.documents.append(self.generator.document))
        self.export.start()
        self.addCleanup(self.export.stop)

    def records(self, cls, document=None):
        return list((document or self.documents[-1]).get_records(cls))

    def assert_graph(self, document):
        """
        Helper to test if the graphs work correctly.
        """
        nodes = {r.identifier: r for r in document.get_records() if isinstance(r, prov.ProvElement)}
        self.assertEqual(len(nodes), sum(isinstance(r, prov.ProvElement) for r in document.get_records()))
        for relation in document.get_records():
            if isinstance(relation, prov.ProvRelation):
                self.assertIn(relation.args[0], nodes)
                self.assertIn(relation.args[1], nodes)
                if isinstance(relation, prov.ProvGeneration):
                    self.assertIsInstance(nodes[relation.args[0]], prov.ProvEntity)
                    self.assertIsInstance(nodes[relation.args[1]], prov.ProvActivity)
                if isinstance(relation, prov.ProvUsage):
                    self.assertIsInstance(nodes[relation.args[0]], prov.ProvActivity)
                    self.assertIsInstance(nodes[relation.args[1]], prov.ProvEntity)
        self.assertEqual(document, prov.ProvDocument.deserialize(content=document.serialize(format="json"), format="json"))

    def test_equal_start_times_distinguish_running_and_completed_activities(self):
        """
        Tests if activities that get the same timestamp (due to clock resolution) are still distinguishable.
        """
        started = []
        timestamp = datetime(2026, 9, 16, 10, 30, 0, 123456)

        @self.generator.activity()
        def return_borrowings(remaining):
            started.append(self.generator.executing_activities[-1])
            if remaining:
                return_borrowings(remaining - 1)

        @self.generator.activity()
        def library_workflow():
            return_borrowings(2)
            return_borrowings(0)

        with patch("django_prov.generator.datetime") as clock:
            clock.datetime.now.return_value = timestamp
            library_workflow()

        base = "return_borrowings-2026-09-16_10-30-00-123456"
        self.assertEqual(started, [base, f"{base}-2", f"{base}-3", f"{base}-4"])
        activities = self.records(prov.ProvActivity)
        self.assertEqual(len(activities), 5)
        for activity in activities:
            self.assertEqual(activity.get_startTime(), timestamp)
            self.assertEqual(activity.get_endTime(), timestamp)
        self.assert_graph(self.documents[-1])

    def test_equal_snapshot_times_distinguish_instances_and_state_versions(self):
        """
        Tests that equal snapshot times of fields as entities get ordered correctly.
        """
        class Borrowing:
            status = "O"

            @self.generator.activity(fields=["status"])
            def start_borrowing(self):
                self.status = "B"

        @self.generator.activity()
        def start_ordered_borrowings():
            Borrowing().start_borrowing()
            Borrowing().start_borrowing()

        with patch("django_prov.generator.datetime") as clock:
            clock.datetime.now.return_value = datetime(2026, 9, 16, 10, 30)
            start_ordered_borrowings()
            start_ordered_borrowings()

        base = "Borrowing-2026-09-16_10-30-00-000000"
        for document in self.documents:
            entities = self.records(prov.ProvEntity, document)
            self.assertEqual([str(entity.identifier) for entity in entities],
                             [base, f"{base}-2", f"{base}-3", f"{base}-4"])
            self.assertEqual(len(self.records(prov.ProvGeneration, document)), 2)
            self.assertEqual(len(self.records(prov.ProvDerivation, document)), 2)
            self.assert_graph(document)

    def test_whole_class_preserves_type_and_tracks_construction_and_public_methods(self):
        """
        Tests that when a whole Python class is tracked, nothing in the class is changed.
        """
        class Borrowing:
            def __init__(self):
                self.status = "O"

            def start_borrowing(self):
                self.status = "B"
                return self.status

            def _status_label(self):
                return {"O": "Ordered", "B": "Borrowed", "R": "Returned"}[self.status]

            @property
            def is_borrowed(self):
                return self.status == "B"

        original = Borrowing
        Borrowing = self.generator.activity()(Borrowing)
        borrowing = Borrowing()
        self.assertIs(Borrowing, original)
        self.assertIsInstance(borrowing, original)
        self.assertEqual(borrowing.start_borrowing(), "B")
        self.assertTrue(borrowing.is_borrowed)
        self.assertEqual(borrowing._status_label(), "Borrowed")
        self.assertEqual(len(self.documents), 2)
        self.assertEqual(borrowing.start_borrowing.__name__, "start_borrowing")
        for document in self.documents:
            self.assertEqual(len(self.records(prov.ProvActivity, document)), 1)
            self.assert_graph(document)

    def test_selected_state_construction_mutation_and_read_only_call(self):
        """
        Tests that changing or reading recorded classes follow the expected pattern.
        """
        @self.generator.activity(fields=["status"])
        @dataclass
        class Borrowing:
            status: str = "O"

            def start_borrowing(self):
                self.status = "B"

            def get_status(self):
                return self.status

        borrowing = Borrowing()
        self.assertEqual(len(self.records(prov.ProvEntity)), 1)
        self.assertEqual(len(self.records(prov.ProvGeneration)), 1)
        borrowing.start_borrowing()
        self.assertEqual(len(self.records(prov.ProvEntity)), 2)
        self.assertEqual(len(self.records(prov.ProvDerivation)), 1)
        self.assertEqual(len(self.records(prov.ProvUsage)), 1)
        self.assertEqual(len(self.records(prov.ProvGeneration)), 1)
        self.assertEqual(borrowing.get_status(), "B")
        self.assertEqual(len(self.records(prov.ProvEntity)), 1)
        self.assertEqual(len(self.records(prov.ProvGeneration)), 0)
        for document in self.documents:
            self.assert_graph(document)

    def test_individual_method_and_nested_calls_share_document(self):
        """
        Tests that nested activities share the same document and get connected correctly.
        """
        class Borrowing:
            status = "O"

            @self.generator.activity(fields=["status"])
            def start_borrowing(this):
                this.status = "B"
                return this.status

            @self.generator.activity(fields=["status"])
            def return_borrowing(this):
                this.status = "R"
                return this.status

        borrowing = Borrowing()
        @self.generator.activity()
        def borrow_and_return():
            borrowing.start_borrowing()
            borrowing.return_borrowing()
        borrow_and_return()
        self.assertEqual(borrowing.status, "R")
        self.assertEqual(len(self.documents), 1)
        self.assertEqual(len(self.records(prov.ProvActivity)), 3)
        self.assertEqual(len(self.records(prov.ProvEntity)), 3)
        self.assertEqual(len(self.records(prov.ProvDerivation)), 2)
        self.assertEqual(len(self.records(prov.ProvCommunication)), 2)
        self.assert_graph(self.documents[0])

    def test_inherited_methods_descriptors_and_explicit_method_override(self):
        """
        Tests that overriding methods of a class that is tracked works as expected.
        """
        class LibraryService:
            def borrowing_statuses(self):
                return ("O", "B", "R")

        @self.generator.activity(name="BorrowingService")
        class BorrowingService(LibraryService):
            @staticmethod
            def is_available(book):
                return not book.is_borrowed

            @classmethod
            def for_library(cls):
                return cls()

            @self.generator.activity(name="return_borrowing")
            def return_borrowing(self, borrowing):
                borrowing.status = "R"
                return borrowing.status

        @dataclass
        class Book:
            is_borrowed: bool = False

        @dataclass
        class Borrowing:
            status: str = "B"

        service = BorrowingService()
        self.assertEqual(service.borrowing_statuses(), ("O", "B", "R"))
        self.assertTrue(service.is_available(Book()))
        self.assertIsInstance(BorrowingService.for_library(), BorrowingService)
        self.assertEqual(service.return_borrowing(Borrowing()), "R")
        self.assertEqual(len(self.records(prov.ProvActivity)), 1)
        self.assertTrue(str(self.records(prov.ProvActivity)[0].identifier).startswith("return_borrowing-"))
        count = len(self.documents)
        self.assertEqual(LibraryService().borrowing_statuses(), ("O", "B", "R"))
        self.assertEqual(len(self.documents), count)
        for document in self.documents:
            self.assert_graph(document)

    def test_zero_argument_keyword_only_and_main_module_functions(self):
        """
        Tests that a decorated functions behavior doesn't change.
        """
        def borrowing_period(*, days=2):
            return days
        borrowing_period.__module__ = "__main__"
        decorated = self.generator.activity()(borrowing_period)
        self.assertEqual(decorated(), 2)
        self.assertEqual(decorated(days=4), 4)
        self.assert_graph(self.documents[-1])

    def test_keyword_receiver_and_slots(self):
        """
        Tests that an activities 'fields' parameter works as expected.
        """
        class Book:
            __slots__ = ("is_borrowed",)

            def __init__(self):
                self.is_borrowed = False

            @self.generator.activity(fields=["is_borrowed"])
            def borrow(self):
                self.is_borrowed = True
        book = Book()
        Book.borrow(self=book)
        self.assertTrue(book.is_borrowed)
        self.assertEqual(len(self.records(prov.ProvEntity)), 2)
        self.assert_graph(self.documents[-1])

    def test_mutable_state_and_change_hidden_by_truncation(self):
        """
        Tests that the change of a tracked field results in the correct output even when the output is shortened.
        """
        self.generator.max_field_value_length = lambda value: value[:2]
        class Borrowing:
            def __init__(self):
                self.ordered_books = ["The Hobbit"]

            @self.generator.activity(fields=["ordered_books"])
            def order_book(self, title):
                self.ordered_books.append(title)
        borrowing = Borrowing()
        borrowing.order_book("The Lord of the Rings")
        self.assertEqual(borrowing.ordered_books, ["The Hobbit", "The Lord of the Rings"])
        self.assertEqual(len(self.records(prov.ProvEntity)), 2)
        self.assertEqual(len(self.records(prov.ProvDerivation)), 1)

    def test_separate_instances_and_document_reset(self):
        """
        Tests that different instances of the same class get connected correctly.
        """
        @self.generator.activity(fields=[])
        class LibraryService:
            pass
        @self.generator.activity()
        def create_library_services():
            return LibraryService(), LibraryService()
        left, right = create_library_services()
        self.assertIsNot(left, right)
        self.assertEqual(len(self.records(prov.ProvEntity)), 2)
        self.assertEqual(self.generator._python_records, {})
        self.assert_graph(self.documents[-1])

    def test_failed_method_exports_and_next_call_is_clean(self):
        """
        Tests that a failed call still creates the correct document.
        """
        class Book:
            is_borrowed = True

            @self.generator.activity(fields=["is_borrowed"])
            def borrow(self):
                if self.is_borrowed:
                    raise LookupError("Book is already borrowed")
        with self.assertRaisesRegex(LookupError, "Book is already borrowed"):
            Book().borrow()
        self.assertEqual(self.generator.executing_activities, [])
        self.assertEqual(self.generator._python_records, {})
        self.assert_graph(self.documents[-1])
        self.assertTrue(any(str(key).endswith("exception") and value == "LookupError"
                            for key, value in self.records(prov.ProvActivity)[0].attributes))
        @self.generator.activity()
        def available_books():
            return ["The Hobbit"]
        self.assertEqual(available_books(), ["The Hobbit"])
        self.assertEqual(len(self.records(prov.ProvActivity)), 1)

    def test_invalid_fields_and_missing_attribute(self):
        """
        Tests that an Exception is raised when a field that is not existing is specified.
        """
        for fields in ("status", [1], ["not-valid"]):
            with self.assertRaises(TypeError):
                self.generator.activity(fields=fields)
        with self.assertRaises(ValueError):
            self.generator.activity(fields=["status", "status"])
        class Borrowing:
            @self.generator.activity(fields=["bor_returned_date"])
            def return_borrowing(self):
                raise AssertionError("must not execute")
        with self.assertRaisesRegex(ProvenanceGeneratorException, "Missing recorded attribute"):
            Borrowing().return_borrowing()
        self.assertEqual(self.generator.executing_activities, [])

    def test_async_and_generator_methods_rejected_without_partial_decoration(self):
        """
        Tests that the usage of async functions raises an Exception.
        """
        async def fetch_available_books():
            return ["The Hobbit"]
        def iter_available_books():
            yield "The Hobbit"
        for function in (fetch_available_books, iter_available_books):
            with self.assertRaisesRegex(TypeError, "synchronous"):
                self.generator.activity()(function)
        class LibraryCatalogue:
            def available_books(self):
                return ["The Hobbit"]
            async def refresh_catalogue(self):
                return ["The Hobbit", "The Lord of the Rings"]
        original = LibraryCatalogue.available_books
        with self.assertRaises(TypeError):
            self.generator.activity()(LibraryCatalogue)
        self.assertIs(LibraryCatalogue.available_books, original)

    def test_export_failure_still_resets_document(self):
        """
        Tests that an Excpetion resets the current document appropriately.
        """
        self.generator.print_document.side_effect = OSError("output unavailable")

        @self.generator.activity()
        def available_books():
            return ["The Hobbit"]

        with self.assertRaises(OSError):
            available_books()
        self.assertEqual(self.generator.executing_activities, [])
        self.assertEqual(self.generator._python_records, {})

    def test_instance_representation_can_call_a_tracked_method(self):
        """
        Tests that a class's method is also tracked when the instance calls it.
        """
        @self.generator.activity()
        @dataclass
        class Book:
            title: str = "The Hobbit"

            def get_title(self):
                return self.title

            def __str__(self):
                return self.get_title()

            def catalogue_entry(self):
                return self

        book = Book()
        self.assertIs(book.catalogue_entry(), book)
        self.assertEqual(len(self.records(prov.ProvActivity)), 2)
        self.assert_graph(self.documents[-1])

    def test_nested_failure_does_not_contaminate_catching_parent(self):
        """
        Tests that an Exception does not wrongfully stop the uppermost activities from executing.
        """
        @self.generator.activity()
        def return_borrowing():
            raise ValueError("Borrowing is already returned")

        @self.generator.activity()
        def return_all_borrowings():
            with self.assertRaises(ValueError):
                return_borrowing()
            return "Returns processed"

        self.assertEqual(return_all_borrowings(), "Returns processed")
        self.assertEqual(len(self.documents), 1)
        self.assertEqual(len(self.records(prov.ProvActivity)), 2)
        self.assertEqual(len(self.records(prov.ProvCommunication)), 1)
        self.assert_graph(self.documents[-1])

    def test_original_exception_survives_export_failure(self):
        """
        Tests that an Exception in a tracked activity is preserved correctly.
        """
        self.generator.print_document.side_effect = OSError("output")
        @self.generator.activity()
        def find_book():
            raise LookupError("Book not found")
        with self.assertLogs("django_prov.generator", level="ERROR"), self.assertRaisesRegex(LookupError, "Book not found"):
            find_book()
        self.assertEqual(self.generator.executing_activities, [])
