import typing
from importlib import import_module
from typing import List

from flask import request

from hbos_server.defaultoutput import DefaultOutput
from .outputbase import OutputBase
from .sourcebase import SourceBase
from .workbase import WorkBase


def get_library_and_class_names(importstatement):
    name = importstatement.split('.')
    return '.'.join(name[:-1]), name[-1]


def get_class(name):
    module_name, classname = get_library_and_class_names(name)
    m = import_module(module_name)
    return getattr(m, classname)


def instantiate_worker_object(options):
    classObject = get_class(options["class"])
    return classObject(options["name"], options)


class QuerySet(object):

    def __init__(self, name, config_options=None):
        self._name = name
        self._sources = list()
        self._work = list()
        self._outputs = list()
        self._methods = ["GET"]
        if config_options is not None:
            self.name = config_options["name"]
            for k in config_options["sources"]:
                self.sources.append(instantiate_worker_object(k))
            if "work" in config_options:
                for k in config_options["work"]:
                    self.work.append(instantiate_worker_object(k))
            if "outputs" in config_options:
                for k in config_options["outputs"]:
                    self.outputs.append(instantiate_worker_object(k))
            if("methods" in config_options):
                self.methods = config_options["methods"]


    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def sources(self) -> List[SourceBase]:
        return self._sources

    @sources.setter
    def sources(self, value: List[SourceBase]):
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
    def work(self, value: List[WorkBase]):
        self._work = value

    @property
    def outputs(self) -> List[OutputBase]:
        if len(self._outputs)==0: return [ DefaultOutput({})]
        return self._outputs

    @outputs.setter
    def outputs(self, value: List[WorkBase]):
        self._outputs = value

    @property
    def methods(self) -> List[str]:
        return self._methods

    @methods.setter
    def methods(self, value: List[str]):
        self._methods = value

    def get(self, req : request, *args, **kwargs) -> typing.Optional[object]:
        dataset = dict()
        results = dict()

        for k in self.sources:
            data = k.retrieve(*args, **kwargs)
            outputs = self.outputs if len(self.outputs) > 0 else [DefaultOutput(kwargs)]
            dataset[k.name] = data
        results = self.process_results(dataset, results)
        return results

    def process_results(self, dataset, results):
        modified = None
        for output in self.outputs:
            name, modified = output.output(self.name, dataset)
        return modified



    def put(self, req:request, *args, **kwargs) -> typing.Optional[object]:
        body = req.json
        dataset = dict()
        results = dict()
        for k in self.sources:
            original_values = k.retrieve(*args, **kwargs)
            data = k.update(body[k.name],original_values, *args, **kwargs)
            dataset[k.name]=data
        results = self.process_results(dataset, results)
        return results

    def post(self, req:request, *args, **kwargs) -> typing.Optional[object]:
        body = req.json
        dataset = dict()
        results = dict()
        for k in self.sources:
            data = k.create(body[k.name], *args, **kwargs)
            dataset[k.name]=data
        results = self.process_results(dataset, results)
        return results

    def delete(self,req: request ,*args, **kwargs)-> typing.Optional[object]:
        body = req.json
        dataset = dict()
        results = dict()
        for k in self.sources:
            data = k.delete(body[k.name],*args, **kwargs)
            dataset[k.name]=data
        results = self.process_results(dataset, results)
        return results

    def execute(self, method: str, req:request, *args, **kwargs) -> typing.Optional[object]:
        if(method=="get"):
            return self.get(req, *args, **kwargs)
        elif method == "put":
            return self.put(req, *args, **kwargs)
        elif method == "post":
            return self.post(req, *args, **kwargs)
        elif method == "delete":
            return self.post(req, *args, **kwargs)



class NotSupportedException(BaseException):
    pass
