import os
import warnings

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field
from prov.identifier import Namespace

from django_prov.utils import get_system_info_attributes


class ProvenanceGeneratorConfigurationException(Exception):
    """
    Provenance generator configuration exception
    """

class ProvenanceGeneratorConfigurationWarning(Warning):
    """
    Provenance generator configuration warning
    """


class ProvenanceGeneratorConfiguration:
    """
    Configuration class for ProvenanceGenerator
    """
    def __init__(self, configuration: dict = None):
        self._configuration = configuration

        self.default_namespace = None
        self.namespaces = []
        self.entities = {}
        self.agents = {}
        self.output = {}
        self.extras = {}

        if configuration:
            if isinstance(configuration, dict):
                self.validate_settings()
            else:
                raise ProvenanceGeneratorConfigurationException(f"The provided Configuration has to be of type <class 'dict'>. Provided: {type(configuration)}.")

    def _validate_namespaces(self):
        """
        Validates and updates the default namespace and the extra namespaces.
        """

        try:
            default_ns = self._configuration["NAMESPACES"]["DEFAULT"]
            extra_ns = self._configuration["NAMESPACES"]["EXTRA"]
        except KeyError as e:
            raise ProvenanceGeneratorConfigurationException(f"Section {e} does not exist in the settings.") from e
        except TypeError as e:
            raise ProvenanceGeneratorConfigurationException("The type of 'NAMESPACES' has to be a dictionary.") from e
        try:
            if isinstance(default_ns, str):
                self.default_namespace = Namespace("", default_ns)
            else:
                raise ProvenanceGeneratorConfigurationException("The default namespace has to be of type <class 'str'>.")
            if isinstance(extra_ns, list):
                for prefix in extra_ns:
                    if prefix == "sys":
                        self.extras["GET_SYSTEM_INFO"] = get_system_info_attributes
                    namespace = Namespace(prefix, f"{self.default_namespace.uri}{prefix}/")
                    if namespace not in self.namespaces:
                        self.namespaces.append(namespace)
                    else:
                        raise ProvenanceGeneratorConfigurationException(
                            f"Namespace '{prefix}' has been configured multiple times in section 'NAMESPACES' in the settings."
                            f"Please remove the other occurrences.")
            else: raise ProvenanceGeneratorConfigurationException("The extra namespaces have to be of type <class 'list'>.")
        except ValueError as e:
            raise ProvenanceGeneratorConfigurationException("A namespace can not be a blank string.") from e

    @staticmethod
    def _validate_fields(model, specified_fields: bool | list) -> list[Field]:
        """
        Validates the fields of a model and returns the fields as a list.
        """
        if isinstance(specified_fields, bool):
            return model._meta.fields
        elif isinstance(specified_fields, list):
            ret = []
            seen = set()
            for field in specified_fields:
                try:
                    if field in seen:
                        raise ProvenanceGeneratorConfigurationException(f"Field '{field}' of model '{model._meta.label}' has been defined multiple times in the settings.")
                    ret.append(model._meta.get_field(field))
                    seen.add(field)
                except FieldDoesNotExist as e:
                    warnings.warn(
                        f"The field '{field}' in the model '{model._meta.label}' seems to be nonexistent. "
                        f"Please remove it from the settings.", ProvenanceGeneratorConfigurationWarning)
            if len(ret) == 0:
                warnings.warn(
                    f"The settings for model '{model._meta.label}' do not specify at least one valid field to track. "
                    f"Provenance records for objects of the model will only contain the provenance identifier and the type.",
                    ProvenanceGeneratorConfigurationWarning)
            return ret
        else:
            raise ProvenanceGeneratorConfigurationException(f"Model '{model._meta.label}' is not correctly declared in the settings. "
                                               f"The value of '{model._meta.label}' has to be of type <class 'bool'> or <class 'list'>.\n"
                                               f"Provided type: {type(specified_fields)}")

    def _validate_models(self, key):
        """
        Validates the specified models and updates the entities and agents property.
        """
        model_dict = getattr(self, key.lower())

        try:
            for model_name, fields in self._configuration[key].items():
                try:
                    django_model = apps.get_model(model_name)
                    if model_name in self.entities and model_dict == self.agents:
                        raise ProvenanceGeneratorConfigurationException(
                            f"Model '{model_name}' is specified twice in 'ENTITIES' and 'AGENTS'. "
                            f"Remove at least one occurrence from the settings.")
                    filtered_fields = self._validate_fields(django_model, fields)
                    model_dict[model_name] = filtered_fields
                except LookupError as e:
                    raise ProvenanceGeneratorConfigurationException(
                        f"Specified Model '{model_name}' is not existing. Please remove it from the settings.") from e
        except AttributeError as e:
            raise ProvenanceGeneratorConfigurationException(
                f"The section '{key}' in the settings is not a dictionary.") from e
        except KeyError as e:
            if e.args[0] == "ENTITIES":
                raise ProvenanceGeneratorConfigurationException(f"Could not find the section {e} in the settings.") from e

    @staticmethod
    def _validate_formats(formats, key, valid_formats):
        """
        Validates the specified output formats.
        """

        ret = []

        if isinstance(formats, list):
            for serialization_format in formats:
                if serialization_format in valid_formats:
                    ret.append(serialization_format)
                else:
                    raise ProvenanceGeneratorConfigurationException(f"'{serialization_format}' is not a valid output format.")
        elif isinstance(formats, str):
            if formats in valid_formats:
                ret.append(formats)
            else:
                raise ProvenanceGeneratorConfigurationException(
                    f"'{formats}' is not a valid output format.")

        else:
            raise ProvenanceGeneratorConfigurationException(f"Section '{key}' is not correctly declared in the settings. "
                                               f"The value of '{key}' has to be of type <class 'list'> or <class 'str'>.\n"
                                               f"Provided type: {type(formats)}")
        return ret

    def _validate_output(self):
        """
        Validates the output path and formats.
        """
        try:
            output = self._configuration["OUTPUT"]
            serialize = output["SERIALIZE"]
            graphic = output.get("GRAPHIC")
        except KeyError as e:
            raise ProvenanceGeneratorConfigurationException(f"Section {e} does not exist in the settings.") from e
        except TypeError as e:
            raise ProvenanceGeneratorConfigurationException(f"The type of 'OUTPUT' has to be a dictionary.") from e

        path = output.get("PATH")
        if path is not None:
            try:
                os.makedirs(path, exist_ok=True)
                self.output["PATH"] = path
            except Exception as e:
                raise ProvenanceGeneratorConfigurationException(f"Output path '{path}' could not be accessed. "
                                                   f"Make sure that you have sufficient permissions.") from e
        else:
            warnings.warn(
                "You did not specify an output path. All provenance documents will be written to the commandline."
                "It is not possible to produce graphical output without an output path.",
                ProvenanceGeneratorConfigurationWarning)

        self.output["SERIALIZE"] = self._validate_formats(serialize, "SERIALIZE", ["provn", "txt", "rdf", "json", "xml"])
        if graphic:
            self.output["GRAPHIC"] = self._validate_formats(graphic, "GRAPHIC", ["png", "svg", "pdf"])
        else:
            self.output["GRAPHIC"] = []

    def _validate_extras(self):
        """
        Validates specified extras.
        """
        extras = self._configuration.get("OTHER")
        if extras:
            max_arg_length = extras.get("MAX_ARG_LENGTH")
            if isinstance(max_arg_length, (int, type(None))):
                self.extras["MAX_ARG_LENGTH"] = max_arg_length
            else:
                raise ProvenanceGeneratorConfigurationException(
                    f"Section 'MAX_ARG_LENGTH' is not correctly declared in the settings. "
                    f"The value of 'MAX_ARG_LENGTH' has to be of type <class 'int'>.\n"
                    f"Provided type: {type(max_arg_length)}")

            max_field_value_length = extras.get("MAX_FIELD_VALUE_LENGTH")
            if isinstance(max_field_value_length, (int, type(None))):
                self.extras["MAX_FIELD_VALUE_LENGTH"] = max_field_value_length
            else:
                raise ProvenanceGeneratorConfigurationException(
                    f"Section 'MAX_FIELD_VALUE_LENGTH' is not correctly declared in the settings. "
                    f"The value of 'MAX_FIELD_VALUE_LENGTH' has to be of type <class 'int'>.\n"
                    f"Provided type: {type(max_field_value_length)}")

            sys_info_func = extras.get("GET_SYSTEM_INFO")
            if callable(sys_info_func):
                if any(ns.prefix == "sys" for ns in self.namespaces):
                    self.extras["GET_SYSTEM_INFO"] = sys_info_func
                else:
                    raise ProvenanceGeneratorConfigurationException(
                        f"A function to track system information for executing activities was provided, "
                        f"but 'sys' is not part of your Namespaces. Please add 'sys' to your namespaces.")
            elif isinstance(sys_info_func, type(None)):
                pass
            else:
                raise ProvenanceGeneratorConfigurationException(
                    f"Section 'GET_SYSTEM_INFO' is not correctly declared in the settings. "
                    f"'GET_SYSTEM_INFO' has to be a callable. \n"
                    f"Provided type: {type(sys_info_func)}")


    def validate_settings(self):
        """
        Validates and updates the ProvenanceGeneratorConfiguration
        """

        self.default_namespace = None
        self.namespaces = []
        self._validate_namespaces()

        self.entities = {}
        self._validate_models("ENTITIES")

        self.agents = {}
        self._validate_models("AGENTS")

        self.output = {}
        self._validate_output()

        self.extras = {}
        self._validate_extras()
