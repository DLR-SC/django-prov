from django.apps import AppConfig
from django.conf import settings

from django.utils.translation import gettext_lazy as _


class ProvCaptureConfig(AppConfig):
    name = 'django_prov'
    verbose_name = _("Django Provenance Capture")
    generator_instance = None

    def ready(self):
        from . import generator

        self.generator_instance = generator.ProvenanceGenerator.get(settings.PROVENANCE["NAMESPACES"]["DEFAULT"])
