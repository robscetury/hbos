from werkzeug.exceptions import HTTPException

class BaseHBOSException(HTTPException):
    def __init__(self, message, status_code=None, payload=None, *args, **kwargs):
        HTTPException.__init__(self, message, *args,**kwargs)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidObject(BaseHBOSException):
    status_code = 500
    def __init__(self, message, payload=None):
        BaseHBOSException.__init__(self, message,status_code= 500 , payload = payload)



class QuerySetNotFound(BaseHBOSException):
    status_code = 404
    def __init__(self, message, payload=None):
        BaseHBOSException.__init__(self, message,status_code= 500 , payload = payload)



class ObjectAlreadyExists(BaseHBOSException):
    def __init__(self):
        BaseHBOSException.__init__(self, "Object Already Exists", status_code = 500)



class ObjectNotFound(BaseHBOSException):
    def __init__(self):
        BaseHBOSException.__init__(self, "Object Not Found", status_code = 400)

