import os
import typing
import uuid
from json import load, dump
from os.path import join
from typing import Dict, List

from ..sourcebase import SourceBase


def write_file(path:str, obj:typing.Any):
    with open(path, "w+") as f:
        dump(obj, f)

def read_file(path:str):
    with open(path, "r+") as f:
        return load(f)

class FileSystemStorage(SourceBase):

    def create(self, objs_to_create: List[Dict[str, typing.Any]]) -> bool:
        all_created = True
        hold_on_to_e = None
        for item in objs_to_create:
            try:
                if not "_hbos_id" in item:
                    item["_hbos_id"] = str(uuid.uuid1())
                write_file(join(self.storage_directory, f"{item['_hbos_id']}.json"), item)
            except Exception as e:
                all_created = False
                hold_on_to_e=e
                break
        if not all_created:
            self.undo("create", objs_to_create)
            raise hold_on_to_e
        return all_created

    def retrieve(self, *args, **kwargs) -> List[Dict[str, typing.Any]]:

        if "_hbos_id" in kwargs:
            return [ read_file( join(self.storage_directory, f"{kwargs['_hbos_id']}.json"))]
        else:
            result = []
            # get a whole directory....
            for root,dirs,fnames in os.walk(self.storage_directory):
                for fname in fnames:
                    result.append( read_file( join(root, fname)))
            return result


    def update(self, update_values: List[Dict[str, typing.Any]],
               original_values: List[Dict[str, typing.Any]] = None) -> bool:
        original_values = []
        all_written = False
        hold_on_to_e = None
        for i in range(0, len(update_values)):
            item = update_values[i]
            path = join(self.storage_directory, f"{item['_hbos_id']}.json")
            original_values.append(read_file(path))
            try:
                write_file(path, item)
            except Exception as e:
                hold_on_to_e= e
                all_written = False
                break
        if not all_written:
            self.undo("update", update_values, original_values)
            raise hold_on_to_e
        return all_written

    def delete(self, to_delete: List[Dict[str, typing.Any]]) -> bool:
        original_values = []
        all_deleted = False
        hold_on_to_e = None
        for i in range(0, len(to_delete)):
            item = to_delete[i]
            try:
                path = join(self.storage_directory, f"{item['_hbos_id']}.json")
                original_values.append(read_file(path))
                self.delete_object(item)
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
            write_file( join(self.storage_directory, f"{original_value['_hbos_id']}.json"), original_value)

    def undo_delete(self, attempt_delete: Dict[str, typing.Any]):
        if "_hbos_id" in attempt_delete:
            write_file( join(self.storage_directory, f"{attempt_delete['_hbos_id']}.json"), attempt_delete)

    def undo_create(self, attempt_create: Dict[str, typing.Any]):
        try:
            self.delete_object(attempt_create)
        except Exception as e:
            pass

    def delete_object(self, attempt_delete):
        if "_hbos_id" in attempt_delete:
            path = join(self.storage_directory, f"{attempt_delete['_hbos_id']}.json")
            os.unlink(path)

    @property
    def storage_directory(self):
        return typing.cast(str, self.options["path"])