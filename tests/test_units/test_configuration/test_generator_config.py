import re

import pytest
from django.apps import apps
from django.db.models import Field
from django.test import TestCase
from prov.identifier import Namespace

from django_prov.configuration import ProvenanceGeneratorConfiguration, ProvenanceGeneratorConfigurationException, \
    ProvenanceGeneratorConfigurationWarning

from tests.utils.configs import DEFAULT_PROVENANCE

class TestProvenanceGeneratorConfiguration:
    """
    Tests the validation functionality of the ProvenanceGeneratorConfiguration.
    """
    @staticmethod
    def test_init_default_config_success():
        """
        Tests that for a simple dictionary configuration the ProvenanceGeneratorConfiguration is instantiated correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration(DEFAULT_PROVENANCE)

        assert prov_configuration._configuration == DEFAULT_PROVENANCE
        assert prov_configuration.default_namespace.uri == DEFAULT_PROVENANCE["NAMESPACES"]["DEFAULT"]
        assert len(prov_configuration.namespaces) == 5
        assert prov_configuration.entities == {}
        assert prov_configuration.agents == {}
        assert prov_configuration.extras["MAX_ARG_LENGTH"] == 100
        assert prov_configuration.output == DEFAULT_PROVENANCE["OUTPUT"]

    @staticmethod
    def test_init_no_config():
        """
        Tests that for no configuration the ProvenanceGeneratorConfiguration is instantiated correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        assert prov_configuration._configuration is None
        assert prov_configuration.default_namespace is None
        assert len(prov_configuration.namespaces) == 0
        assert prov_configuration.entities == {}
        assert prov_configuration.agents == {}
        assert prov_configuration.extras == {}
        assert prov_configuration.output == {}

    @staticmethod
    def test_init_config_type_error():
        """
        Tests that for a wrong configuration the ProvenanceGeneratorConfiguration raises an error.
        """
        config = "wrong"
        with pytest.raises(ProvenanceGeneratorConfigurationException, match=f"The provided Configuration has to be of type <class 'dict'>. Provided: {type(config)}."):
            prov_configuration = ProvenanceGeneratorConfiguration(config)

            assert prov_configuration._configuration is None
            assert prov_configuration.default_namespace is None
            assert len(prov_configuration.namespaces) == 0
            assert prov_configuration.entities == {}
            assert prov_configuration.agents == {}
            assert prov_configuration.extras == {}
            assert prov_configuration.output == {}

    @staticmethod
    def test_validate_namespaces_success():
        """
        Tests that ProvenanceGeneratorConfiguration correctly validates ProvNamespaces.
        """
        prov_configuration = ProvenanceGeneratorConfiguration({})
        prov_configuration._configuration["NAMESPACES"] = DEFAULT_PROVENANCE["NAMESPACES"]

        prov_configuration._validate_namespaces()

        assert isinstance(prov_configuration.default_namespace, Namespace)
        assert prov_configuration.default_namespace.uri == DEFAULT_PROVENANCE["NAMESPACES"]["DEFAULT"]
        assert isinstance(prov_configuration.namespaces, list)
        assert len(prov_configuration.namespaces) == 5

        for namespace in prov_configuration.namespaces:
            assert isinstance(namespace, Namespace)
            assert namespace.uri == f"{prov_configuration.default_namespace.uri}{namespace.prefix}/"

    @staticmethod
    def test_validate_namespaces_key_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises ProvenanceGeneratorConfigurationExceptions when the 'NAMESPACES' section is not existing correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="Section 'NAMESPACES' does not exist in the settings."):
            prov_configuration._configuration = {}
            prov_configuration._validate_namespaces()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="The type of 'NAMESPACES' has to be a dictionary."):
            prov_configuration._configuration = {"NAMESPACES": "foo"}
            prov_configuration._validate_namespaces()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="Section 'DEFAULT' does not exist in the settings."):
            prov_configuration._configuration = {"NAMESPACES": {"foo": "foo"}}
            prov_configuration._validate_namespaces()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="Section 'EXTRA' does not exist in the settings."):
            prov_configuration._configuration = {"NAMESPACES": {"DEFAULT": "foo"}}
            prov_configuration._validate_namespaces()

    @staticmethod
    def test_validate_namespaces_format_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises ProvenanceGeneratorConfigurationExceptions when a Namespace has the wrong format.
        :return:
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="A namespace can not be a blank string."):
            prov_configuration._configuration = {"NAMESPACES": {"DEFAULT": "", "EXTRA": ["correct"]}}
            prov_configuration._validate_namespaces()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="The default namespace has to be of type <class 'str'>."):
            prov_configuration._configuration = {"NAMESPACES": {"DEFAULT": 123, "EXTRA": ["correct"]}}
            prov_configuration._validate_namespaces()

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="The extra namespaces have to be of type <class 'list'>."):
            prov_configuration._configuration = {"NAMESPACES": {"DEFAULT": "correct", "EXTRA": "wrong"}}
            prov_configuration._validate_namespaces()

    @staticmethod
    def test_validate_namespaces_duplicate_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException when there are duplicate Namespaces.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"Namespace 'duplicate' has been configured multiple times in section 'NAMESPACES' in the settings."
                            f"Please remove the other occurrences."):
            prov_configuration._configuration = {"NAMESPACES": {"DEFAULT": "correct", "EXTRA": ["duplicate", "duplicate"]}}
            prov_configuration._validate_namespaces()

    @staticmethod
    def test_validate_fields_success():
        """
        Tests that the fields for an existing model are validated correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model = apps.get_model("example.Book")

        fields = prov_configuration._validate_fields(model, ["id", "isbn", "title"])

        assert len(fields) == 3
        for field in fields:
            assert isinstance(field, Field)

        fields = prov_configuration._validate_fields(model, True)

        assert len(fields) == len(model._meta.fields)
        for field in fields:
            assert isinstance(field, Field)

    @staticmethod
    def test_validate_fields_format_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when fields for an existing model are not declared correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model = apps.get_model("example.Book")

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="Model 'example.Book' is not correctly declared in the settings. "
                                 "The value of 'example.Book' has to be of type <class 'bool'> or <class 'list'>.\n"
                                 "Provided type: <class 'str'>"):
            prov_configuration._validate_fields(model, "wrong")

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="Model 'example.Book' is not correctly declared in the settings. "
                                 "The value of 'example.Book' has to be of type <class 'bool'> or <class 'list'>.\n"
                                 "Provided type: <class 'int'>"):
            prov_configuration._validate_fields(model, 123)

    @staticmethod
    def test_validate_fields_duplicate_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when fields for an existing model are defined multiple times.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model = apps.get_model("example.Book")

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="Field 'isbn' of model 'example.Book' has been defined multiple times in the settings."):
            fields = prov_configuration._validate_fields(model, ["isbn", "isbn"])

    @staticmethod
    def test_validate_fields_field_not_existing():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationWarning
        when specified fields for an existing model are not existing.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model = apps.get_model("example.Book")

        with pytest.warns(ProvenanceGeneratorConfigurationWarning,
                           match="The field 'notexistingfield' in the model 'example.Book' seems to be nonexistent. "
                        "Please remove it from the settings."):
            fields = prov_configuration._validate_fields(model, ["notexistingfield", "isbn"])
            assert len(fields) == 1

    @staticmethod
    def test_validate_fields_no_valid_fields():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationWarning
        when all specified fields for an existing model are not existing.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model = apps.get_model("example.Book")

        with pytest.warns(ProvenanceGeneratorConfigurationWarning,
                          match="The field 'notexistingfield' in the model 'example.Book' seems to be nonexistent. "
                                "Please remove it from the settings."):
            with pytest.warns(ProvenanceGeneratorConfigurationWarning,
                              match="The settings for model 'example.Book' do not specify at least one valid field to track. "
                        "Provenance records for objects of the model will only contain the provenance identifier and the type."):
                fields = prov_configuration._validate_fields(model, ["notexistingfield"])
                assert len(fields) == 0

    @staticmethod
    def test_validate_models_success():
        """
        Tests that specified models that exist are validated correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        key1 = "ENTITIES"
        key2 = "AGENTS"

        prov_configuration._configuration = {"ENTITIES": {"example.Book": True, "example.Borrowing": True}, "AGENTS": {"example.Student": True}}

        prov_configuration._validate_models(key1)
        prov_configuration._validate_models(key2)

        assert len(prov_configuration.entities) == 2
        assert len(prov_configuration.agents) == 1
        assert len(prov_configuration.agents["example.Student"]) == 3
        assert len(prov_configuration.entities["example.Book"]) == 6
        assert len(prov_configuration.entities["example.Borrowing"]) == 9

    @staticmethod
    def test_validate_models_format_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when the 'ENTITIES' or 'AGENTS' section is declared incorrectly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"The section 'ENTITIES' in the settings is not a dictionary."):
            prov_configuration._configuration = {"ENTITIES": "wrong"}
            prov_configuration._validate_models("ENTITIES")

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"The section 'AGENTS' in the settings is not a dictionary."):
            prov_configuration._configuration = {"AGENTS": "wrong"}
            prov_configuration._validate_models("AGENTS")

    @staticmethod
    def test_validate_models_key_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when the 'ENTITIES' section is not existing.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="Could not find the section 'ENTITIES' in the settings."):
            prov_configuration._configuration = {}
            prov_configuration._validate_models("ENTITIES")

        # No error when 'AGENTS' not existing:
        prov_configuration._configuration = {"ENTITIES": {"example.Book", True}}
        prov_configuration._validate_models("AGENTS")
        assert prov_configuration.agents == {}

    @staticmethod
    def test_validate_models_duplicate_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when a model is specified in 'ENTITIES' and 'AGENTS' section.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model_name = "example.Book"

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"Model '{model_name}' is specified twice in 'ENTITIES' and 'AGENTS'. "
                            f"Remove at least one occurrence from the settings."):
            prov_configuration._configuration = {"ENTITIES": {model_name: True}, "AGENTS": {model_name: True}}
            prov_configuration._validate_models("ENTITIES")
            prov_configuration._validate_models("AGENTS")

    @staticmethod
    def test_validate_models_lookup_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when a specified model is not existing.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        model_name = "example.WrongModel"

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"Specified Model '{model_name}' is not existing. Please remove it from the settings."):
            prov_configuration._configuration = {"ENTITIES": {model_name: True}}
            prov_configuration._validate_models("ENTITIES")


    @staticmethod
    def test_validate_formats_success():
        """
        Tests that all supported output formats are validated correctly.
        """
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]
        valid_graphic_formats = ["png", "svg", "pdf"]

        prov_configuration = ProvenanceGeneratorConfiguration()

        formats = prov_configuration._validate_formats("provn", "SERIALIZE", valid_serialize_formats)
        assert len(formats) == 1
        assert "provn" in formats

        formats = prov_configuration._validate_formats(["png", "svg"], "GRAPHIC", valid_graphic_formats)
        assert len(formats) == 2

    @staticmethod
    def test_validate_formats_type_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when output formats are not declared correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        input_formats = 123
        key = "SERIALIZE"
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]

        with pytest.raises(ProvenanceGeneratorConfigurationException, match=f"Section '{key}' is not correctly declared in the settings. "
                                               f"The value of '{key}' has to be of type <class 'list'> or <class 'str'>.\n"
                                               f"Provided type: {type(input_formats)}"):
            prov_configuration._validate_formats(input_formats, key, valid_serialize_formats)

    @staticmethod
    def test_validate_formats_format_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when not supported output formats are specified.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        output_format1 = "wrong_format"
        output_format2 = ["wrong_format"]
        key = "SERIALIZE"
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"'{output_format1}' is not a valid output format."):
            prov_configuration._validate_formats(output_format1, key, valid_serialize_formats)

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match=f"'{output_format2[0]}' is not a valid output format."):
            prov_configuration._validate_formats(output_format2, key, valid_serialize_formats)

    @staticmethod
    def test_validate_output_success(tmp_path):
        """
        Tests that the ProvenanceGeneratorConfiguration creates an output path if specified.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]
        valid_graphic_formats = ["png", "svg", "pdf"]
        test_dir = tmp_path / "test-path/"
        output_config = {"PATH": test_dir, "SERIALIZE": valid_serialize_formats, "GRAPHIC": valid_graphic_formats}

        prov_configuration._configuration = {"OUTPUT": output_config}
        assert not test_dir.exists()
        prov_configuration._validate_output()
        assert prov_configuration.output == output_config
        assert test_dir.exists()
        assert test_dir.is_dir()

    @staticmethod
    def test_validate_output_no_graphic_success(tmp_path):
        """
        Tests that the ProvenanceGeneratorConfiguration is validated correctly, even if no 'GRAPHIC' output is specified
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        valid_serialize_formats = ["provn", "txt", "rdf", "json", "xml"]
        valid_graphic_formats = ["png", "svg", "pdf"]
        test_dir = tmp_path / "test-path/"
        output_config = {"PATH": test_dir, "SERIALIZE": valid_serialize_formats}

        # test that GRAPHIC is not mandatory
        prov_configuration._configuration = {"OUTPUT": output_config}
        assert not test_dir.exists()
        prov_configuration._validate_output()
        assert prov_configuration.output == output_config | {"GRAPHIC": []}
        assert test_dir.exists()
        assert test_dir.is_dir()

    @staticmethod
    def test_validate_output_key_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when the 'OUTPUT' section is not existing.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        config_1 = {"WRONG_OUTPUT_KEY": True}
        config_2 = {"OUTPUT": {"WRONG_FORMAT_KEY": True}}

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="Section 'OUTPUT' does not exist in the settings."):
            prov_configuration._configuration = config_1
            prov_configuration._validate_output()

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="Section 'SERIALIZE' does not exist in the settings."):
            prov_configuration._configuration = config_2
            prov_configuration._validate_output()

    @staticmethod
    def test_validate_output_type_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when the 'OUTPUT' section is not declared correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        config = {"OUTPUT": ["test"]}

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                           match="The type of 'OUTPUT' has to be a dictionary."):
            prov_configuration._configuration = config
            prov_configuration._validate_output()

    @staticmethod
    def test_validate_output_no_path_warning():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationWarning
        when no output path is specified.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        config = {"OUTPUT": {"SERIALIZE": ["provn"]}}

        with pytest.warns(ProvenanceGeneratorConfigurationWarning,
                           match="You did not specify an output path. "
                                 "All provenance documents will be written to the commandline."
                                 "It is not possible to produce graphical output without an output path."):
            prov_configuration._configuration = config
            prov_configuration._validate_output()

    @staticmethod
    def test_validate_output_path_not_accessible(tmp_path):
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when the output path can not be accessed.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()
        data_file = tmp_path / "output"
        data_file.write_text("foo")
        target_dir = data_file / "provenance"
        config = {"OUTPUT": {"PATH": target_dir, "SERIALIZE": ["provn"]}}

        with pytest.raises(ProvenanceGeneratorConfigurationException,
                          match=f"Output path '{re.escape(str(target_dir))}' could not be accessed. "
                                f"Make sure that you have sufficient permissions."):
            prov_configuration._configuration = config
            prov_configuration._validate_output()

    @staticmethod
    def test_validate_extras_success():
        """
        Tests that the supported extra / other options are validated correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        config = {"OTHER": {"MAX_ARG_LENGTH": 100}}
        prov_configuration._configuration = config
        prov_configuration._validate_extras()

        assert prov_configuration.extras["MAX_ARG_LENGTH"] == 100

    @staticmethod
    def test_validate_extras_type_error():
        """
        Tests that the ProvenanceGeneratorConfiguration raises a ProvenanceGeneratorConfigurationException
        when entries of the 'OTHER' section are not declared correctly.
        """
        prov_configuration = ProvenanceGeneratorConfiguration()

        config = {"OTHER": {"MAX_ARG_LENGTH": "wrong_type"}}
        prov_configuration._configuration = config

        with pytest.raises(ProvenanceGeneratorConfigurationException, match="Section 'MAX_ARG_LENGTH' is not correctly declared in the settings. "
                    "The value of 'MAX_ARG_LENGTH' has to be of type <class 'int'>.\n"
                    "Provided type: <class 'str'>"):
            prov_configuration._validate_extras()
