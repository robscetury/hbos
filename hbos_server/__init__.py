from typing import Dict

from flask import Flask
from flask_restful import Api

from .configuration import HBOSConfig
from .hbos_resource import HBOSResource, create_resource
from .queryset import QuerySet
from os import chdir
from os.path import dirname

class HBOServer(object):

    def __init__(self, api,  configFile):
        #Flask.__init__(name)
        self._config = HBOSConfig(configFile)
        self._query_config: Dict[str, QuerySet] = self._config.querysets if not self._config.is_new else dict()
        self._resources = dict()
        for name in self._query_config:
            self._resources[name]=create_resource(qs=self._query_config[name])

            api.add_resource(self._resources[name], name)

    @property
    def query_config(self) -> Dict[str, QuerySet ]:
        return self._query_config

    @query_config.setter
    def query_config(self, value: Dict[str,QuerySet]):
        self._query_config = value



def start_hbos_server(args):

    app = Flask("HBOServer")
    api = Api(app)
    configFile = args[-1]
    basedir = dirname(configFile)
    chdir(basedir)
    hbos = HBOServer(api, args[-1])
    app.run()
