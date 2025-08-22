import re
from datetime import datetime

from gurux_dlms import GXUInt8, GXUInt16, GXStructure, GXUInt32
from gurux_dlms.enums import DataType, ObjectType


def set_value(obj, reader, value, attribute):
    if obj.getObjectType() == ObjectType.DATA:
        return set_value_for_data(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.REGISTER:
        return set_value_for_register(obj, reader, value, attribute)
    else:
        raise NotImplementedError('Пока этот класс не обрабатывается!!!')


def parse_data_object_for_write(obj, reader, value, attribute):
    if obj.logicalName in ['0.0.128.1.0.255', '0.0.128.2.0.255']:
        value = re.sub(r'[^0-9,]', '', value).split(',')
        obj.value = [GXUInt8(int(value[0])), GXUInt8(int(value[1]))]
        return obj
    elif obj.logicalName == '0.0.2.164.6.255':
        # Очищаем значение и разбиваем по запятой
        cleaned_value = re.sub(r'[^0-9,]', '', value).split(',')

        # Проверяем корректность данных
        if len(cleaned_value) != 6 * 30:
            raise ValueError("Неверное количество значений для гармоник")

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
    elif obj.logicalName == '0.0.2.164.11.255':
        cleaned_value = re.sub(r'[^0-9,]', '', value).split(',')
        if len(cleaned_value) != 6:
            raise ValueError("Неверное количество значений для Порогов срабатывания детектора короткого замыкания")
        new_value = GXStructure()
        for i in range(6):
            new_value.append(GXUInt32(int(cleaned_value[i])))
        obj.value = new_value
        return obj
    # elif obj.logicalName == "0.0.96.2.1.255":
    #     res = reader.read(obj, 2)
    #     he = f'{hex(res[0])[2:]}{hex(res[1])[2:]}'
    #     year = int(he, 16)
    #     month = res[2]
    #     day = res[3]
    #     hour = res[5]
    #     minute = res[6]
    #     second = res[7]
    #     # переносим в тип datetime для сравнения
    #     actual = datetime.strptime(f'{month}/{day}/{year} {hour}:{minute}:{second}', "%m/%d/%Y %H:%M:%S")
    elif reader.readType(obj, int(attribute)) != DataType.STRING:
        obj.value = int(value)
        return obj
    elif reader.readType(obj, int(attribute)) == DataType.STRING:
        obj.value = value
        return obj
    else:
        raise NotImplementedError('Пока этот объект не обрабатывается!!!')


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
