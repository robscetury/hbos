import logging
import traceback
import typing
from importlib import import_module
from typing import List

from flask import request

from hbos_server.defaultoutput import DefaultOutput
from .exceptions import InvalidObject
from .outputbase import OutputBase
from .sourcebase import SourceBase
from .validationbase import ValidationBase, Validation
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
        self._work: List[WorkBase] = list()
        self._outputs: List[OutputBase] = list()
        self._validations :List[ValidationBase] = list()
        self._methods = ["GET"]
        self._end_points = dict()
        if config_options is not None:
            self.name = config_options["name"]
            for k in config_options["sources"]:
                self.sources.append(instantiate_worker_object(k))
            if "work" in config_options:
                for k in config_options["work"]:
                    self.work.append(instantiate_worker_object(k))
            if "outputs" in config_options:
                for k in config_options["outputs"]:
                    self._outputs.append(instantiate_worker_object(k))
            if("methods" in config_options):
                self.methods = config_options["methods"]
            if "endPoints" in config_options:
                self._end_points=config_options["endPoints"]
            else:
                self._end_points=dict()

            if "schemas" in config_options:
                self._schemas = config_options["schemas"]
            else:
                self._schemas = list()
            # for s in self.sources:
            #     if not s.swagger_files is None:
            #         self._swagger_files = s.swagger_files
                # loaded_swaggers = dict()
                # for k in self._swagger_files:
                #
                #         swag = self._swagger_files[k]
                #         if os.path.exists(swag):
                #             with open( os.path.abspath( os.path.normpath(swag)), "r") as f:
                #                 loaded_swaggers[k] = f.read()
                #         else:
                #             loaded_swaggers[k] = swag
                # self._swagger_files = loaded_swaggers
    @property
    def schemas(self):
        return self._schemas

    @property
    def end_points(self):
        return self._end_points

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
        if len(self._outputs)==0: return [ DefaultOutput("default",
                                                         {})]
        return self._outputs

    @outputs.setter
    def outputs(self, value: List[OutputBase]):
        self._outputs = value

    @property
    def validations(self):
        return self._validations

    @validations.setter
    def validations(self,value:List[ValidationBase]):
       self._validations = value

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
            dataset[k.name] = data
        results = self.process_results(dataset, results)
        return results

    def process_results(self, dataset, results):
        modified = None
        for output in self.outputs:
                name, modified = output.output(self.name, dataset)
        return modified


    def validate(self, body):
        if len(self.validations)==0: return Validation(True,"")
        for v in self.validations:
            valid = v.validate(body)
            if not valid.is_valid:
                raise InvalidObject("Unable to validate object", valid.message )

    def put(self, req:request, *args, **kwargs) -> typing.Optional[object]:
        body = self.undo_outputs(req.json)
        if(not self.validate(body)): raise
        dataset = dict()
        results = dict()
        for k in self.sources:
            original_values = k.retrieve(*args, **kwargs)
            if k.name in body:
                data = k.update(body[k.name],original_values, *args, **kwargs)
                dataset[k.name]=data
        results = self.process_results(dataset, results)
        return results

    def post(self, req:request, *args, **kwargs) -> typing.Optional[object]:
        body = self.undo_outputs(req.json)
        dataset = dict()
        results = dict()
        for k in self.sources:
            if k.name in body:
                data = k.create(body[k.name], *args, **kwargs)
                dataset[k.name]=data
        results = self.process_results(dataset, results)
        return results

    def delete(self,req: request ,*args, **kwargs)-> typing.Optional[object]:
        body = self.undo_outputs(req.json)
        dataset = dict()
        results = dict()
        for k in self.sources:
            data = k.delete(body[k.name],*args, **kwargs)
            dataset[k.name]=data
        results = self.process_results(dataset, results)
        return results

    def undo_outputs(self, body) -> typing.Dict[str, typing.Any]:
        modified = None
        for output in self.outputs:
            name, modified = output.undo_output(self.name, body)
            body=modified
        return modified

    def execute(self, method: str, req:request, *args, **kwargs) -> typing.Optional[object]:
        try:
            if(method=="get"):
                return self.get(req, *args, **kwargs)
            elif method == "put":
                return self.put(req, *args, **kwargs)
            elif method == "post":
                return self.post(req, *args, **kwargs)
            elif method == "delete":
                return self.delete(req, *args, **kwargs)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            raise e

    # def add_swagger_config(self, swagger_config):
    #     for k in self.end_points:
    #         swagger_config["components"]["definitions"][k] = self.end_points[k]



class NotSupportedException(BaseException):
    pass
