# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from .models import Student, Librarian


def user_is_student(view_func):
    def wrapped_view(request, *args, **kwargs):
        person = User()
        try:
            person = Student.objects.get(person=request.user)
        except Exception as e:
            pass

        if not isinstance(person, Student):
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return wrapped_view


def user_is_librarian(view_func):
    def wrapped_view(request, *args, **kwargs):
        person = User()
        try:
            person = Librarian.objects.get(person=request.user)
        except Exception as e:
            pass

        if not isinstance(person, Librarian):
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return wrapped_view
