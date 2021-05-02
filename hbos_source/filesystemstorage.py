import os
import typing
import uuid
from json import load, dump
from os.path import join, normpath, abspath
from typing import Dict, List

from hbos_server.sourcebase import SourceBase

def read_idx(path:str, item_key=None):
    idx_path = os.path.join(path, ".idx")
    idx={}
    if os.path.exists(idx_path):
        with open(idx_path, "r") as f:
            idx = load(f)
    else:
        for root,dirs,fnames in os.walk(path):
            for fname in fnames:
               try:
                   with open( join(root, fname), "r") as f:
                       obj = load(f)
                   if item_key in obj:
                       idx[obj[item_key]] = fname
               except:
                   pass # it's not an hbos file, don't worry
    return idx

def delete_from_idx(path:str, item_key_value):
    idx = read_idx(path)
    del idx[item_key_value]
    write_idx(path, idx)

def write_idx(path:str, idx):
    idx_path = os.path.join(path, ".idx")
    with open(idx_path,"w") as f:
        dump(idx, f)

def write_file(path:str, obj:typing.Any, item_key_value=None):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, "w+") as f:
        dump(obj, f)
    if item_key_value is not None:
        idx = read_idx(os.path.dirname(path))
        idx[item_key_value]=os.path.basename(path)
        write_idx(os.path.dirname(path), idx)

def read_file(path:str):
    with open(path, "r+") as f:
        return load(f)


class ObjectAlreadyExists(Exception):
    pass


class ObjectNotFound(Exception):
    pass


