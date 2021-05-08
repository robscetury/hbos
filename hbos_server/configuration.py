from typing import Dict, Union, Tuple

from .queryset import QuerySet
from json import load
from os.path import exists
from traceback import print_exc
import logging

class HBOSConfig(object):

    # noinspection PyBroadException
    def __init__(self, config_file):
        config = None
        self._new_install = False
        self._querysets: Dict[str, QuerySet] = dict()
        if exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config = load(f)
                    f.close()
            except:
                config = None
                self._new_install=True
                print_exc()
        if config is None:
            self._new_install = True
            return

        for k in config["querysets"]:
            self._querysets[k["name"]] = QuerySet(k["name"], k)
        if "ssl" in config:
            self._use_ssl = config["ssl"]["ssl"]
            self._ssl_context = config["ssl"]["ssl_context"]
        else:
            self._use_ssl = False
            self._ssl_context = None

        if "network" in config:
            self._port = config["network"]["port"]
            self._interface = config["network"]["interface"]
        else:
            self._port = 5055
            self._interface="localhost"

        if "logging" in config:
            self._loglevel = config["logging"]["loglevel"]
            self._logfile = config["logging"]["logfile"]
        else:
            self._loglevel = "warn"
            self._logfile = "./hbos.log"

        self._config = config

        self._loggingdebug = logging.INFO
        if(hasattr(logging, self._loglevel.upper())):
            self._loggingdebug = getattr(logging, self._loglevel.upper())

        logging.basicConfig(filename = self._logfile, level=self._loggingdebug )
    @property
    def use_ssl(self) -> bool:
        return self._use_ssl

    @property
    def ssl_context(self) -> Union[str, Tuple]:
        return self._ssl_context

    @property
    def port(self) -> int:
        return self._port

    @property
    def interface(self) -> str:
        return self._interface
    @property
    def querysets(self) -> Dict[str, QuerySet]:
        return self._querysets

    @querysets.setter
    def querysets(self, value: Dict[str, QuerySet]):
        self._querysets = value

    @property
    def is_new(self) -> bool:
        return self._new_install

    @is_new.setter
    def is_new(self, value: bool):
        self._new_install = value

    @property
    def title(self):
        if "title" in self._config:
            return self._config["title"]
        else:
            return "HBOS Server"
    @property
    def version(self):
        if "version" in self._config:
            return self._config["version"]
        else:
            return "0"

    @property
    def terms_of_service(self):
        if "termsOfService" in self._config:
            return self._config["termsOfService"]
        else:
            return ""

    @property
    def static_url_path(self):
        if "staticUrlPath" in self._config:
            return self._config["staticUrlPath"]
        else:
            return ""
    @property
    def description(self):
        if "description" in self._config:
            return self._config["description"]
        else:
            return ""

    @property
    def schemas(self) -> Dict[str, Dict]:
        if "schemas" in self._config:
            return self._config["schemas"]
        else:
            return {}
