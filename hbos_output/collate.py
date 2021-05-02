import typing

from pandas import DataFrame

from hbos_server.outputbase import OutputBase


class Collate(OutputBase):

    #for each queryset name in input_data
    # for e
    def output(self, name: str, input_data: DataFrame) -> typing.Tuple[str, object]:
        raise NotImplemented