import typing
from typing import Dict

from pandas import DataFrame

from hbos_server.outputbase import OutputBase

class LazyLoadLinksOutput(OutputBase):
    def output(self, name: str, input_data: Dict[str,DataFrame]) -> typing.Tuple[str, object]:
        """
        This output filter will take specific fields and convert them to lazy load api links.

        So for example, a foreign key that you don't want to pull down everytime, or
        a set of children that may take a very long time to load.

        It's on the client to be able to interpret these values correctly.  (Sorry client folks. :) )
        """
        for querysetname in self.options["querysets"]:
            qs  =input_data[querysetname]
            lazy_options = self.options["querysets"][querysetname]
            for field in lazy_options["fields"]:
                qs[field["name"]].astype(object)
                qs[field["name"]] = qs[field["name"]].map(
                    lambda x:
                    { "rel": field["relName"], "link": field["link"].replace("{fieldvalue}", str(x))}
                )
            input_data[querysetname]=qs
        return name,input_data
