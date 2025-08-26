import re
from datetime import datetime

from gurux_dlms import GXUInt8, GXUInt16, GXStructure, GXUInt32
from gurux_dlms.enums import DataType, ObjectType

from libs.parsing import parse_data_object_for_write


def set_value(obj, reader, value, attribute):
    if obj.getObjectType() == ObjectType.DATA:
        return set_value_for_data(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.REGISTER:
        return set_value_for_register(obj, reader, value, attribute)
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

        obj.value = int(value)
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса Register >>", e)
        return False
