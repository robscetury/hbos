from typing import Dict

from flask import Flask, request, Response, jsonify
from flask_restful import Api, Resource, reqparse
from .queryset import QuerySet
from .configuration import HBOSConfig



class HBOServer(Resource):

    def __init__(self, app,  configFile):
        #Flask.__init__(name)
        self._config = HBOSConfig(configFile)
        self._query_config: Dict[str, QuerySet] = self._config.querysets if self._config.is_new else dict()
        for name in self._query_config:
            qs=self._query_config[name]
            app.add_url_rule(
                name,
                qs.execute,
                methods=qs.methods
            )

    @property
    def query_config(self) -> Dict[str, QuerySet ]:
        return self._query_config

    @query_config.setter
    def set_query_config(self, value: Dict[str,QuerySet]):
        self._query_config = value



def start_hbos_server(args):

    app = Flask("HBOServer")
    hbos = HBOServer(app, args[-1])
    app.run()
