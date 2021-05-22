from os.path import abspath, normpath
from types import MethodType

from flask import request, Flask
from flask_restful import Resource
from pandas import DataFrame

from .queryset import QuerySet

resource_count = 0

def add_swagger(obj, method, docstring):
    docstring = abspath( normpath (docstring))
    method.__doc__ =  f"\nfile: {docstring}\n"
    new_method = MethodType(method, obj)
    #new_method.__doc__ = docstring
    #
    #new_method.__doc__ =
    return new_method

def create_resource(app:Flask, qs:QuerySet,
                    *args, **kwargs):
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
                         "get": get if "GET" in qs.methods else None,
                         "put": put if "PUT" in qs.methods else None,
                         "delete": delete if "DELETE" in qs.methods else None,
                         "post": post if "POST" in qs.methods else None

                     }
                     )
    if "get" in qs.end_points:
        get = add_swagger(new_class, get, qs.end_points["get"])
    if "put" in qs.end_points:
        put = add_swagger(new_class, put, qs.end_points["put"])
    if "post" in qs.end_points:
        post = add_swagger(new_class, put, qs.end_points["put"])
    if "delete" in qs.end_points:
        delete = add_swagger(new_class, delete, qs.end_points["delete"])


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
