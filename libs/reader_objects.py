from datetime import datetime
from zoneinfo import ZoneInfo

from gurux_dlms import GXUInt16, GXUInt8, GXDateTime
from gurux_dlms.enums import ObjectType, DataType, Unit
from gurux_dlms.objects import GXDLMSActionItem, GXDLMSPushSetup, GXDLMSClock, GXDLMSGprsSetup, GXDLMSRegister, \
    GXDLMSActionSchedule, GXDLMSSpecialDay, GXDLMSScript, GXDLMSScriptAction, GXDLMSSeasonProfile, GXDLMSWeekProfile, \
    GXDLMSDayProfile, GXDLMSDayProfileAction, GXDLMSGSMDiagnostic, GXDLMSGSMCellInfo, GXAdjacentCell, \
    GXDLMSObjectDefinition
from gurux_dlms.objects.enums import ControlState, ControlMode, BaudRate, ClockBase, AutoConnectMode, \
    SingleActionScheduleType, GsmStatus, GsmCircuitSwitchStatus, GsmPacketSwitchStatus, SortMethod

from libs.ProtectionMode import ProtectionMode
from libs.ProtectionStatus import ProtectionStatus
# from libs.parsing import parse_buffer_for_read_from_profile_generic


# Все кроме ImageTranser, ecuritySetup и AssociationLogicalName (всего 7 объектов для 1ф)
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

    elif obj.getObjectType() == ObjectType.DISCONNECT_CONTROL:
        return get_value_from_disconnect_control(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.PUSH_SETUP:
        return get_value_from_push_setup(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.AUTO_CONNECT:
        return get_value_from_auto_connect(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.ACTION_SCHEDULE:
        return get_value_from_action_schedule(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.SPECIAL_DAYS_TABLE:
        return get_value_from_special_days_table(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.SCRIPT_TABLE:
        return get_value_from_script_table(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.ACTIVITY_CALENDAR:
        return get_value_from_activity_calendar(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.TCP_UDP_SETUP:
        return get_value_from_tcp_udp_setup(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.IP4_SETUP:
        return get_value_from_ip4_setup(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.GSM_DIAGNOSTIC:
        return get_value_from_gsm_diagnostic(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.COMMUNICATION_PORT_PROTECTION:
        return get_value_from_communication_port_protection(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.PROFILE_GENERIC:
        return get_value_from_profile_generic(obj, reader, attribute)

    elif obj.getObjectType() == ObjectType.REGISTER_ACTIVATION:
        return get_value_from_register_activation(obj, reader, attribute)
    else:
        return reader.read(obj, int(attribute))


def get_value_from_data(obj, reader, attribute):
    if obj.logicalName in ['0.0.42.0.0.255', '0.0.96.1.0.255', '0.0.96.1.1.255', '0.0.96.1.2.255', '0.0.96.1.3.255',
                           '0.0.96.1.4.255', '0.0.96.1.6.255', '0.0.96.1.8.255', '0.0.96.1.9.255'] and attribute == '2':
        value = reader.read(obj, int(attribute)).decode()
    elif obj.logicalName == '0.0.0.9.2.255' and attribute == '2':
        value = reader.read(obj, int(attribute)).value.strftime('%d.%m.%Y')
    elif obj.logicalName in ['0.0.96.2.1.255', '0.0.96.2.5.255', '0.0.96.2.7.255', '0.0.96.2.12.255',
                             '0.0.96.2.13.255', '0.0.96.20.1.255', '0.0.96.20.6.255', '0.0.96.20.16.255',
                             '0.0.96.50.1.255', '0.0.96.50.11.255', '0.0.96.50.6.255', '0.0.96.50.26.255',
                             '0.0.96.50.31.255'] and attribute == '2':
        res = reader.read(obj, int(attribute))
        he = f'{hex(res[0])[2:]}{hex(res[1])[2:]}'
        year = int(he, 16)
        month = res[2]
        day = res[3]
        hour = res[5]
        minute = res[6]
        second = res[7]
        if year == 0:
            value = "НУЛЕВАЯ ЗАПИСЬ"
        else:
            # переносим в тип datetime для сравнения
            value = datetime.strptime(f'{day}/{month}/{year} {hour}:{minute}:{second}',
                                      "%d/%m/%Y %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")  # нулевые не обрабатывает
    elif obj.logicalName == '0.0.96.5.135.255' and attribute == '2':
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
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        scaler = reader.read(obj, 3)[0]
        value = f'value = {temp * scaler}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        member = Unit(temp[1])
        value = f'scaler = {temp[0]}, Unit = {member.name}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_gprs(obj, reader, attribute):
    value = reader.read(obj, int(attribute))
    return value


def get_value_from_clock(obj, reader, attribute):
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute)).value.strftime("%d.%m.%Y %H:%M:%S")
        value = f'time = {temp}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = f'timeZone = {temp}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        value = f'status = {temp}'
    elif attribute == '5':
        value = f'begin = {reader.read(obj, int(attribute)).value.strftime("%d.%m.%Y %H:%M:%S")}'
    elif attribute == '6':
        value = f'end  = {reader.read(obj, int(attribute)).value.strftime("%d.%m.%Y %H:%M:%S")}'
    elif attribute == '7':
        temp = reader.read(obj, int(attribute))
        value = f'deviation = {temp}'
    elif attribute == '8':
        temp = reader.read(obj, int(attribute))
        value = f'enabled = {temp}'
    elif attribute == '9':
        temp = reader.read(obj, int(attribute))
        member = ClockBase(temp)
        value = f'clockBase = {member.name}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_iec_hdlc_setup(obj, reader, attribute):
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        member = BaudRate(temp)
        value = f'communicationSpeed = {member.name}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = f'windowSizeTransmit = {temp}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        value = f'windowSizeReceive = {temp}'
    elif attribute == '5':
        value = f'maximumInfoLengthReceive = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'maximumInfoLengthTransmit  = {reader.read(obj, int(attribute))}'
    elif attribute == '7':
        temp = reader.read(obj, int(attribute))
        value = f'interCharachterTimeout = {temp}'
    elif attribute == '8':
        temp = reader.read(obj, int(attribute))
        value = f'inactivityTimeout = {temp}'
    elif attribute == '9':
        temp = reader.read(obj, int(attribute))
        value = f'deviceAddress = {temp}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_limiter(obj, reader, attribute):
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'monitoredValue  = {reader.read(obj, int(attribute))}'  #  monitoredValue  = None
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = f'thresholdActive = {temp}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        value = f'thresholdNormal = {temp}'
    elif attribute == '5':
        value = f'thresholdEmergency = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'minOverThresholdDuration  = {reader.read(obj, int(attribute))}'
    elif attribute == '7':
        temp = reader.read(obj, int(attribute))
        value = f'minUnderThresholdDuration = {temp}'
    elif attribute == '8':
        temp = reader.read(obj, int(attribute))
        value = f'emergencyProfile = {temp}'
    elif attribute == '9':
        temp = reader.read(obj, int(attribute))
        value = f'emergencyProfileGroupIDs = {temp}'
    elif attribute == '10':
        temp = reader.read(obj, int(attribute))
        value = f'emergencyProfileActive = {temp}'
    elif attribute == '11':
        value = reader.read(obj, int(attribute))
        value = f'[actionOverThreshold, actionUnderThreshold] = [{value[0].logicalName}: {value[0].scriptSelector}, {value[1].logicalName}: {value[1].scriptSelector}]'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_disconnect_control(obj, reader, attribute):
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'outputState  = {reader.read(obj, int(attribute))}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        member = ControlState(temp)
        value = f'controlState = {member.name}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        member = ControlMode(temp)
        value = f'controlMode = {member.name}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


# здесь могут возникнуть проблемы с объектом GXDLMSPushSetup по причине разной реализации в нашей и базовой библ-ах
def get_value_from_push_setup(obj, reader, attribute):
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'pushObjectList = {[i[0].logicalName for i in reader.read(obj, int(attribute))]}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = f'(service, destination, message) = service: {temp[0]}, destination: {temp[1]}, message: {temp[2]}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        value = f'communicationWindow = {temp[0][0].value.strftime("%d.%m.%Y %H:%M:%S"), temp[0][1].value.strftime("%d.%m.%Y %H:%M:%S")}'
    elif attribute == '5':
        value = f'randomisationStartInterval = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'numberOfRetries = {reader.read(obj, int(attribute))}'
    elif attribute == '7':  #  здесь может ругаться на GXUInt16
        value = f'repetitionDelay = {reader.read(obj, int(attribute))}'
    elif attribute == '8':
        value = f'pushInterface = {reader.read(obj, int(attribute))}'
    elif attribute == '9':
        value = f'clientAddress = {reader.read(obj, int(attribute))}'
    elif attribute == '10':
        f'??? = {reader.read(obj, int(attribute))}'
    elif attribute == '11':
        value = f'methodOfConfirmation = {reader.read(obj, int(attribute))}'
    elif attribute == '12':
        f'??? = {reader.read(obj, int(attribute))}'
    elif attribute == '13':
        value = f'lastConfirmation = {reader.read(obj, int(attribute))}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_auto_connect(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        member = AutoConnectMode(temp)
        value = f'Mode = {member.name}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = f'Repetitions = {temp}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        value = f'Repetition Delay = {temp}'
    elif attribute == '5':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Calling Window №{i} = ' + ''.join(
                    f'start: {obj[0].value.strftime("%d.%m.%Y %H:%M:%S")}, end: {obj[1].value.strftime("%d.%m.%Y %H:%M:%S")} \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '6':
        value = f'Destinations = {reader.read(obj, int(attribute))}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_action_schedule(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        value = f'Executed Script Logical Name = logicalName: {temp[0]}, scriptSelector:{temp[1]}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        member = SingleActionScheduleType(temp)
        value = f'Type = {member.name}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Execution Time №{i} = ' + ''.join(f'{obj.value.strftime("%d.%m.%Y %H:%M:%S")} \n')) # Вместо звездочек вписывает дефолтные значения бибилиотечные пидр
        else:
            value = "НЕТ ЗАПИСЕЙ"
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_special_days_table(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Entries №{i} = ' + ''.join(
                    f'index: {obj.index}, day: {obj.date.value.strftime("%d.%m.%Y")}, dayId: {obj.dayId} \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_script_table(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'logicalName = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Script №{i} = ' + ''.join(f'id: {obj.id},'
                                                          f' actions: [target:{obj.actions[0].target},'
                                                          f' index:{obj.actions[0].index}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_activity_calendar(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'Active Calendar Name = {reader.read(obj, int(attribute))}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Active Season Profile №{i} = ' + ''.join(f'[name: {obj.name.decode()},'
                                                                        f' start: {obj.start.value.strftime("%d.%m.%Y %H:%M:%S")},'
                                                                        f' weekName: {obj.weekName.decode()}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Active Week Profile Table №{i} = ' + ''.join(f'[name: {obj.name.decode()},'
                         f' week:{obj.monday, obj.tuesday, obj.wednesday, obj.thursday, obj.friday, obj.saturday, obj.sunday}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '5':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Active Day Profile Table №{i} = ' + ''.join(f'[dayId: {obj.dayId},'
                         f' daySchedules:{[(i.startTime.value.strftime("%H:%M:%S"), i.scriptLogicalName, i.scriptSelector) for i in obj.daySchedules]}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
        # value = f'Active Day Profile Table = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'Passive Calendar Name = {reader.read(obj, int(attribute))}'
    elif attribute == '7':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Passive Season Profile №{i} = ' + ''.join(f'[name: {obj.name.decode()},'
                                                                        f' start: {obj.start.value.strftime("%d.%m.%Y %H:%M:%S")},'
                                                                        f' weekName: {obj.weekName.decode()}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '8':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Passive Week Profile Table №{i} = ' + ''.join(f'[name: {obj.name.decode()},'
                         f' week:{obj.monday, obj.tuesday, obj.wednesday, obj.thursday, obj.friday, obj.saturday, obj.sunday}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '9':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Passive Day Profile Table №{i} = ' + ''.join(f'[dayId: {obj.dayId},'
                         f' daySchedules:{[(i.startTime.value.strftime("%H:%M:%S"), i.scriptLogicalName, i.scriptSelector) for i in obj.daySchedules]}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '10':
         value = f'Time = {reader.read(obj, int(attribute)).value.strftime("%d.%m.%Y %H:%M:%S")}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_tcp_udp_setup(obj, reader, attribute):
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'Port = {reader.read(obj, int(attribute))}'
    elif attribute == '3':
        value = f'IP Reference = {reader.read(obj, int(attribute))}'
    elif attribute == '4':
        value = f'Maximum Segment Size = {reader.read(obj, int(attribute))}'
    elif attribute == '5':
        value = f'Maximum Simultaneous Connections = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'Inactivity Timeout = {reader.read(obj, int(attribute))}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_ip4_setup(obj, reader, attribute):
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'Data LinkLayer Reference = {reader.read(obj, int(attribute))}'
    elif attribute == '3':
        value = f'IP Address = {reader.read(obj, int(attribute))}'
    elif attribute == '4':
        value = f'Multicast IP Address = {reader.read(obj, int(attribute))}'
    elif attribute == '5':
        value = f'IP Options = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'Subnet Mask = {reader.read(obj, int(attribute))}'
    elif attribute == '7':
        value = f'Gateway IP Address = {reader.read(obj, int(attribute))}'
    elif attribute == '8':
        value = f'Use DHCP = {reader.read(obj, int(attribute))}'
    elif attribute == '9':
        value = f'Primary DNS Address = {reader.read(obj, int(attribute))}'
    elif attribute == '10':
        value = f'Secondary DNS Address = {reader.read(obj, int(attribute))}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_gsm_diagnostic(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        value = f'Operator = {reader.read(obj, int(attribute))}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        member = GsmStatus(temp)
        value = f'Status = {member.name}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        member = GsmCircuitSwitchStatus(temp)
        value = f'CircuitSwitchStatus = {member.name}'
    elif attribute == '5':
        temp = reader.read(obj, int(attribute))
        member = GsmPacketSwitchStatus(temp)
        value = f'PacketSwitchStatus = {member.name}'
    elif attribute == '6':
        obj.version = 0
        temp = reader.read(obj, 6)
        value = f'CellInfo = {temp.cellId, temp.ber, temp.locationId, temp.signalQuality, temp.mobileCountryCode, temp.mobileNetworkCode, temp.channelNumber}'
    elif attribute == '7':
        temp = reader.read(obj, int(attribute))
        if len(temp) != 0:
            for i, obj in enumerate(temp):
                value += str(f'Passive Day Profile Table №{i} = ' + ''.join(f'[cellId: {obj.cellId},'
                         f' signalQuality:{obj.signalQuality}] \n'))
        else:
            value = "НЕТ ЗАПИСЕЙ"
    elif attribute == '8':
        value = f'CaptureTime = {reader.read(obj, int(attribute)).value.strftime("%d.%m.%Y %H:%M:%S")}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_communication_port_protection(obj, reader, attribute):
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        member = ProtectionMode(temp)
        value = f'Protection mode = {member.name}'
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = f'Allowed failed attempts = {temp}'
    elif attribute == '4':
        temp = reader.read(obj, int(attribute))
        value = f'Initial lockout time = {temp}'
    elif attribute == '5':
        value = f'Steepness factor = {reader.read(obj, int(attribute))}'
    elif attribute == '6':
        value = f'Max lockout time  = {reader.read(obj, int(attribute))}'
    elif attribute == '7':
        temp = reader.read(obj, int(attribute))
        n_1 = str(temp[0])
        n_2 = str(temp[1])
        n_3 = str(temp[2])
        n_4 = str(temp[3])
        n_5 = str(temp[4])
        n_6 = str(temp[5])

        value = f'Port = {n_1 + '.' + n_2 + '.' + n_3 + '.' + n_4 + '.' + n_5 + '.' + n_6}'
    elif attribute == '8':
        temp = reader.read(obj, int(attribute))
        member = ProtectionStatus(temp)
        value = f'Protection status = {member.name}'
    elif attribute == '9':
        temp = reader.read(obj, int(attribute))
        value = f'Failed attempts = {temp}'
    elif attribute == '10':
        temp = reader.read(obj, int(attribute))
        value = f'Cumulative failed attempts = {temp}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_profile_generic(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        if reader.read(obj, 7) != 0:
            reader.read(obj, 3)
            temp = reader.read(obj, 2)
            value = 'Buffer = \n'
            for i, obj in enumerate(temp):
                value += str(f'Запись №{i + 1} = ' + ''.join(f'[Time: {obj[0].value.strftime("%d.%m.%Y %H:%M:%S")}....] \n'))
        else:
            value = 'НЕТ ЗАПИСЕЙ'
    elif attribute == '3':
        temp = reader.read(obj, 3)
        value = 'CaptureObjects = \n'
        for i, obj in enumerate(temp):
            value += str(''.join(f'{obj[0]} \n'))
    elif attribute == '4':
        value = f'Capture Period = {reader.read(obj, int(attribute))}'
    elif attribute == '5':
        temp = reader.read(obj, int(attribute))
        member = SortMethod(temp)
        value = f'Sort Method = {member.name}'
    elif attribute == '6':
        value = f'Sort Object = {reader.read(obj, int(attribute))}'
    elif attribute == '7':
        value = f'Entries In Use = {reader.read(obj, int(attribute))}'
    elif attribute == '8':
        value = f'Profile Entries = {reader.read(obj, int(attribute))}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value


def get_value_from_register_activation(obj, reader, attribute):
    value = ''
    if attribute == '1':
        value = f'Logical Name = {reader.read(obj, int(attribute))}'
    elif attribute == '2':
        temp = reader.read(obj, int(attribute))
        value = 'Register Assignment = \n'
        for i, obj in enumerate(temp):
            value += str(''.join(f'{obj.logicalName} \n'))
    elif attribute == '3':
        temp = reader.read(obj, int(attribute))
        value = 'Mask List = \n'
        for i, obj in enumerate(temp):
            value += str(''.join(f'{obj[0].decode()} \n'))
    elif attribute == '4':
        value = f'Active Mask = {reader.read(obj, int(attribute)).decode()}'
    else:
        raise Exception('Атрибут не удалось считать')
    return value
