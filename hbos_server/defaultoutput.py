from abc import ABC
from typing import Tuple, List, Dict

import typing

from .outputbase import OutputBase


class DefaultOutput(OutputBase, ABC):

    def output(self, name: str, input_data : List[Dict[str,object]]) -> Tuple[str, object]:
        return name, input_data

    def undo_output(self, name: str, input_data: Dict[str,List[Dict[str, typing.Any]]]) -> Tuple[str, object]:
        return name, input_data