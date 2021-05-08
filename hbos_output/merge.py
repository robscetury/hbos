from typing import Dict, List
from pandas import DataFrame
import typing

from hbos_server.outputbase import OutputBase

class MergeOutput(OutputBase):

    def output(self, name: str, input_data: DataFrame) -> typing.Tuple[str, object]:
        """
        For simple parent child relations where we are getting the parent "mergeToKeys"
        and the children in mergeFromKeys will be merged to a new property value
        in the first item in mergetToKeys
        """
        name = ""
        for merge_to_key in self.options["mergeKeys"]:
            merge_options = self.options["mergeKeys"][merge_to_key]
            name = merge_to_key
            for k in merge_options:
                options = k
                if not options["mergeSource"] in input_data: return name, input_data
                if len(input_data[options["mergeSource"]])==0 :return name, input_data
                mergeData = input_data[options["mergeSource"]]
                #need to add a column
                input_data[merge_to_key][options["mergeDest"]] = mergeData.to_dict('records')
                del input_data[options["mergeSource"]]
        return name, input_data


    def undo_output(self, name: str, input_data: Dict[str,List[Dict[str, typing.Any]]]) -> typing.Tuple[str, object]:
        pass