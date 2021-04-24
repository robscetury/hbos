from abc import abstractproperty, abstractmethod, abstractclassmethod, abstractstaticmethod


# Represents a source of data e.g. a database query,
# restful api or other entity that provides data
from typing import List, Dict


class SourceBase(object):

    @abstractmethod
    def execute(self, *args, **kwargs)  -> List[Dict[str,object]]:
        raise NotImplemented

    @property
    def options(self):
        return self._options

    @options.setter
    def set_options(self, value):
        self._options = value


    @property
    def name(self):
        return self._name

    @name.setter
    def set_name(self, value):
        self._name = value


    def __init__(self, name, options):
        self._name = name
        self._options = options
