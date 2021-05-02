import typing
from typing import List, Dict
from json import loads
from hbos_server.sourcebase import SourceBase
from subprocess import Popen, PIPE
from os import linesep


class SimpleExecutable(SourceBase):

    def update(self, update_values: List[Dict[str, typing.Any]],
               original_values: List[Dict[str, typing.Any]] = None,*args,**kwargs) -> bool:
        pass

    def delete(self, to_delete: List,*args,**kwargs) -> bool:
        pass

    def undo_update(self, original_value: Dict[str, typing.Any]):
        pass

    def undo_delete(self, attempt_delete: Dict[str, typing.Any]):
        pass

    def undo_create(self, attempt_create: Dict[str, typing.Any]):
        pass

    def create(self, List,*args,**kwargs):
        pass

    def retrieve(self, *args, **kwargs) -> List[Dict[str, typing.Any]]:
        path = self.options["path"]
        exec_args: List[str] = loads(self.options["arguments"])

        replacements: List[str] = [x for x in exec_args if x.startswith('<') and x in kwargs]
        for replace in replacements:
            exec_args[exec_args.index(replace)] = kwargs[replace]
        exec_args.insert(0, path)
        output:List[str] = list()
        with Popen(exec_args, stdout=PIPE) as p:
            while True:
                line = str( p.stdout.readline())
                if not line: break
                output.append(line.replace(str(linesep), ""))
            p.stdout.close()

        property_name = kwargs["name"] if kwargs["name"] else "output"
        return  list(dict(       {property_name: linesep.join(output)} ))
