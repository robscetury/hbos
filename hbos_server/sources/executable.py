import typing
from typing import List, Dict
from json import loads
from hbos_server.sourcebase import SourceBase
from subprocess import Popen, PIPE
from os import linesep


class SimpleExecutable(SourceBase):

    def execute(self, *args, **kwargs) -> List[Dict[str, object]]:
        path = self.options["path"]
        exec_args: List[str] = loads(self.options["arguments"])

        replacements: List[str] = [x for x in exec_args if x.starts_with('<') and x in kwargs]
        for replace in replacements:
            exec_args[exec_args.index(replace)] = kwargs[replace]
        exec_args.insert(0, path)
        output = list()
        with Popen(exec_args, stdout=PIPE) as p:
            while True:
                line = p.stdout.readline()
                if not line: break
                output.append(line.replace(linesep, ""))
            p.stdout.close()

        property_name = kwargs["name"] if kwargs["name"] else "output"
        return {
            property_name: linesep.join(output)
        }
