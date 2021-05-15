import typing

from pandas import DataFrame,Series

from hbos_server.outputbase import OutputBase


class CollateOutput(OutputBase):


    def output(self, name: str, input_data: typing.Dict[str,DataFrame]) -> typing.Tuple[str, object]:
        """
        This output filter will combine two sources/queries based on a single key.

        This should be used with caution, for large data sets this will take a long time,
        and would probably be better to use MergeOutput and a single key.

        However, if you want to return a small list of objects and have everything combined, then this should be good for you

        """
        name = ""
        for merge_to_key in self.options["mergeKeys"]:
            merge_options = self.options["mergeKeys"][merge_to_key]
            name = merge_to_key
            df = input_data[name]
            for k in merge_options:
                options = k
                merge_value = options["mergeValue"]
                dest_value = options["mergeDestValue"]
                #input_data[name].loc[:,options["mergeDest"]] =None
                #df[options["mergeDest"]] = None
                #df[options["mergeDest"]] = df[options["mergeDest"]].astype(object)
                df[options["mergeDest"]] = Series()
                if not options["mergeSource"] in input_data: return name, input_data
                if len(input_data[options["mergeSource"]])==0 :return name, input_data

                merge_data = input_data[options["mergeSource"]]
                    #need to add a column
                #mask=merge_data[merge_value].values==input_data[name][dest_value].values
                #input_data[name][options["mergeDest"]] =  #merge_data[ mask ].to_dict('records')
                #del input_data[options["mergeSource"]]
                #input_data[name].combine(merge_data, self.combine_func)
                #x = input_data[name].join( merge_data, on=merge_value)

                for value in df[dest_value]:
                    merged = merge_data[ merge_data[merge_value] == value]
                    df = df[df[merge_value]==value].assign( **{options["mergeDest"]:[merged.to_dict('records')]}).astype(object)

                    #input_data[name][input_data[name][merge_value]== value][ options["mergeDest"]] = [merged.to_dict('records')]
                #x = input_data[name].loc[ input_data[dest_value] == merge_data[merge_value]]
                input_data[name] = df
        return name, input_data


    def combine_func(self, r1, r2):
        print(r1)
        print(r2)

