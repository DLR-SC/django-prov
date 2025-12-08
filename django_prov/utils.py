import getpass
import platform
import sys


def get_system_info_attributes(label):
    """
    Returns a List of attributes customized for the ProvDocument.
    :param label: Prefix of the namespace that has to be taken
    :return: List of Attributes
    """
    attributes = [(f'sys:python_version', sys.version)]
    attributes.append((f'sys:os', platform.platform()))
    attributes.append((f'sys:os_username', getpass.getuser()))
    return attributes
