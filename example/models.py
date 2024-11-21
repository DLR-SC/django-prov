import datetime

from django.conf import global_settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    matrikelnr = models.IntegerField(validators=[MaxValueValidator(9999999), MinValueValidator(1000000)], verbose_name="Matriculation Number")
    person = models.ForeignKey(global_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               verbose_name="Associated User")

    def __str__(self):
        return self.person.username


class Librarian(models.Model):
    person = models.ForeignKey(global_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               verbose_name="Associated User")

    def __str__(self):
        return self.person.username


class Book(models.Model):
    isbn = models.CharField(max_length=13, verbose_name="ISBN", null=False)
    title = models.CharField(max_length=60, verbose_name="Booktitle", null=False)
    author = models.CharField(max_length=40, verbose_name="Author", null=False)
    pub_year = models.IntegerField(verbose_name="Published", null=False)
    is_borrowed = models.BooleanField(default=False, verbose_name="Book currently borrowed")

    def __str__(self):
        return self.title


class Borrowing(models.Model):
    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE,
                                verbose_name="Student",
                                null=False)
    responsible_librarian = models.ForeignKey(Librarian, on_delete=models.DO_NOTHING,
                                              verbose_name="Responsible Librarian", null=True)
    ordered_books = models.ManyToManyField(Book, related_name="ordered_books", blank=False)
    borrowed_books = models.ManyToManyField(Book, related_name="borrowed_books", blank=True)
    date_of_order = models.DateField(null=False, default=datetime.date.today, editable=False)
    bor_start_date = models.DateField(null=True, blank=True, verbose_name="Start Date of Borrowing")
    bor_auto_end_date = models.DateField(null=True, blank=True, verbose_name="End Date of Borrowing")
    bor_returned_date = models.DateField(null=True, blank=True, verbose_name="Returned Date")
    CHOICES = [
        ("O", "Status: Is Order"),
        ("B", "Status: Borrow running"),
        ("R", "Status: Is Returned")
    ]

    status = models.CharField(
        max_length=1,
        choices=CHOICES,
        default="O"
    )
    note = models.CharField(max_length=400, verbose_name="Note for the order", blank=True)

    def __str__(self):
        return "Borrowing " + str(self.id)

    def get_selected_o_books(self):
        books = []
        for book in self.ordered_books.all():
            books.append(book)
        return books

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        if self.status == "B":
            for book in self.ordered_books.all():
                book.is_borrowed = True
                book.save()
