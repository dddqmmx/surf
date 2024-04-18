# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/3/26 17:03
File Name       : __init__.py.py
Last Edit Time  : 2024/4/9
"""
import os
import importlib

MODULES_PATH = os.path.dirname(__file__)
modules_dir = os.listdir(MODULES_PATH)

all_url_patterns = []

for module_name in modules_dir:
    module_routing_path = os.path.join(MODULES_PATH, module_name, 'core', 'routing.py')
    if os.path.isfile(module_routing_path):
        try:
            # 导入模块
            module_routing = importlib.import_module(f".{module_name}.core.routing", package="surf.modules")
            # 提取url_patterns
            url_patterns = getattr(module_routing, 'url')
            all_url_patterns.extend(url_patterns)
        except AttributeError:
            # 没有找到url_patterns，忽略模块
            continue
        except Exception as e:
            print(e)
            continue
routing = all_url_patterns
