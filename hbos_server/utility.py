from importlib import import_module


def get_library_and_class_names(importstatement):
    name = importstatement.split('.')
    return '.'.join(name[:-1]), name[-1]


def get_class(name):
    module_name, classname = get_library_and_class_names(name)
    m = import_module(module_name)
    return getattr(m, classname)


def instantiate_worker_object(options):
    classObject = get_class(options["class"])
    return classObject(options["name"], options)

def instantiate_with_kwargs(classname, **kwargs):
    classObject = get_class(classname)
    return classObject(**kwargs)