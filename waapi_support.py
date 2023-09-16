from waapi import WaapiClient, CannotConnectToWaapiException, SequentialThreadExecutor

from waapi_support.waapi_uri import WAAPI_URI as URI
from waapi_support.wwise_path import RootPath
from waapi_support.waapi_opt_return import *


class QuerySelect:
    parent = 'parent'
    children = 'children'
    descendants = 'descendants'
    ancestors = 'ancestors'
    references = 'referencesTo'


class QueryWhere:
    @staticmethod
    def contains(name: str) -> list:
        return ['name:contains', name]

    @staticmethod
    def matches(name: str) -> list:
        return ['name:matches', name]

    @staticmethod
    def type_is(w_type: str) -> list:
        return ['type:isIn', [w_type]]

    @staticmethod
    def category_is(category: str) -> list:
        return ['category:isIn', [category]]


class CreateConflict:
    rename = 'rename'
    replace = 'replace'
    fail = 'fail'
    merge = 'merge'


class ImportOperation:
    create_new = 'createNew'
    use_existing = 'useExisting'
    replace_existing = 'replaceExisting'


class WaapiClientX(WaapiClient):

    def __init__(self, port=None, url=None, allow_exception=False, callback_executor=SequentialThreadExecutor):
        if port is not None and url is None:
            url = f'ws://127.0.0.1:{port}/waapi'
        super().__init__(url, allow_exception, callback_executor)
        self.set_full_return()

    # region 获取相关 实例方法
    def get_info(self):
        return self.call(URI.ak_wwise_core_getinfo)

    def get_version(self):
        result = self.get_info()
        if result:
            return result['version']['displayName'].replace('v', '')

    def set_full_return(self):
        ver_text = self.get_version()
        if not ver_text:
            self.full_return = rt_2022
            return
        if ver_text.startswith('2019'):
            self.full_return = rt_2019
        if ver_text.startswith('2021'):
            self.full_return = rt_2021
        if ver_text.startswith('2022'):
            self.full_return = rt_2022

    def __gen_options(self, return_list: list, full_return: bool = False):
        if full_return:
            options = {'return': self.full_return}
        else:
            options = {'return': SMALL_RETURN}
        if return_list is not None:
            options['return'] += return_list
        return options

    def __gen_get_args(self, w_obj):
        w_obj = str(w_obj)
        if w_obj.startswith('{'):
            args = {'from': {'id': [w_obj]}, 'transform': []}
        elif w_obj.startswith('\\'):
            args = {'from': {'path': [w_obj]}, 'transform': []}
        else:
            args = {'from': {'search': [w_obj]}, 'transform': []}
        return args

    def get_selected_objects(self, return_list: list = None, full_return=False) -> list:
        options = self.__gen_options(return_list, full_return)
        result = self.call(URI.ak_wwise_ui_getselectedobjects, options=options)
        if result and result['objects']:
            return result['objects']
        return []

    def __get(self, args, options):
        result = self.call(URI.ak_wwise_core_object_get, args, options=options)
        if result and result['return']:
            return result['return']
        return []

    def get(self, w_obj: str, select: str = None, where: list = None,
            return_list: list = None, full_return=False) -> list:
        args = self.__gen_get_args(w_obj)
        if select:
            args['transform'].append({'select': [select]})
        if where:
            args['transform'].append({'where': where})
        options = self.__gen_options(return_list, full_return)
        return self.__get(args, options)

    def get_from_type(self, w_type, return_list: list = None) -> list:
        args = {'from': {'ofType': [w_type]}}
        options = self.__gen_options(return_list)
        return self.__get(args, options)

    def get_property(self, w_obj, return_str):
        result = self.get(w_obj, return_list=[return_str])
        return result[0][return_str] if result else None

    def get_properties(self, w_obj) -> dict:
        result = self.call(
            URI.ak_wwise_core_object_getpropertyandreferencenames,
            {'object': w_obj})
        if not result or not result['return']:
            return {}
        return_list = ['@' + i for i in result['return']]
        result = self.get(w_obj, return_list=return_list, full_return=True)
        return result[0] if result else {}

    def get_path(self, w_obj):
        return self.get_property(w_obj, rt_path)

    def get_id(self, w_obj):
        return self.get_property(w_obj, rt_id)

    def get_type(self, w_obj):
        return self.get_property(w_obj, rt_type)

    def get_parent(self, w_obj):
        return self.get(w_obj, select=QuerySelect.parent)

    def get_children(self, w_obj):
        return self.get(w_obj, select=QuerySelect.children)

    def get_children_contains(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.children, where=QueryWhere.contains(name))

    def get_children_matches(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.children, where=QueryWhere.matches(name))

    def get_children_type_is(self, w_obj, w_type):
        return self.get(w_obj, select=QuerySelect.children, where=QueryWhere.type_is(w_type))

    def get_children_category_is(self, w_obj, category):
        return self.get(w_obj, select=QuerySelect.children, where=QueryWhere.category_is(category))

    def get_descendants(self, w_obj):
        return self.get(w_obj, select=QuerySelect.descendants)

    def get_descendants_contains(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.descendants, where=QueryWhere.contains(name))

    def get_descendants_matches(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.descendants, where=QueryWhere.matches(name))

    def get_descendants_type_is(self, w_obj, w_type):
        return self.get(w_obj, select=QuerySelect.descendants, where=QueryWhere.type_is(w_type))

    def get_descendants_category_is(self, w_obj, category):
        return self.get(w_obj, select=QuerySelect.descendants, where=QueryWhere.category_is(category))

    def get_ancestors(self, w_obj):
        return self.get(w_obj, select=QuerySelect.ancestors)

    def get_ancestors_contains(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.ancestors, where=QueryWhere.contains(name))

    def get_ancestors_matches(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.ancestors, where=QueryWhere.matches(name))

    def get_ancestors_type_is(self, w_obj, w_type):
        return self.get(w_obj, select=QuerySelect.ancestors, where=QueryWhere.type_is(w_type))

    def get_ancestors_category_is(self, w_obj, category):
        return self.get(w_obj, select=QuerySelect.ancestors, where=QueryWhere.category_is(category))

    def get_references(self, w_obj):
        return self.get(w_obj, select=QuerySelect.references)

    def get_references_contains(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.references, where=QueryWhere.contains(name))

    def get_references_matches(self, w_obj, name):
        return self.get(w_obj, select=QuerySelect.references, where=QueryWhere.matches(name))

    def get_references_type_is(self, w_obj, w_type):
        return self.get(w_obj, select=QuerySelect.references, where=QueryWhere.type_is(w_type))

    def get_references_category_is(self, w_obj, category):
        return self.get(w_obj, select=QuerySelect.references, where=QueryWhere.category_is(category))

    def get_bank_inclusions(self, w_obj) -> list:
        '''get event id list in bank'''
        data = []
        args = {'soundbank': w_obj}
        result = self.call(URI.ak_wwise_core_soundbank_getinclusions, args)
        if result and result['inclusions']:
            for i in result['inclusions']:
                data.append(i['object'])
        return data

    # endregion

    # region 设置相关 实例方法

    def set_property(self, w_obj, name, value):
        pass

    def set_notes(self, w_obj, value):
        args = {'object': w_obj, 'value': value}
        result = self.call(URI.ak_wwise_core_object_setnotes, args)
        if result == {}:
            return True
        return False

    # endregion

    # region 创建相关 实例方法

    def create(self, parent, w_type, name,
               onNameConflict=CreateConflict.merge,
               autoAddToSourceControl=True, **kwargs):
        args = {
            'parent': parent,
            'type': w_type,
            'name': name,
            'onNameConflict': onNameConflict,
            'autoAddToSourceControl': autoAddToSourceControl
        }
        if kwargs:
            for k, v in kwargs.items():
                if k in ['platform', 'notes', 'children']:
                    args[k] = v
                else:
                    args['@' + k] = v

        result = self.call(URI.ak_wwise_core_object_create, args)
        return result[rt_id] if result else None

    # endregion

    # region 导入相关 实例方法

    def import_audio(self, imports,
                     importOperation=ImportOperation.use_existing,
                     autoAddToSourceControl=True,
                     return_list=SMALL_RETURN) -> list:
        args = {
            'importOperation': importOperation,
            'imports': imports,
            'autoAddToSourceControl': autoAddToSourceControl
        }
        options = {'return': return_list}
        result = self.call(URI.ak_wwise_core_audio_import, args, options=options)

        return result['objects'] if result and result['objects'] else []

    # endregion

    # region UI相关

    def go_to_sync_group(self, obj_list: list, group_suffix=1):
        if not obj_list: return
        if not isinstance(group_suffix, int): return
        if group_suffix not in [1, 2, 3, 4]: return

        args = {
            "command": f"FindInProjectExplorerSyncGroup{group_suffix}",
            "objects": obj_list
        }
        self.call(URI.ak_wwise_ui_commands_execute, args)

    # endregion
