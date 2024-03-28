# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/3/26 16:39
File Name       : __init__.py
Last Edit Time  : 
"""
print(__file__)
try:
    import base_db_pg
    from session_util import Session
    print("done")
except Exception as e:
    print(e)
    print("fuck you")