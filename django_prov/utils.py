import getpass
import platform
import sys


def get_system_info_attributes(label="sys"):
    """
    Returns a List of attributes customized for the ProvDocument.
    :param label: Prefix of the namespace that has to be taken
    :return: List of Attributes
    """
    attributes = [(f'{label}:python_version', sys.version), (f'{label}:os', platform.platform()),
                  (f'{label}:os_username', getpass.getuser())]
    return attributes
