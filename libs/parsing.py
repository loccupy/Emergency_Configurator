import re
from datetime import datetime

from gurux_dlms import GXUInt8, GXUInt16, GXStructure, GXUInt32, GXDateTime
from gurux_dlms.enums import DataType
from gurux_dlms.objects import GXDLMSHdlcSetup, GXDLMSCaptureObject, GXDLMSData, GXDLMSDisconnectControl, \
    GXDLMSRegister, GXDLMSAutoConnect


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
            raise Exception('Атрибут не поддерживает запись!!!')
        return obj
    except Exception as e:
        raise


def load_display_readout(all_values):
    capture_objects = []
    for obis in all_values:
        # if index == number_of_elements:
        #     break
        # if obis in old_capture_objects_names:
        #     continue

        if obis in "0.0.22.0.0.255 0.1.22.0.0.255 0.2.22.0.0.255":
            obj = GXDLMSHdlcSetup(obis)
            capture_object = GXDLMSCaptureObject(2, 0)
            item = (obj, capture_object)
            capture_objects.append(item)
            continue
        elif obis in "0.0.96.1.2.255 0.0.96.1.8.255 0.0.96.4.3.255 0.0.96.1.0.255 0.0.0.9.1.255 0.0.0.9.2.255":
            obj = GXDLMSData(obis)
            capture_object = GXDLMSCaptureObject(2, 0)
            item = (obj, capture_object)
            capture_objects.append(item)
            continue
        elif obis == "0.0.96.3.10.255":
            obj = GXDLMSDisconnectControl(obis)
            capture_object = GXDLMSCaptureObject(3, 0)
            item = (obj, capture_object)
            capture_objects.append(item)
            continue
        elif obis not in "0.2.22.0.0.255":
            obj = GXDLMSRegister(obis)
            capture_object = GXDLMSCaptureObject(2, 0)
            item = (obj, capture_object)
            capture_objects.append(item)
            continue
    return capture_objects


def parse_profile_generic_object_for_write(obj, reader, value, attribute):
    if obj.logicalName == '0.0.21.0.1.255':
        if attribute == '4':
            obj.capturePeriod = int(value)
        elif attribute == '3':
            value = re.sub(r'[^0-9,.]', '', value)
            value = value.split(',')
            capture_objects = load_display_readout(value)
            obj.captureObjects = capture_objects
    elif attribute == '4':
        obj.capturePeriod = int(value)
    else:
        raise Exception('Атрибут не поддерживает запись!!!')
    return obj


def parse_auto_connect_object_for_write(obj, reader, value, attribute):
    if attribute == '2' and value in ['101', '104']:
        obj.mode = value
    elif attribute == '3':
        obj.repetitions = int(value)
    elif attribute == '4':
        obj.repetitionDelay = int(value)
    elif attribute == '5':
        # value = re.sub(r'[^0-9,.:* ]', '', value)
        # value = value.split(',')
        # value[0] = value[0].strip()
        #
        # value[1] = value[1].strip()
        #
        # start = GXDateTime(value[0], "%d.%m.%Y %H:%M:%S")
        #
        # end = GXDateTime(value[1], "%d.%m.%Y %H:%M:%S")
        #
        # obj.callingWindow.append((start, end))  #  'NoneType' object has no attribute 'seconds' ???   *.*.* 13:11:31, *.*.* 14:17:31
        raise Exception('Атрибут пока не обрабатывается для записи!!!')

    elif attribute == '6':
        value = re.sub(r'[^0-9,.:*]', '', value)
        value = value.split(',')
        obj.destinations = value
    else:
        raise Exception('Атрибут не поддерживает запись!!!')
    return obj


def parse_communication_port_protection_object_for_write(obj, reader, value, attribute):
    if attribute == '2':
        if value in ['1', '2']:
            obj.protectionMode = int(value)
        else:
            raise Exception('Для protectionMode доступны только значения 1 или 2..')
    elif attribute == '3':
        obj.allowedFailedAttempts = int(value)
    elif attribute == '4':
        obj.initialLockoutTime = int(value)
    elif attribute == '5':
        obj.steepnessFactor = int(value)
    elif attribute == '6':
        obj.maxLockoutTime = int(value)
    else:
        raise Exception('Атрибут не поддерживает запись!!!')
    return obj


def parse_iec_hdlc_setup_object_for_write(obj, reader, value, attribute):
    if attribute == '2':
        if value in ['5', '6', '7', '8', '9']:
            obj.communicationSpeed = int(value)
        else:
            raise Exception('Для protectionMode доступны только значения 5, 6, 7, 8, 9..')
    elif attribute == '5':
        obj.maximumInfoLengthTransmit = int(value)
    elif attribute == '6':
        obj.maximumInfoLengthReceive = int(value)
    elif attribute == '8':
        obj.inactivityTimeout = int(value)
    else:
        raise Exception('Атрибут не поддерживает запись!!!')
    return obj


def parse_action_schedule_object_for_write(obj, reader, value, attribute):
    if attribute == '3':
        obj.type_ = int(value)
        if value in ['1', '2', '3', '4', '5']:
            obj.type_ = int(value)
        else:
            raise Exception('Для Type доступны только значения 1, 2, 3, 4, 5..')
    elif attribute == '4':
        value = re.sub(r'[^0-9,.:* ]', '', value)
        value = value.split(',')
        for i, time in enumerate(value):
            time = time.strip()
            time_to_write = GXDateTime(time, "%d.%m.%Y %H:%M:%S")
            # time_to_write.skip = execution_time[i].skip   *.*.* 21:00:00,  *.*.* 22:00:00
            obj.executionTime.append(time_to_write)
    else:
        raise Exception('Атрибут не поддерживает запись!!!')
    return obj
