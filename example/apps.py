# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class ExampleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'example'
