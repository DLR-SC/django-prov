import sys
import warnings
import datetime

from functools import wraps
from logging import exception
from pathlib import Path

import prov.model as prov
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ForeignKey
from django.db.models.signals import *

from django_prov.configuration import ProvenanceGeneratorConfiguration


class ProvenanceGeneratorException(Exception):
    """provenance generator exception"""

class ProvenanceGeneratorWarning(Warning):
    """provenance generator warning"""

class ProvenanceGenerator:
    """
    Handler Class for Generating Provenance Documents
    """
    _instance = None

    def __init__(self, config: dict | ProvenanceGeneratorConfiguration = None):
        """
        Initializes the single ProvenanceGenerator instance.
        """

        self.config = None
        self.executing_activities = list()
        self.document = prov.ProvDocument()
        self.arg_length_check = lambda s: s
        self.max_field_value_length = lambda s: s

        self.clean_state(config)

    @classmethod
    def reset_settings(cls, config=None):
        instance = cls.get(config)
        cls.reset_receivers()
        instance.clean_state(config)
        return instance

    @classmethod
    def reset_cls(cls):
        cls._instance = None
        cls.reset_receivers()

    def clean_state(self, config: dict | ProvenanceGeneratorConfiguration = None):
        print("Initialized Generator")
        if config:
            self.config = config if isinstance(config, ProvenanceGeneratorConfiguration) \
                else ProvenanceGeneratorConfiguration(config)
        else:
            self.config = ProvenanceGeneratorConfiguration(settings.PROVENANCE)

        self.executing_activities = list()
        self.document = prov.ProvDocument()
        self.arg_length_check = lambda s: s
        self.max_field_value_length = lambda s: s

        self.set_max_lengths()

        self.connect_signals()
        self.create_new_document()

    @classmethod
    def reset_receivers(cls):
        pre_save.receivers.clear()
        post_save.receivers.clear()
        m2m_changed.receivers.clear()

    @classmethod
    def get(cls, config: dict | ProvenanceGeneratorConfiguration = None):
        """
        Returns the single instance of the class ProvenanceGenerator. Applies the Singleton-Pattern.
        :return:
        """
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    def handle_post_save(self, sender, instance, **kwargs):
        """
        Receiver-function for the post_save-Signal.
        :param sender: ModelBase class of the instance that got changed
        :param instance: Instance that got changed
        :param kwargs: other with the signal passed kwargs
        """
        identifier = self.create_prov_record(sender, instance)
        if len(self.executing_activities) > 0 and identifier:
            self.create_relation(identifier, self.executing_activities[-1], prov.ProvGeneration)

    def handle_pre_save(self, sender, instance, **kwargs):
        """
        Receiver-function for the pre_save-Signal.
        :param sender: ModelBase class of the instance that is going to be changed
        :param instance: Instance that is going to be changed
        :param kwargs: other with the signal passed kwargs
        """
        try:
            orig_object = sender.objects.get(pk=instance.id)
            self.create_prov_record(sender, orig_object)
        except ObjectDoesNotExist as e:
            # No previous state to derive a new entity from
            # No problem for the rest of the program
            pass

    def handle_m2m_changed(self, sender, instance, **kwargs):
        """
        Receiver-function for the m2m_changed-Signal. If an m2m_changed is triggered, either a new ProvRecord is created or connected to an existing ProvRecord.
        :param sender: ModelBase class of the instance
        :param instance: Instance of the given class
        :param kwargs: other with the signal passed kwargs
        """
        if kwargs["action"] == "post_add" or kwargs["action"] == "post_remove":
            m2m_entity = None
            try:
                m2m_entity = list(self.filter_prov_objects(instance._meta.app_label, sender._meta.object_name, instance.id))[-1]
            except Exception as e:
                print(e, file=sys.stderr)
                try:
                    parent_entity_of_m2m_entity_identifier = list(self.filter_prov_objects(instance._meta.app_label, instance._meta.object_name, instance.id))[-1]

                except Exception as e:
                    print(e, file=sys.stderr)
                    parent_entity_of_m2m_entity_identifier = self.create_prov_record(instance._meta.model, instance)
                if parent_entity_of_m2m_entity_identifier:
                    parent_entity_of_m2m_entity = self.document.get_record(parent_entity_of_m2m_entity_identifier)[0]

                    for field in instance._meta.many_to_many:
                        if instance._meta.object_name + "_" + field.attname == sender._meta.object_name:
                            m2m_entity = self.create_many_to_many_record(parent_entity_of_m2m_entity, instance, field)

            # Create Entities for entries in m2m_fields
            if kwargs["model"]._meta.label in self.config.entities:
                for pk in kwargs["pk_set"]:
                    try:
                        entity_in_m2m = list(self.filter_prov_objects(kwargs["model"]._meta.app_label, kwargs["model"]._meta.object_name, pk))[-1].identifier._str
                    except IndexError as e:
                        entity_in_m2m = self.create_prov_record(kwargs["model"], kwargs["model"].objects.get(pk=pk))
                    if entity_in_m2m and m2m_entity:
                        self.create_relation(m2m_entity, entity_in_m2m, prov.ProvMembership)

    def connect_signals(self):
        """
        Connects the Django Signals pre_save, post_save and m2m_changed with every model that is given in the settings.
        """
        from django.apps import apps
        for model in [*self.config.entities, *self.config.agents]:
            try:
                model = apps.get_model(model)
            except LookupError as e:
                raise ProvenanceGeneratorException(f"Model {model} not existing. Please remove it from the settings.") from e

            pre_save.connect(self.handle_pre_save, model, dispatch_uid=f"pre_save_{model}")
            print("Connected pre", model)
            post_save.connect(self.handle_post_save, model, dispatch_uid=f"post_save_{model}")
            print("Connected post", model)
            if model._meta.many_to_many:
                for m2m in model._meta.many_to_many:
                    sender = m2m.remote_field.through
                    m2m_changed.connect(self.handle_m2m_changed, sender, dispatch_uid=f"m2m_changed_{model}")
                    print("Connected m2m", model)

    def create_new_document(self):
        """
        Creates a new ProvDocument and needed ProvenanceGenerator instance-variables. Sets the default Namespace for the
        ProvDocument and adds extra namespaces.
        """
        self.executing_activities = list()
        self.document = prov.ProvDocument()
        self.document.set_default_namespace(self.config.default_namespace.uri)

        for namespace in self.config.namespaces:
            self.document.add_namespace(namespace)

    def set_max_lengths(self):
        """
        Sets the maximum lengths to record of function call arguments and django object fields.
        """

        arg_length_check = self.config.extras.get("MAX_ARG_LENGTH")
        if arg_length_check:
            self.arg_length_check = lambda s: f"{s[:arg_length_check]}..." if len(s) > arg_length_check else s

        max_field_value_length = self.config.extras.get("MAX_FIELD_VALUE_LENGTH")
        if max_field_value_length:
            self.max_field_value_length = lambda s: f"{s[:max_field_value_length]}..." if len(s) > max_field_value_length else s


    def create_m2m_entries(self, sender, instance, attributes):
        """
        Appends attributes of a ProvRecord for every ManyToManyField that is existing in the referenced instance.
        Deprecated.
        :param sender: ModelBase class of the instance
        :param instance: Instance of the given class
        :param attributes: Already existing List of Attributes for a new ProvRecord
        :return: List of new Attributes
        """
        for m2m_field in sender._meta.many_to_many:
            related_attr = getattr(instance, m2m_field.attname)
            new_attribute = (f'{sender._meta.app_label}:{m2m_field.attname}', str(related_attr.all()))
            attributes.append(new_attribute)
        return attributes

    def create_prov_record(self, class_info, obj):
        """
        Creates a ProvRecord (Entity or Agent) by a given class and object.
        :param class_info: ModelBase class of the instance
        :param obj: Instance of the given class
        :return: Identifier of a new or an existing ProvRecord
        """
        attributes = [(prov.PROV_TYPE, f"{obj._meta.app_label}:{class_info}")]

        # get included fields
        fields, prov_type = self.get_fields_to_record(obj)

        if prov_type is None:
            warning = (f"You didn't specify a ProvType for the class: {obj._meta.label}."
                       f" Records of the class are not stored in the provenance documents.")
            warnings.warn(warning, ProvenanceGeneratorWarning)
            return None

        for f in fields:
            new_attribute = (f'{obj._meta.app_label}:{f.attname}', self.max_field_value_length(str(getattr(obj, f.attname))))
            attributes.append(new_attribute)
        identifier = f"{obj._meta.app_label}:{obj._meta.object_name}-{obj.id}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}"

        try:
            last_similar_record = self.filter_prov_objects(obj._meta.app_label, obj._meta.object_name, obj.id, prov_type)[-1]
            if self.check_is_already_existing(last_similar_record, attributes):
                return last_similar_record.identifier._str
        except IndexError as e:
            pass

        if prov_type == prov.ProvEntity:
            self.document.entity(identifier, attributes)
            self.check_derivation(obj._meta.app_label, obj._meta.object_name, obj.id)
            # Foreign Key check may result in an endless loop if there is a circle of foreign keys (further work)
            self.check_foreign_keys(identifier, class_info, obj)

        elif prov_type == prov.ProvAgent or (
                any(ns.prefix == "auth" for ns in self.config.namespaces) and obj._meta.app_label == "auth"):
            self.document.agent(identifier, attributes)
            self.check_foreign_keys(identifier, class_info, obj, prov_type)
        else:
            warning = (f"You didn't specify a ProvType for the class: {obj._meta.label}."
                       f" Records of the class are not stored in the provenance documents.")
            warnings.warn(warning)
            return None

        return identifier

    def get_fields_to_record(self, obj):
        """
        Returns the fields and the type of ProvRecord of an object that will be tracked.
        Returns ([], None) if the object should not be tracked.
        """
        if obj._meta.label in self.config.entities:
            return self.config.entities[obj._meta.label], prov.ProvEntity
        elif obj._meta.label in self.config.agents:
            return self.config.agents[obj._meta.label], prov.ProvAgent
        elif any(ns.prefix == "auth" for ns in self.config.namespaces) and obj._meta.app_label == "auth":
            return obj._meta.fields, prov.ProvAgent
        return [], None

    def filter_prov_objects(self, label, model_name, identifier, prov_class=prov.ProvEntity):
        """
        Returns all objects that are similar to a given ProvRecord, by a given id and name. 'Similar' means that they
        describe the same instance in different timestamps.
        :param label: Valid namespace prefix that has been declared in settings
        :param model_name: ModelBase class of the instance whose ProvRecords have to be filtered
        :param identifier: Primary key of the instance for which all existing ProvRecords have to be checked
        :param prov_class: ProvType that has to be filtered
        :return: List of related ProvRecords
        """
        objs = list(self.document.get_records(prov_class))
        check_str = f"{label}:{model_name}-{identifier}-"
        new_objs = []
        for obj in objs:
            if check_str in str(obj.identifier):
                new_objs.append(obj)
        return new_objs

    def check_derivation(self, label, model_name, pk):
        """
        Checks if there need to be derivations between entities.
        :param label: Valid namespace prefix that has been declared in settings
        :param model_name: ModelBase class of the instance whose ProvRecords have to be checked
        :param pk: Primary key of the instance for which all existing ProvRecords have to be checked
        """
        derivations = list(self.document.get_records(prov.ProvDerivation))
        records = self.filter_prov_objects(label, model_name, pk)
        if len(records) > 1:
            for i in range(len(records) - 1):
                matching_derivation = None
                for derivation in derivations:
                    if derivation.attributes[0][1] == records[i + 1].identifier and derivation.attributes[1][1] == \
                            records[i].identifier:
                        matching_derivation = derivation
                        break
                if not matching_derivation:
                    self.create_relation(records[i + 1].identifier._str, records[i].identifier._str,
                                         prov.ProvDerivation)

    def create_foreign_key_entry(self, existing, foreign_model, foreign_pk):
        """
        Creates a related ProvRecord for an existing entity. This ProvRecord is accessed through a foreign key in the original entity.
        :param existing: The existing ProvRecord which has the foreign key field, identifier as str
        :param foreign_model: ModelBase class of the foreign key instance
        :param foreign_pk: Primary key of the foreign key instance
        """
        foreign_key_obj = foreign_model.objects.get(pk=foreign_pk)
        identifier = self.create_prov_record(foreign_model, foreign_key_obj)
        if identifier:
            if (foreign_model._meta.label and foreign_key_obj._meta.label) in self.config.entities:
                self.create_relation(existing, identifier, prov.ProvMembership)
            elif foreign_model._meta.label in self.config.agents or (
                    any(ns.prefix == "auth" for ns in self.config.namespaces) and foreign_model._meta.app_label == "auth"):
                if existing.identifier._str.split("-")[0].replace(":", ".") in self.config.agents:
                    self.create_relation(existing.identifier._str, identifier, prov.ProvInfluence)
                else:
                    self.create_relation(existing.identifier._str, identifier, prov.ProvAttribution)

    def create_many_to_many_record(self, parent_entity, obj, m2m_field):
        """
        :param parent_entity: Parent ProvEntity of which the m2m field originates
        :param obj: (ModelBase) Corresponding Object to the Parent Entity
        :param m2m_field: ManyToManyField for which the new entity shall be generated
        :return: ProvEntity
        """
        attributes = [(prov.PROV_TYPE, f"{obj._meta.app_label}:{m2m_field}"),
                      (f'{obj._meta.app_label}:model', str(m2m_field.model)),
                      (f'{obj._meta.app_label}:model_id', str(obj.id)),
                      (f'{obj._meta.app_label}:related_model', str(m2m_field.related_model))]
        identifier = f"{obj._meta.app_label}:{obj._meta.object_name}_{m2m_field.attname}-{obj.id}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}"
        if obj._meta.label in self.config.entities:
            entity = self.document.entity(identifier, attributes)
            self.create_relation(parent_entity, identifier, prov.ProvMembership)
            return entity.identifier._str
        return None

    def check_foreign_keys(self, identifier, sender, instance, prov_class=prov.ProvEntity):
        """
        Checks if an instance has referenced foreign keys and creates ProvRecords for them
        :param sender: ModelBase class of the sending instance
        :param instance: Instance of the ModelBase class
        :param kwargs: Kwargs that got passed
        """
        records = self.filter_prov_objects(sender._meta.app_label, instance._meta.object_name, instance.id, prov_class)
        if records:
            identifier = records[-1]

        for field in instance._meta.fields:
            if isinstance(field, ForeignKey):
                pk = getattr(instance, field.attname)
                if pk:
                    self.create_foreign_key_entry(identifier, field.related_model, pk)

        for field in instance._meta.many_to_many:
            m2m_identifier = self.create_many_to_many_record(identifier, instance, field)
            objs = list(getattr(instance, field.attname).all())
            if objs:
                for obj in objs:
                    self.create_foreign_key_entry(m2m_identifier, field.related_model, obj.pk)

    def check_is_already_existing(self, record, attributes):
        """
        Checks if the exactly same prov record is already existing in the document.
        If True is returned, this would mean that it was tried to write the exakt record with a new id.
        :param record: ProvRecord of which the attributes have to be checked
        :param attributes: List of attributes which are compared
        :return: True if existing, False if not
        """
        for i, j in zip(record.attributes, attributes):
            if isinstance(j[0], str):
                prefix, localpart = j[0].split(":")
                if prefix == i[0].namespace.prefix and localpart == i[0].localpart and i[1] == j[1]:
                    pass
                else:
                    return False

        return True

    def create_relation(self, first, second, rel_type):
        """
        Creates relations of type 'rel_type' between two ProvRecords.
        """
        # document.get_record() doesn't work for relations
        similar_records = list(self.document.get_records(rel_type))

        for record in similar_records:
            if first == record.args[0]._str and second == record.args[1]._str:
                return None

        if rel_type == prov.ProvDerivation:
            self.document.wasDerivedFrom(first, second)
        elif rel_type == prov.ProvMembership:
            self.document.hadMember(first, second)
        elif rel_type == prov.ProvCommunication:
            self.document.communication(first, second)
        elif rel_type == prov.ProvAssociation:
            self.document.association(first, second)
        elif rel_type == prov.ProvAttribution:
            self.document.wasAttributedTo(first, second)
        elif rel_type == prov.ProvGeneration:
            self.document.wasGeneratedBy(first, second)
        elif rel_type == prov.ProvInfluence:
            self.document.wasInfluencedBy(first, second)

    def print_document(self):
        """
        Exports the most recent document into the formats that are declared in the config
        """
        filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        path = self.config.output.get("PATH")
        if path:
            path = Path(path).as_posix() + "/"

        for serialization in self.config.output["SERIALIZE"]:
            if serialization == "txt":
                content = self.document.get_provn()
            else:
                content = self.document.serialize(format=serialization)
            if path:
                with open(f"{path}{filename}.{serialization}", "w") as file:
                    file.write(content)
            else:
                print(content)

        for graphic in self.config.output.get("GRAPHIC"):
            if path:
                self.document.plot(f"{path}{filename}.{graphic}")
            else:
                warnings.warn("'Without a path, no graphic can be printed. Please adapt your configuration.",
                      ProvenanceGeneratorWarning)


    def activity(self, name=None):
        """
        Decorator-function that can be applied to Views and other functions.
        :param name: Name that has to be applied to the decorated function
        :return: _decorator
        """

        def _decorator(func):
            """
            Sets the name for the decorated function.
            :param func: Decorated function
            :return: wrapped_func
            """
            if name is None:
                _name = func.__name__
            else:
                _name = name

            @wraps(func)
            def wrapped_func(*args, **kwargs):
                """
                Captures the execution of different decorated Views and functions.
                Creates ProvActivities for each executed function and relates them.
                :param args: Args of the decorated function
                :param kwargs: Kwargs of the decorated function
                :return: Return value of the decorated function
                """
                start_time = datetime.datetime.now()
                if "django." in func.__module__:
                    label = func.__module__.split(".")[0]
                else:
                    label = func.__module__.split(".")[-2]
                # check if post or get request for excluding get? (further work)
                attributes = [(prov.PROV_TYPE, f"{label}:func {func}")]

                sys_info_func = self.config.extras.get("GET_SYSTEM_INFO")
                if sys_info_func:
                    try:
                        attributes.extend(sys_info_func())
                    except Exception as e:
                        warnings.warn(f"The given 'GET_SYSTEM_INFO' function {sys_info_func} has not been executed successfully. "
                                      f"The return value has to be a list of tuples.")


                # append args and kwargs the orig func got called with
                if len(args) > 0:
                    attributes.extend((f"{label}:args-{i}", self.arg_length_check(str(arg))) for i, arg in enumerate(args))
                if len(kwargs) > 0:
                    attributes.extend((f"{label}:kwargs-{i}-{kwarg}", self.arg_length_check(str(kwargs[kwarg]))) for i, kwarg in enumerate(kwargs))

                identifier = f"{label}:{_name}-{start_time.strftime('%Y-%m-%d_%H-%M-%S-%f')}"

                self.executing_activities.append(identifier)
                result = func(*args, **kwargs)
                self.executing_activities.remove(identifier)
                attributes.append((f"{label}:result", str(result)))
                end_time = datetime.datetime.now()

                self.document.activity(identifier, start_time, end_time, attributes)

                # check for related objects
                for possible_obj in args:
                    try:
                        related_objs = self.filter_prov_objects(possible_obj._meta.app_label,
                                                                possible_obj._meta.object_name, possible_obj.id)
                        self.create_relation(related_objs[-1].identifier._str, identifier, prov.ProvGeneration)
                    except Exception as e:
                        print(e, file=sys.stderr)
                        pass
                # check for other activities that are generated by the most recent activity
                if len(self.executing_activities) > 0:
                    self.create_relation(identifier, self.executing_activities[-1], prov.ProvCommunication)

                # If Django Request: get request user
                if isinstance(args[0], WSGIRequest) and any(ns.prefix == "auth" for ns in self.config.namespaces):
                    try:
                        user_agent_identifier = \
                        list(self.filter_prov_objects("auth", "User", args[0].user.id, prov.ProvAgent))[-1].identifier._str
                    except IndexError as e:
                        user_agent_identifier = self.create_prov_record(User, args[0].user)
                    if user_agent_identifier:
                        self.create_relation(identifier, user_agent_identifier, prov.ProvAssociation)

                # If list is empty it means every activity got handled -> print finished document and start new one
                if not self.executing_activities:
                    self.print_document()
                    self.create_new_document()
                return result

            return wrapped_func

        return _decorator
