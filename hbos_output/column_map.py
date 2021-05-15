import typing
from typing import Dict

from pandas import DataFrame

from hbos_server.outputbase import OutputBase

class ColumnMapOutput(OutputBase):
    def output(self, name: str, input_data: Dict[str,DataFrame]) -> typing.Tuple[str, object]:
        """
        This output filter will take specific fields and convert them to lazy load api links.

        So for example, a foreign key that you don't want to pull down everytime, or
        a set of children that may take a very long time to load.

        It's on the client to be able to interpret these values correctly.  (Sorry client folks. :) )
        """
        for querysetname in self.options["querysets"]:
            qs  =input_data[querysetname]
            columns = qs.columns
            new_columns = []
            mapping_options = self.options["querysets"][querysetname]
            fields = mapping_options["fields"]
            for c in columns:
                if c in fields:
                    if fields[c] is None:
                        del qs[c]
                    else:
                        new_columns.append(fields[c])
                else:
                    new_columns.append(c)
            qs.columns = new_columns
            input_data[querysetname]=qs

        return name,input_data
