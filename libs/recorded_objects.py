import re
from datetime import datetime

from gurux_dlms import GXUInt8, GXUInt16, GXStructure, GXUInt32, GXDateTime
from gurux_dlms.enums import DataType, ObjectType

from libs.parsing import parse_data_object_for_write, parse_clock_object_for_write, \
    parse_profile_generic_object_for_write, parse_auto_connect_object_for_write


def set_value(obj, reader, value, attribute):
    if obj.getObjectType() == ObjectType.DATA:
        return set_value_for_data(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.REGISTER:
        return set_value_for_register(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.CLOCK:
        return set_value_for_clock(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.PROFILE_GENERIC:
        return set_value_for_profile_generic(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.GPRS_SETUP:
        return set_value_for_gprs_setup(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.AUTO_CONNECT:
        return set_value_for_auto_connect(obj, reader, value, attribute)
    else:
        raise NotImplementedError('Пока этот класс не обрабатывается!!!')


def set_value_for_data(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        obj = parse_data_object_for_write(obj, reader, value, attribute)
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса Data >>", e)
        return False


def set_value_for_register(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        scalar = reader.read(obj, 3)[0]
        obj.value = int(int(value) / scalar)
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса Register >>", e)
        return False


def set_value_for_clock(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        obj = parse_clock_object_for_write(obj, reader, value, attribute)
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса Clock >>", e)
        return False


def set_value_for_profile_generic(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        obj = parse_profile_generic_object_for_write(obj, reader, value, attribute)
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса Profile Generic >>", e)
        return False


def set_value_for_gprs_setup(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        if attribute == '2':
            obj.apn = value
        else:
            raise Exception('Атрибут не поддерживает запись!!!')
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса GPRSSetup >>", e)
        return False


def set_value_for_auto_connect(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        obj = parse_auto_connect_object_for_write(obj, reader, value, attribute)
        # obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса AutoConnect >>", e)
        return False
