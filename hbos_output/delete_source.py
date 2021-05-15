import typing
from typing import Dict

from pandas import DataFrame

from hbos_server.outputbase import OutputBase

class DeleteSourceOutput(OutputBase):
    def output(self, name: str, input_data: Dict[str,DataFrame]) -> typing.Tuple[str, object]:
        """
        This output filter will delete data sets that are no longer needed...for example,
        one that has been collated and you do not want to delete the data.

        [Unlike MergeOutput, CollateOuput does NOT delete the relevant data as it might be used as part of a later output filter.]
        """
        for del_to_key in self.options["deleteKeys"]:
            del input_data[del_to_key]
        return name, input_data