from waapi import WaapiClient, CannotConnectToWaapiException, SequentialThreadExecutor

from waapi_support.waapi_uri import WAAPI_URI as URI
from waapi_support.wwise_path import RootPath
from waapi_support.waapi_opt_return import *


class QuerySelect:
    parent = 'parent'
    children = 'children'
    descendants = 'descendants'
    ancestors = 'ancestors'
    references = 'references'


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


class MyClient(WaapiClient):

    def __init__(self, port=None, url=None, allow_exception=False, callback_executor=SequentialThreadExecutor):
        if port is not None and url is None:
            url = f'ws://127.0.0.1:{port}/waapi'
        super().__init__(url, allow_exception, callback_executor)

    # region 获取相关 实例方法
    def get_info(self):
        return self.call(URI.ak_wwise_core_getinfo)

    def get_version(self):
        result = self.get_info()
        if result:
            return result['version']['displayName'].replace('v', '')

    def __gen_options(self, return_list: list, full_return: bool = False):
        if full_return:
            options = {'return': FULL_RETURN}
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


if __name__ == '__main__':
    from waapi_object import WaapiObject
    from pprint import pprint

    try:
        with MyClient(allow_exception=False) as client:
            info = client.get_info()
            selected_id = client.get_selected_objects()[0]['id']
            print(client.get_properties(selected_id))

            # print(client.get_from_type(WaapiObject.SoundBank))
            #
            # print(client.get('hello', select=QuerySelect.parent))
            # print(client.get('hello', where=QueryWhere.type_is(WaapiObject.Sound)))
            #
            # print(client.get_descendants_contains(selected_id, 'hello'))
            # print(client.get_descendants_matches(selected_id, 'hello'))
            # print(client.get_descendants_type_is(selected_id, WaapiObject.Sound))

            # client.create(selected_id, WaapiObject.Sound, 'name', Volume=-5, IsStreamingEnabled=True)

            path = RootPath.actor_mixer_hierarchy
            pprint(client.get_descendants(path))

            client.disconnect()

    except CannotConnectToWaapiException:
        print('WAAPI 连接失败！请检查是否已启用 WAAPI ！')
    # except Exception as e:
    #     print(f'错误：{e}')
