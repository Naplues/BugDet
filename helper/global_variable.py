# -*- coding: utf-8 -*-

def init():
    global global_variable_dict
    global_variable_dict = {}

def set_value(name, value):
    global_variable_dict[name] = value

def get_value(name, defValue=None):
    try:
        return global_variable_dict[name]
    except KeyError:
        return defValue