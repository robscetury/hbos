import abc
from typing import List, Dict
from abc import abstractmethod


# represents work done on an external system
# for example "When saving new employees
# in HR, create new LDAP account
class WorkBase(object):

    @abstractmethod
    def execute(self, data: Dict[str,List[Dict[str, object]]]) -> bool:
        raise NotImplemented

    def __init__(self, options):
        self._options = options

    @property
    def options(self):
        return self._options

    @options.setter
    def set_options(self, value):
        self._options = value
