import re
from datetime import datetime

from gurux_dlms import GXUInt8, GXUInt16, GXStructure, GXUInt32, GXDateTime
from gurux_dlms.enums import DataType

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


def parse_clock_object_for_write(obj, reader, value, attribute):
    try:
        if attribute == '2':
            obj.time = datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
        elif attribute == '3':
            obj.timeZone = int(value)
        elif attribute == '5':
            if reader.read(obj, 8):
                obj.begin = datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
            else:
                raise Exception('Сначала надо включить девиацию!!')
        elif attribute == '6':
            if reader.read(obj, 8):
                obj.end = datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
            else:
                raise Exception('Сначала надо включить девиацию!!')
        elif attribute == '7':
            if reader.read(obj, 8):
                obj.deviation = int(value)
            else:
                raise Exception('Сначала надо включить девиацию!!')
        elif attribute == '8':
            if value == 'True':
                obj.enabled = True
            elif value == 'False':
                obj.enabled = False
            else:
                raise Exception('Только True или False!!!')
        else:
            raise Exception('Данный атрибут недоступен для записи!!!')
        return obj
    except Exception as e:
        raise
