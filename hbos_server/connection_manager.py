from hbos_server.utility import instantiate_with_kwargs
from typing import Dict, Any

# This is going to maintain a dictionary of named
# connections that are defined in the config
#  Question -- are file system stored objects handled here too?
# I think so, that way there is a constant API going forward

class ConnectionManager(object):
    def __init__(self):
        self._connections:Dict[str, ConnectionDef] = {}

    def initialize(self, connection_defs):
        for name in connection_defs:
            connection_defs[name]["name"] = name
            con_def = ConnectionDef(connection_defs[name])
            self._connections[name] = con_def


    def __getitem__(self, item):
        if item in self._connections:
            return self._connections[item].connection
        else:
            return None


class ConnectionDef(object):
    def __init__(self, definition):
        self._name = definition["name"]
        self._class = definition["class"]
        self._kwargs = definition["args"]
        del definition["name"]
        self.__reconnect()


    def __reconnect(self) -> object:
        self._conn = self.__create_connection(self.name, self._class, **self._kwargs)
        return self._conn

    def __create_connection(self, name, classname, **kwargs)->object:
        return instantiate_with_kwargs(classname, **kwargs)

    @property
    def name(self) -> str:
        return self._name
    @property
    def classname(self) ->str:
        return self._class
    @property
    def kwargs(self) -> Dict[str, Any]:
        return self._kwargs

    @property
    def connection(self):
        return self._conn
_manager = ConnectionManager()


def get_manager():
    global _manager
    if (_manager is None):
        _manager = ConnectionManager()
    return _manager
