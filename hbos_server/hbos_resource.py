from flask import request
from flask_restful import Resource
from pandas import DataFrame

from .queryset import QuerySet

resource_count = 0


def create_resource(qs: QuerySet, *args, **kwargs):
    global resource_count

    def get_queryset(self):
        return self._queryset

    def set_queryset(self, value):
        self._queryset = value



    def get(self, *args, **kwargs):
        result = self.queryset.execute("get", request, *args, **kwargs)
        clean_result(result)
        return result

    def clean_result(result):
        if (isinstance(result, dict)):
            for k in result.keys():
                item_records = result[k]
                if isinstance(item_records, DataFrame):
                    result[k] = item_records.to_dict('records')

    def put(self, *args, **kwargs):
        result = self.queryset.execute("put", request, *args, **kwargs)
        clean_result(result)
        return result

    def post(self, *args, **kwargs):
        result = self.queryset.execute("post", request, *args, **kwargs)
        clean_result(result)
        return result

    def delete(self, *args, **kwargs):
        result = self.queryset.execute("delete", request, *args, **kwargs)
        clean_result(result)
        return result

    new_class = type(f"__HBOSResource{resource_count}",
                     (Resource,),
                     {
                         "_queryset": qs,
                         "queryset": property(get_queryset, set_queryset),
                         "get": get,
                         "put": put,
                         "delete": delete,
                         "post": post

                     }
                     )
    resource_count += 1
    return new_class


class HBOSResource(Resource):

    def __init__(self, qs: QuerySet):
        self._queryset = qs
        self.__name__ = qs.name

    @property
    def queryset(self):
        return self._queryset

    @queryset.setter
    def queryset(self, value):
        self._queryset = value

    def get(self, *args, **kwargs):
        return self.queryset.execute("get", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.queryset.execute("put", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.queryset.execute("post", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.queryset.execute("delete", *args, **kwargs)