class FileSystemStorage(SourceBase):

    def create(self, objs_to_create: List[Dict[str, typing.Any]],*args, **kwargs) -> List[Dict[str, typing.Any]]:
        all_created = True
        hold_on_to_e = None
        for item in objs_to_create:
            try:
                if "item_key" in self.options:
                    idx = read_idx(self.storage_directory, self.options["item_key"])
                    if idx is not None:
                        obj = self.load_by_item_key(idx,  kwargs if self.options["item_key"] in kwargs else item)
                        if obj is not None:
                            raise ObjectAlreadyExists
                if not "_hbos_id" in item:
                    item["_hbos_id"] = str(uuid.uuid1())
                write_file(join(self.storage_directory, f"{item['_hbos_id']}.json"), item, self.get_item_key(item))
            except Exception as e:
                all_created = False
                hold_on_to_e=e
                break
        if not all_created:
            self.undo("create", objs_to_create)
            raise hold_on_to_e
        return objs_to_create

    def retrieve(self, *args, **kwargs) -> List[Dict[str, typing.Any]]:

        if "_hbos_id" in kwargs:
            return [ read_file( join(self.storage_directory, f"{kwargs['_hbos_id']}.json"))]
        elif self.has_item_key(kwargs):
            idx = read_idx(self.storage_directory, self.options["item_key"])
            if self.get_item_key(kwargs) in idx:
                result = list()
                result.append(self.load_by_item_key(idx, kwargs))
                return result
        else:
            result = []
            # get a whole directory....
            for root,dirs,fnames in os.walk(self.storage_directory):
                for fname in fnames:
                    if fname.startswith("."): continue
                    result.append( read_file( join(root, fname)))
            return result

    def load_by_item_key(self, idx, kwargs):
        filepath = self.get_file_by_item_key(idx, kwargs)
        if filepath is None or not os.path.exists(filepath): return None
        with open( filepath ) as f:
            return load(f)

    def get_file_by_item_key(self, idx, kwargs):
        try:
            return join(self.storage_directory, idx[self.get_item_key(kwargs)])
        except:
            return None

    def get_item_key(self, kwargs):
        return kwargs[self.options["item_key"]]

    def has_item_key(self, kwargs):
        return "item_key" in self.options and self.options["item_key"] in kwargs

    def update(self, update_values: List[Dict[str, typing.Any]],
               original_values: List[Dict[str, typing.Any]] = None, *args, **kwargs) -> List[Dict[str, typing.Any]]:
        #original_values = []
        all_written = True
        hold_on_to_e = None
        if self.has_item_key(kwargs) and len(update_values)>0:
            obj = update_values[0]
            path = join(self.storage_directory, f"{obj['_hbos_id']}.json")
            write_file(path, obj , self.get_item_key(kwargs))
        for i in range(0, len(update_values)):
            item = update_values[i]
            _hbos_id = None
            if "_hbos_id" in item:
                _hbos_id = item["_hbos_id"]
            elif not "_hbos_id" in item and "item_key" in self.options:
                #idx = read_idx(self.storage_directory, self.options["item_key"])
                _hbos_ids = [ x["_hbos_id"] for x in original_values if "_hbos_id" in x and x[self.options["item_key"]] == item[self.options["item_key"]] ]
                _hbos_id = _hbos_ids[0] if len(_hbos_ids)>0 else None
            if _hbos_id is None:
                raise ObjectNotFound
            else:
                item["_hbos_id"] = _hbos_id
            path = join(self.storage_directory, f"{_hbos_id}.json")
            original_values.append(read_file(path))
            try:
                curr = None
                if "item_key" in self.options and hasattr(item,self.options["item_key"]):
                    orig = [x for x in original_values if "_hbos_id" in x and x[self.options["item_key"]] == item[self.options["item_key"]] ][0]
                    curr = getattr(item, self.options["item_key"])
                    if curr != orig:
                        delete_from_idx(self.storage_directory, orig)
                write_file(path, item, curr)
            except Exception as e:
                hold_on_to_e= e
                all_written = False
                break
        if not all_written:
            self.undo("update", update_values, original_values)
            raise hold_on_to_e
        return update_values

    def delete(self, to_delete: List[Dict[str, typing.Any]],*args,
               **kwargs) -> bool:
        original_values = self.retrieve(self, *args, **kwargs)
        all_deleted = True
        hold_on_to_e = None
        if self.has_item_key(kwargs):
            item_key_value = self.get_item_key(kwargs)
            idx = read_idx(self.storage_directory, self.options["item_key"])
            filename = self.get_file_by_item_key(idx,kwargs)
            obj = self.load_by_item_key(idx, kwargs)
            self.delete_object(obj, item_key_value)
            return True
        else:
            for i in range(0, len(to_delete)):
                item = to_delete[i]
                _hbos_id = None
                if "_hbos_id" in item:
                    _hbos_id = item["_hbos_id"]
                elif not "_hbos_id" in item and "item_key" in self.options:
                    #idx = read_idx(self.storage_directory, self.options["item_key"])
                    _hbos_ids = [ x["_hbos_id"] for x in original_values if "_hbos_id" in x and x[self.options["item_key"]] == item[self.options["item_key"]] ]
                    _hbos_id = _hbos_ids[0] if len(_hbos_ids)>0 else None
                if _hbos_id is None:
                    raise ObjectNotFound
                else:
                    item["_hbos_id"] = _hbos_id
                try:

                    path = join(self.storage_directory, f"{item['_hbos_id']}.json")
                    original_values.append(read_file(path))
                    self.delete_object(item)
                    if "item_key" in self.options and item[self.options["item_key"]]:
                        delete_from_idx(self.storage_directory, item[self.options["item_key"]])

                except Exception as e:
                    all_deleted = False
                    hold_on_to_e = e
                    break
            if not all_deleted:
                self.undo("delete", original_values)
                raise hold_on_to_e
            return all_deleted

    def undo_update(self, original_value: Dict[str, typing.Any]):
        if "_hbos_id" in original_value:
            write_file( join(self.storage_directory, f"{original_value['_hbos_id']}.json"), original_value, self.get_item_key(original_value))

    def undo_delete(self, attempt_delete: Dict[str, typing.Any]):
        if "_hbos_id" in attempt_delete:
            write_file( join(self.storage_directory, f"{attempt_delete['_hbos_id']}.json"), attempt_delete, self.get_item_key(attempt_delete))

    def undo_create(self, attempt_create: Dict[str, typing.Any]):
        try:
            self.delete_object(attempt_create)
        except Exception as e:
            pass

    def delete_object(self, attempt_delete, *args, **kwargs):
        if "_hbos_id" in attempt_delete:
            path = join(self.storage_directory, f"{attempt_delete['_hbos_id']}.json")
            os.unlink(path)


    @property
    def storage_directory(self):
        return abspath( normpath(typing.cast(str, self.options["path"])))