from os import chdir
from os.path import dirname, exists
from typing import Dict

from flasgger import Swagger
from flask import Flask, make_response
from flask_restful import Api, abort

from .configuration import HBOSConfig
from .exceptions import BaseHBOSException, ObjectAlreadyExists
from .hbos_resource import HBOSResource, create_resource
from .queryset import QuerySet

swagger_config = {
    "headers": [],
    "openapi":"3.0.2",
    "components":{
        "schemas": {},
        "definitions":{}
    },
    "title": "",
    "version":"",
    "termsOfService":"",
    "static_url_path":"",
    "swagger_ui":True,
    "description":""
}

class HBOServer(Api):

    def __init__(self, app:Flask, config_file):
        #Flask.__init__(name)
        Api.__init__(self)

        if isinstance(config_file, HBOSConfig):
            self._config = config_file
        else:
            self._config = HBOSConfig(config_file)
        self._query_config: Dict[str, QuerySet] = self._config.querysets if not self._config.is_new else dict()
        self._resources = dict()
        self.configure_swagger(self._config)
        for name in self._query_config:
           self._resources[name]=create_resource(app=app, qs=self._query_config[name])
           self.add_resource(self._resources[name], name)

    @property
    def query_config(self) -> Dict[str, QuerySet ]:
        return self._query_config

    @query_config.setter
    def query_config(self, value: Dict[str,QuerySet]):
        self._query_config = value


    def configure_swagger(self, config:HBOSConfig, swagger_config:Dict=None):
        # swagger_config["title"] = self.title
        # swagger_config["version"] = self.version
        # swagger_config["termsOfService"] = self.terms_of_service
        # swagger_config["static_url_path"] = self.static_url_path
        # swagger_config["description"] = self.description
        for k in self.query_config:
            qs = self.query_config[k]
            #qs.add_swagger_config(swagger_config)
        # for k in self._config.schemas:
        #     swagger_config["components"]["schemas"][k] = self._config.schemas[k]

    @property
    def title(self):
        return self._config.title

    @property
    def version(self):
        return self._config.version

    @property
    def terms_of_service(self):
        return self._config.terms_of_service

    @property
    def static_url_path(self):
        return self._config.static_url_path

    @property
    def description(self):
        return self._config.description

    def handle_error(self, e:BaseHBOSException):
         """Return JSON instead of HTML for HTTP errors."""
         # start with the correct headers and status code from the error
         if(hasattr(e, "get_response")):
             try:

                 message = {"message": e.message,
                            "name": e.name,
                            "details": e.description}
                 status_code = 500
                 if hasattr(e, "status_code"):
                     status_code = e.status_code
                 response =  make_response(message, status_code) #e.get_response()

                 # replace the body with JSON

                 response.content_type = "application/json"

                 return response
             except Exception as e2:
                 pass
         return abort(e.status_code)



def start_hbos_server(args):

    config_file = args[-1]
    basedir = dirname(config_file)
    chdir(basedir)
    config = None
    if exists(config_file):
        config = HBOSConfig(config_file)
    app = Flask("HBOServer")

    api = HBOServer(app, config)

    #hbos = HBOServer(app, api, config)
    #hbos.configure_swagger(config, swagger_config)
    swag = Swagger(app, config=swagger_config, merge=True)
    api.init_app(app)
    app.run(port=config.port, host=config.interface, ssl_context = config.ssl_context if config.use_ssl else None)
