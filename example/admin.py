# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from .models import *

admin.site.register(Student)
admin.site.register(Librarian)
admin.site.register(Book)
admin.site.register(Borrowing)
