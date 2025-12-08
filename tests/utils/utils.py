"""
This file holds functionality to clean the ProvenanceGenerator before each test.
"""

import copy

from django_prov.generator import ProvenanceGenerator

def clean_test_settings(config):
    return copy.deepcopy(config)

def get_clean_generator_init(config = None):
    ProvenanceGenerator.reset_cls()
    generator = ProvenanceGenerator.get(config)
    return generator

def get_clean_generator_no_init(config = None):
    ProvenanceGenerator.reset_cls()
    generator = ProvenanceGenerator.__new__(ProvenanceGenerator)
    generator.config = config
    return generator
