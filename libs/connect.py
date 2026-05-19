from libs.GXDLMSReader import GXDLMSReader
from libs.GXSettings import GXSettings


def connecting(com, password):
    settings = GXSettings()
    settings.getParameters("COM", f'COM{com}', password=password, authentication="High", serverAddress=127,
                           logicalAddress=1, clientAddress=48, baudRate=9600)
    reader = GXDLMSReader(settings.client, settings.media, settings.trace, settings.invocationCounter)
    return reader, settings
