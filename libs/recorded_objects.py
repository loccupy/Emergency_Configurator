import re
from datetime import datetime

from gurux_dlms import GXUInt8, GXUInt16, GXStructure, GXUInt32, GXDateTime
from gurux_dlms.enums import DataType, ObjectType

from libs.parsing import parse_data_object_for_write, parse_clock_object_for_write, \
    parse_profile_generic_object_for_write, parse_auto_connect_object_for_write, \
    parse_communication_port_protection_object_for_write, parse_iec_hdlc_setup_object_for_write, \
    parse_action_schedule_object_for_write


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
    elif obj.getObjectType() == ObjectType.COMMUNICATION_PORT_PROTECTION:
        return set_value_for_communication_port_protection(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.IEC_HDLC_SETUP:
        return set_value_for_iec_hdlc_setup(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.TCP_UDP_SETUP:
        return set_value_for_tcp_udp_setup(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.SPECIAL_DAYS_TABLE:
        return set_value_for_special_days_table(obj, reader, value, attribute)
    elif obj.getObjectType() == ObjectType.ACTION_SCHEDULE:
        return set_value_for_action_schedule(obj, reader, value, attribute)
    # elif obj.getObjectType() == ObjectType.ACTION_SCHEDULE:
    #     return set_value_for_action_schedule(obj, reader, value, attribute)
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
        obj = parse_auto_connect_object_for_write(obj, reader, value, attribute)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса AutoConnect >>", e)
        return False


def set_value_for_communication_port_protection(obj, reader, value, attribute):
    try:
        obj = parse_communication_port_protection_object_for_write(obj, reader, value, attribute)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса CommunicationPortProtection >>", e)
        return False


def set_value_for_iec_hdlc_setup(obj, reader, value, attribute):
    try:
        obj = parse_iec_hdlc_setup_object_for_write(obj, reader, value, attribute)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса HdlcSetup >>", e)
        return False


def set_value_for_tcp_udp_setup(obj, reader, value, attribute):
    try:
        if attribute == '2':
            obj.port = int(value)
        elif attribute == '6':
            obj.inactivityTimeout = int(value)
        else:
            raise Exception('Атрибут не поддерживает запись!!!')
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса TcpUdpSetup >>", e)
        return False


def set_value_for_special_days_table(obj, reader, value, attribute):
    try:
        if attribute == '2':
            value = re.sub(r'[^0-9,.]', '', value)
            value = value.split(',')
            index = int(value[0])
            date = datetime.strptime(value[1], '%d.%m.%Y')
            day_id = int(value[2])
            reader.insert_special_days_table(index, date, day_id)
        else:
            raise Exception('Атрибут не поддерживает запись!!!')

        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса SpecialDaysTable >>", e)
        return False


def set_value_for_action_schedule(obj, reader, value, attribute):
    try:
        obj = parse_action_schedule_object_for_write(obj, reader, value, attribute)

        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print(f"Ошибка при записи атрибута {attribute} объекта {obj.logicalName} класса ActionSchedule >>", e)
        return False
