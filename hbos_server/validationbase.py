from abc import abstractmethod

class Validation(object):

    def __init__(self, is_valid:bool, message:str):
        self._is_valid = is_valid
        self._message = message

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.setter
    def is_valid(self,value:bool):
        self._is_valid = value

    @property
    def message(self)->str:
        return self._message

    @message.setter
    def message(self,value:str):
        self._message = value


class ValidationBase(object):
    @abstractmethod
    def validate(self, object) -> Validation:
        raise NotImplemented

