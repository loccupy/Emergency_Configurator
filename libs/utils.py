from gurux_dlms.objects import GXDLMSAssociationLogicalName

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

        # temp = get_obises_from_meter(reader)
        object_list = reader.read(GXDLMSAssociationLogicalName('0.0.40.0.0.255'), 2)

        reader.close()

        print('Коллекция считана.')

        settings.media.close()

        return object_list
    except Exception as e:
        settings.media.close()
        print(e)
