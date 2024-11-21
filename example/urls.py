from django.urls import path, include
from django.contrib import admin

from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('borrowings/', BorrowingListView.as_view(), name='borrowing.list'),
    path('orders/', OrderListView.as_view(), name='order.list'),
    path('returnings/', ReturningListView.as_view(), name='returning.list'),
    path('return-borrowings-auto/', return_all_borrowings_auto, name='return-borrowings-auto'),
    path('return-borrowings/', return_all_borrowings, name='return-borrowings'),
    path('return-borrowing/<int:pk>', return_a_borrowing, name='return-borrowing'),
    path('books/', BookListView.as_view(), name='book.list'),
    path('order/create/', OrderCreateView.as_view(), name='order.create'),
    path('borrowing/start/<int:pk>', BorrowStartView.as_view(), name='borrow.start'),
    path('print-doc/', print_document_on_click, name='print-doc')
]
