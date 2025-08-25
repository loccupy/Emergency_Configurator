from gurux_dlms.objects import GXDLMSAssociationLogicalName, GXDLMSData, GXDLMSRegister, GXDLMSDemandRegister, \
    GXDLMSRegisterActivation, GXDLMSProfileGeneric, GXDLMSClock, GXDLMSScriptTable, GXDLMSSpecialDaysTable, \
    GXDLMSImageTransfer, GXDLMSActivityCalendar, GXDLMSActionSchedule, GXDLMSHdlcSetup, GXDLMSModemConfiguration, \
    GXDLMSAutoConnect, GXDLMSPushSetup, GXDLMSTcpUdpSetup, GXDLMSIp4Setup, GXDLMSGprsSetup, GXDLMSGSMDiagnostic, \
    GXDLMSSecuritySetup, GXDLMSDisconnectControl, GXDLMSLimiter

# from libs.GXDLMSCommunicationPortProtection import GXDLMSCommunicationPortProtection
from libs.connect import connect


# def get_obises_from_meter(reader):
#     # GXDLMSAssociationLogicalName('0.0.40.0.0.255')
#     object_list = reader.read(GXDLMSAssociationLogicalName('0.0.40.0.0.255'), 2)
#     return object_list

def get_obises(com):
    reader, settings = connect(com)
    try:
        print('Считываю коллекцию.. Ждите.')
        settings.media.open()
        reader.initializeConnection()

        object_list = reader.read(GXDLMSAssociationLogicalName('0.0.40.0.0.255'), 2)  # Не считывает CommPortProtection!!!
        reader.close()

        print('Коллекция считана.')

        settings.media.close()

        return object_list
    except Exception as e:
        settings.media.close()
        print(e)


def parse_data_type(obis, data_type):
    match int(data_type):
        case 1:
            return GXDLMSData(obis)
        case 3:
            return GXDLMSRegister(obis)
        case 5:
            return GXDLMSDemandRegister(obis)
        case 6:
            return GXDLMSRegisterActivation(obis)
        case 7:
            return GXDLMSProfileGeneric(obis)
        case 8:
            return GXDLMSClock(obis)
        case 9:
            return GXDLMSScriptTable(obis)
        case 11:
            return GXDLMSSpecialDaysTable(obis)
        case 15:
            return GXDLMSAssociationLogicalName(obis)
        case 18:
            return GXDLMSImageTransfer(obis)
        case 20:
            return GXDLMSActivityCalendar(obis)
        case 22:
            return GXDLMSActionSchedule(obis)
        case 23:
            return GXDLMSHdlcSetup(obis)
        case 27:
            return GXDLMSModemConfiguration(obis)
        case 29:
            return GXDLMSAutoConnect(obis)
        case 40:
            return GXDLMSPushSetup(obis)
        case 41:
            return GXDLMSTcpUdpSetup(obis)
        case 42:
            return GXDLMSIp4Setup(obis)
        case 45:
            return GXDLMSGprsSetup(obis)
        case 47:
            return GXDLMSGSMDiagnostic(obis)
        case 64:
            return GXDLMSSecuritySetup(obis)
        case 70:
            return GXDLMSDisconnectControl(obis)
        case 71:
            return GXDLMSLimiter(obis)
        case 124:
            return GXDLMSLimiter(obis)
        case _:
            raise Exception(f'Класс с типом {data_type} не идентифицирован!!')




