from typing import Dict

from flask import Flask
from flask_restful import Resource

from .configuration import HBOSConfig
from .queryset import QuerySet


class HBOServer(Resource):

    def __init__(self, app,  configFile):
        #Flask.__init__(name)
        self._config = HBOSConfig(configFile)
        self._query_config: Dict[str, QuerySet] = self._config.querysets if not self._config.is_new else dict()
        for name in self._query_config:
            qs=self._query_config[name]
            print(f"adding path {qs.name}")
            app.add_url_rule(
                name,
                qs.execute.__name__,
                qs.execute,
                methods=qs.methods
            )

    @property
    def query_config(self) -> Dict[str, QuerySet ]:
        return self._query_config

    @query_config.setter
    def query_config(self, value: Dict[str,QuerySet]):
        self._query_config = value



def start_hbos_server(args):

    app = Flask("HBOServer")
    hbos = HBOServer(app, args[-1])
    app.run()
