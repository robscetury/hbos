from typing import List, Dict

from hbos_server.defaultoutput import DefaultOutput
from .outputbase import OutputBase
from .workbase import WorkBase
from .sourcebase import SourceBase


class QuerySet(object):

    def __init__(self, name):
        self._name = name
        self._sources = list()
        self._work = list()
        self._outputs = list()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def set_name(self, value: str):
        self._name = value



    @property
    def sources(self) -> List[SourceBase]:
        return self._sources

    @sources.setter
    def set_sources(self, value: List[SourceBase]):
        # validated we've got a dictionary of SourceBases
        if isinstance(value, list):
            for k in value:
                if not isinstance(k, SourceBase):
                    raise NotSupportedException
        else:
            raise NotSupportedException
        self._sources = value


    @property
    def work(self) -> List[WorkBase]:
        return self._work

    @work.setter
    def set_work(self, value: List[WorkBase]):
        self._work = value



    @property
    def outputs(self) -> List[OutputBase]:
        return self._outputs

    @outputs.setter
    def set_outputs(self, value: List[WorkBase]):
        self._outputs = value

    @property
    def methods(self) -> List[str]:
        return self._methods

    @methods.setter
    def set_methods(self, value: List[str]):
        self._methods = value

    def execute(self, *params, **kwargs) -> Dict[str, object]:
        dataset = dict()
        results = dict()
        for k in self.sources:
            data = self.sources[k.name].execute(*params, *kwargs)
            outputs = self.outputs if len(self.outputs) > 0 else [DefaultOutput(**kwargs)]
            dataset[k.name] = data
            for output in outputs:
                name, modified = output.output(k.name, dataset)
                results[name] = modified
            work_calls = self.work
            for w in work_calls:
                work = w(**kwargs)
                work.execute(results)
        return results


class NotSupportedException(BaseException):
    pass
