from typing import Dict

from .queryset import QuerySet
from json import load
from os.path import exists


class HBOSConfig(object):

    # noinspection PyBroadException
    def __init__(self, configFile):
        config = None
        self._new_install = False
        self._querysets: Dict[str, QuerySet] = dict()
        if exists(configFile):
            try:
                with open(configFile, "r") as f:
                    config = load(f)
                    f.close()
            except:
                config = None
                self._new_install=True
        if config is None:
            self._new_install = True
            return

        for k in config["querysets"]:
            self._querysets[k] = QuerySet(config["querysets"][k])

    @property
    def querysets(self) -> Dict[str, QuerySet]:
        return self._querysets

    @querysets.setter
    def set_querysets(self, value: Dict[str, QuerySet]):
        self._querysets = value

    @property
    def is_new(self) -> bool:
        return self._new_install

    @is_new.setter
    def set_is_new(self, value: bool):
        self._new_install = value