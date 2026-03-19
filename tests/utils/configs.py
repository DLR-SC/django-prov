# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
#
# SPDX-License-Identifier: MIT

"""
This file holds different configurations of the ProvenanceGenerator for integration tests.
"""

from django.conf import settings

DEFAULT_PROVENANCE = {
    "ENTITIES": {},
    "AGENTS": {},
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": [ "auth", "django", "sys", "example", "django_prov"]
    },
    "OUTPUT": {
        "PATH": f"provenance_files/",
        "SERIALIZE": ["provn"],
        "GRAPHIC": [],
    },
    "OTHER": {"MAX_ARG_LENGTH": 100}
}

FULL_PROVENANCE = {
"ENTITIES": {
        'example.Borrowing': True,
        'example.Book': True,
        "example.Student": True,
        "example.Librarian": True,
    },
    "AGENTS": {},
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": ["auth", "django", "sys", "example", "django_prov"]
    },
    "OUTPUT": {
        # captures files in a directory on django-project level
        "PATH": None,
        "SERIALIZE": ["provn",],},
}

PROVENANCE_NO_BORROWING = {
"ENTITIES": {
        'example.Book': True,
        "example.Student": True,
        "example.Librarian": True,
    },
    "AGENTS": {},
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": ["auth","django","sys","example","django_prov"]
    },
    "OUTPUT": {
        # captures files in a directory on django-project level
        "PATH": None,
        "SERIALIZE": ["provn",],
    },
}

PROVENANCE_NO_BOOK = {
"ENTITIES": {
        'example.Borrowing': True,
        "example.Student": True,
        "example.Librarian": True,
    },
    "AGENTS": {},
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": ["auth", "django", "sys", "example", "django_prov"]
    },
    "OUTPUT": {
        # captures files in a directory on django-project level
        "PATH": None,
        "SERIALIZE": ["provn",],},
}

PROVENANCE_NO_STUDENT_NO_LIBRARIAN = {
"ENTITIES": {
        'example.Borrowing': True,
        'example.Book': True,
    },
    "AGENTS": {},
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": ["auth", "django", "sys", "example", "django_prov"]
    },
    "OUTPUT": {
        # captures files in a directory on django-project level
        "PATH": None,
        "SERIALIZE": ["provn",],},
}

PROVENANCE_STUDENT_AND_LIBRARIAN_AGENT = {
"ENTITIES": {
        'example.Borrowing': True,
        'example.Book': True,
    },
    "AGENTS": {
        "example.Student": True,
        "example.Librarian": True,
    },
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": ["auth", "django", "sys", "example", "django_prov"]
    },
    "OUTPUT": {
        # captures files in a directory on django-project level
        "PATH": None,
        "SERIALIZE": ["provn",]}
}

PROVENANCE_NO_AUTH_NO_BORROWING = {
"ENTITIES": {
        'example.Book': True,
        "example.Student": True,
        "example.Librarian": True,
    },
    "AGENTS": {},
    "NAMESPACES": {
        "DEFAULT": f"{settings.ROOT_URLCONF.split('.')[0]}.org/",
        "EXTRA": ["django", "sys", "example", "django_prov" ]
    },
    "OUTPUT": {
        # captures files in a directory on django-project level
        "PATH": None,
        "SERIALIZE": ["provn",],},
}
