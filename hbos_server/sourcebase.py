import typing
from abc import abstractmethod
from pandas import DataFrame
# Represents a source of data e.g. a database query,
# restful api or other entity that provides data
from typing import List, Dict


class SourceBase(object):

    @abstractmethod
    def create(self, objects_to_create: List[Dict[str, typing.Any]],*args,**kwargs) -> DataFrame:
        raise NotImplemented

    @abstractmethod
    def retrieve(self, *args, **kwargs) -> List[Dict[str, typing.Any]]:
        raise NotImplemented

    @abstractmethod
    def update(self, update_values: List[Dict[str, typing.Any]],
               original_values: List[Dict[str, typing.Any]] = None,*args,**kwargs) -> DataFrame:
        raise NotImplemented

    @abstractmethod
    def delete(self, to_delete: List,*args,**kwargs) -> bool:
        raise NotImplemented

    @abstractmethod
    def undo_update(self, original_value: Dict[str, typing.Any]):
        raise NotImplemented

    @abstractmethod
    def undo_delete(self, attempt_delete: Dict[str, typing.Any]):
        raise NotImplemented

    @abstractmethod
    def undo_create(self, attempt_create: Dict[str, typing.Any]):
        raise NotImplemented

    @property
    def options(self) -> Dict[str, typing.Any]:
        return self._options

    @options.setter
    def options(self, value: Dict[str, typing.Any]):
        self._options = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    # noinspection PyTypeChecker
    def undo(self, verb: str, objs=List[Dict[str, typing.Any]], original_objs=List[Dict[str, typing.Any]]):
        to_call = None
        original_value = False
        if verb == "create":
            to_call = self.undo_create
        elif verb == "delete":
            to_call = self.undo_delete
        elif verb == "update":
            to_call = self.undo_update
            original_value = True
        if to_call is None:
            for i in range(0, len(objs)):
                o = objs[i]
                if original_value and original_objs is not None:
                    o = original_objs[i]
                to_call(o)

    def __init__(self, source_name, source_options):
        self._name = source_name
        self._options = source_options
        if "swaggerFiles" in source_options:
            self._swagger_files = source_options["swaggerFiles"]
        else:
            self._swagger_files = {}


    @property
    def swagger_files(self):
        return self._swagger_files
