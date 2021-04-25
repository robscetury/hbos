import abc
from typing import List, Dict, Tuple


# represents a transform of input data
# for example mapping the database columns to new names
# converting from JSON to XML
# or DataBase results to a CSV file

# OutputBases may be chained together for each
# SourceBase in a QuerySet
# Or chained together for the whole QuerySet
import typing


class OutputBase(object):

    @abc.abstractmethod
    def output(self, name: str, input_data: Dict[str,List[Dict[str, typing.Any]]]) -> Tuple[str, object]:
        raise NotImplemented

    def __init__(self, options):
        self._options = options

    @property
    def options(self):
        return self._options

    @options.setter
    def set_options(self, value):
        self._options = value

