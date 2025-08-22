from datetime import datetime

from gurux_dlms.enums import ObjectType, DataType


def read_obj(obj, reader, attribute):
    if obj.getObjectType() == ObjectType.DATA:
        return get_value_from_data(obj, reader, attribute)
    elif obj.getObjectType() == ObjectType.REGISTER:
        return get_value_from_register(obj, reader, attribute)
    elif obj.getObjectType() == ObjectType.GPRS_SETUP:
        return get_value_from_gprs(obj, reader, attribute)
    elif obj.getObjectType() == ObjectType.CLOCK:
        return get_value_from_clock(obj, reader, attribute)
    elif obj.getObjectType() == ObjectType.IEC_HDLC_SETUP:
        return get_value_from_iec_hdlc_setup(obj, reader, attribute)
    elif obj.getObjectType() == ObjectType.LIMITER:
        return get_value_from_limiter(obj, reader, attribute)
    else:
        return reader.read(obj, int(attribute))


def get_value_from_data(obj, reader, attribute):
    if obj.logicalName in ['0.0.42.0.0.255', '0.0.96.1.0.255', '0.0.96.1.1.255', '0.0.96.1.2.255', '0.0.96.1.3.255',
                           '0.0.96.1.4.255', '0.0.96.1.6.255', '0.0.96.1.8.255', '0.0.96.1.9.255']:
        value = reader.read(obj, int(attribute)).decode()
    elif obj.logicalName == '0.0.0.9.2.255':
        value = reader.read(obj, int(attribute)).value.strftime('%d.%m.%Y')
    elif obj.logicalName in ['0.0.96.2.1.255', '0.0.96.2.5.255', '0.0.96.2.7.255', '0.0.96.2.12.255',
                             '0.0.96.2.13.255', '0.0.96.20.1.255', '0.0.96.20.6.255', '0.0.96.20.16.255',
                             '0.0.96.50.1.255', '0.0.96.50.11.255', '0.0.96.50.6.255', '0.0.96.50.26.255',
                             '0.0.96.50.31.255']:
        res = reader.read(obj, int(attribute))
        he = f'{hex(res[0])[2:]}{hex(res[1])[2:]}'
        year = int(he, 16)
        month = res[2]
        day = res[3]
        hour = res[5]
        minute = res[6]
        second = res[7]
        # переносим в тип datetime для сравнения
        value = datetime.strptime(f'{month}/{day}/{year} {hour}:{minute}:{second}', "%m/%d/%Y %H:%M:%S")  # нулевые не обрабатывает
    elif obj.logicalName == '0.0.96.5.135.255':
        last_event_for_push = reader.read(obj, 2)

        n_1 = str(last_event_for_push[0][0])
        n_2 = str(last_event_for_push[0][1])
        n_3 = str(last_event_for_push[0][2])
        n_4 = str(last_event_for_push[0][3])
        n_5 = str(last_event_for_push[0][4])
        n_6 = str(last_event_for_push[0][5])

        value = [n_1 + '.' + n_2 + '.' + n_3 + '.' + n_4 + '.' + n_5 + '.' + n_6, last_event_for_push[1]]
    else:
        value = reader.read(obj, int(attribute))
    return value


def get_value_from_register(obj, reader, attribute):
    value = reader.read(obj, int(attribute))
    return value


def get_value_from_gprs(obj, reader, attribute):
    value = reader.read(obj, int(attribute))
    return value


def get_value_from_clock(obj, reader, attribute):
    value = reader.read(obj, int(attribute))
    return value


def get_value_from_iec_hdlc_setup(obj, reader, attribute):
    value = reader.read(obj, int(attribute))
    return value


def get_value_from_limiter(obj, reader, attribute):
    value = reader.read(obj, int(attribute))
    return value