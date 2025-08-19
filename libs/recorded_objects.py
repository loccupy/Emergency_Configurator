import re

from gurux_dlms import GXUInt8, GXUInt16, GXStructure
from gurux_dlms.enums import DataType, ObjectType


def set_value(obj, reader, value, attribute):
    if obj.getObjectType() == ObjectType.DATA:
        return set_value_for_data(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.REGISTER:
        return set_value_for_register(obj, reader, value, attribute)


def parse_data_object(obj, reader, value, attribute):
    if obj.logicalName in ['0.0.128.1.0.255', '0.0.128.2.0.255']:
        value = re.sub(r'[^0-9,]', '', value).split(',')
        obj.value = [GXUInt8(int(value[0])), GXUInt8(int(value[1]))]
        return obj
    elif obj.logicalName == '0.0.2.164.6.255':
        # Очищаем значение и разбиваем по запятой
        cleaned_value = re.sub(r'[^0-9,]', '', value).split(',')

        # Проверяем корректность данных
        if len(cleaned_value) != 6 * 30:
            raise ValueError("Неверное количество значений для логического имени")

        # Создаем правильную структуру данных
        new_val = []
        for z in range(6):
            row = GXStructure()
            for i in range(30):
                index = z * 30 + i  # Правильный расчет индекса
                row.append(GXUInt16(int(cleaned_value[index])))
            new_val.append(row)
        obj.value = new_val
        return obj
    elif reader.readType(obj, int(attribute)) != DataType.STRING:
        obj.value = int(value)
        return obj
    else:
        raise NotImplementedError('Пока этот объект не обрабатывается!!!')


def set_value_for_data(obj, reader, value, attribute):
    try:
        data_type = reader.readType(obj, int(attribute))
        obj = parse_data_object(obj, reader, value, attribute)
        obj.setDataType(int(attribute), data_type)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print("Ошибка при записи параметра класса Data >>", e)
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
