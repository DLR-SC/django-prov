# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView
from .decorators import user_is_student, user_is_librarian
from example.models import *
from django_prov.generator import ProvenanceGenerator

generator = ProvenanceGenerator.get()


def print_document_on_click(request):
    generator.print_document()
    orig_page = request.META.get('HTTP_REFERER', '/')
    return redirect(orig_page)


def index(request):
    return render(request, 'index.html')


@method_decorator(generator.activity(name="foo22",), name='dispatch')
@method_decorator(user_is_student, name='dispatch')
class OrderCreateView(CreateView):
    model = Borrowing
    template_name = 'order_form.html'
    fields = [
        'ordered_books'
    ]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['ordered_books'].queryset = form.fields['ordered_books'].queryset.filter(is_borrowed=False)
        return form

    def form_valid(self, form):
        form.instance.student = Student.objects.get(person_id=self.request.user.id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('order.list')

@method_decorator(generator.activity(name="foo23",), name='dispatch')
@method_decorator(user_is_librarian, name='dispatch')
class BorrowStartView(UpdateView):
    model = Borrowing
    template_name = 'order_form.html'

    fields = [
        'ordered_books', 'borrowed_books',
    ]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        obooks = self.object.ordered_books.all()
        form.fields['ordered_books'].queryset = obooks
        form.fields['borrowed_books'].queryset = obooks.filter(is_borrowed=False)
        return form

    def form_valid(self, form):
        librarian = Librarian.objects.get(person_id=self.request.user.id)
        form.instance.responsible_librarian = librarian
        today = datetime.date.today()
        form.instance.bor_start_date = today
        form.instance.bor_auto_end_date = today + datetime.timedelta(days=2)
        form.instance.status = "B"
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('borrowing.list')


class BorrowingListView(ListView):
    model = Borrowing
    template_name = 'borrowing_list.html'

    def get_queryset(self):
        return Borrowing.objects.filter(status="B")


class OrderListView(ListView):
    model = Borrowing
    template_name = 'order_list.html'

    def get_queryset(self):
        return Borrowing.objects.filter(status="O")


class ReturningListView(ListView):
    model = Borrowing
    template_name = 'returning_list.html'

    def get_queryset(self):
        return Borrowing.objects.filter(status="R")


class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'
    def get_queryset(self):
        return Book.objects.all()

@generator.activity(name="foo2") #, additional_tracking={"header_info": response.header}, additional_tracking={"header_info": response.header}
def return_borrowing(borrowing):
    borrowing.status = "R"
    borrowing.bor_returned_date = datetime.date.today()
    for book in borrowing.borrowed_books.all():
        book.is_borrowed = False
        book.save()

    borrowing.save()

@generator.activity(name="all")
@user_is_librarian
def return_all_borrowings(request):
    for borrowing in Borrowing.objects.filter(status="B"):
        return_borrowing(borrowing)
    return HttpResponseRedirect(reverse('returning.list'))


@user_is_librarian
def return_all_borrowings_auto(request):
    for borrowing in Borrowing.objects.filter(status="B"):
        if borrowing.bor_auto_end_date <= datetime.date.today():
            return_borrowing(borrowing)
    return HttpResponseRedirect(reverse('returning.list'))


@generator.activity(name="foo",)
def return_a_borrowing(request, pk=None):
    borrowing = get_object_or_404(Borrowing, id=pk)
    try:
        person = Librarian.objects.get(person=request.user)
        return_borrowing(borrowing)
        return HttpResponseRedirect(reverse('returning.list'))
    except ObjectDoesNotExist as e:
        person = Student.objects.get(person=request.user)
        if person.id == borrowing.student_id:
            return_borrowing(borrowing)
            return HttpResponseRedirect(reverse('returning.list'))
        return HttpResponseForbidden("Access denied")
