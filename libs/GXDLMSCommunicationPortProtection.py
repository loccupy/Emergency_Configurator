from gurux_dlms.enums import ErrorCode, ObjectType, DataType
from gurux_dlms.internal._GXCommon import _GXCommon
from gurux_dlms.objects.GXDLMSObject import GXDLMSObject
from gurux_dlms.objects.IGXDLMSBase import IGXDLMSBase
from libs import ProtectionMode, ProtectionStatus


class GXDLMSCommunicationPortProtection(GXDLMSObject, IGXDLMSBase):

    def __init__(self, ln='0.0.44.2.0.255', sn=0):
        GXDLMSObject.__init__(self, ObjectType.COMMUNICATION_PORT_PROTECTION, ln, sn)
        self.protectionMode = ProtectionMode.ProtectionMode.COM_PORT_MODE_UNLOCKED
        self.allowedFailedAttempts = 3
        self.initialLockoutTime = 30
        self.steepnessFactor = 1
        self.maxLockoutTime = 43200
        self.port = None
        self.protectionStatus = ProtectionStatus.ProtectionStatus.COM_PORT_STATUS_UNLOCKED
        self.failedAttempts = 0
        self.cumulativeFailedAttempts = 0

    def getValues(self):
        return [self.logicalName,
                self.protectionMode,
                self.allowedFailedAttempts,
                self.initialLockoutTime,
                self.steepnessFactor,
                self.maxLockoutTime,
                self.port,
                self.protectionStatus,
                self.failedAttempts,
                self.cumulativeFailedAttempts]

    def getAttributeIndexToRead(self, all_):
        attributes = list()
        if all_ or not self.logicalName:
            attributes.append(1)
        if all_ or not self.isRead(2):
            attributes.append(2)
        if all_ or not self.isRead(3):
            attributes.append(3)
        if all_ or not self.isRead(4):
            attributes.append(4)
        if all_ or not self.isRead(5):
            attributes.append(5)
        if all_ or not self.isRead(6):
            attributes.append(6)
        if all_ or not self.isRead(7):
            attributes.append(7)
        if all_ or not self.isRead(8):
            attributes.append(8)
        if all_ or not self.isRead(9):
            attributes.append(9)
        if all_ or not self.isRead(10):
            attributes.append(10)
        return attributes

    def getAttributeCount(self):
        return 10

    def getMethodCount(self):
        return 1

    def getDataType(self, index):
        if index == 1:
            ret = DataType.OCTET_STRING
        elif index == 2:
            ret = DataType.ENUM
        elif index == 3:
            ret = DataType.UINT16
        elif index == 4:
            ret = DataType.UINT32
        elif index == 5:
            ret = DataType.UINT8
        elif index == 6:
            ret = DataType.UINT32
        elif index == 7:
            ret = DataType.OCTET_STRING
        elif index == 8:
            ret = DataType.ENUM
        elif index == 9:
            ret = DataType.UINT32
        elif index == 10:
            ret = DataType.UINT32
        else:
            raise ValueError("getDataType failed. Invalid attribute index.")
        return ret

    def getValue(self, settings, e):
        if e.index == 1:
            ret = _GXCommon.logicalNameToBytes(self.logicalName)
        elif e.index == 2:
            ret = self.protectionMode
        elif e.index == 3:
            ret = self.allowedFailedAttempts
        elif e.index == 4:
            ret = self.initialLockoutTime
        elif e.index == 5:
            ret = self.steepnessFactor
        elif e.index == 6:
            ret = self.maxLockoutTime
        elif e.index == 7:
            ret = self.port
        elif e.index == 8:
            ret = self.protectionStatus
        elif e.index == 9:
            ret = self.failedAttempts
        elif e.index == 10:
            ret = self.cumulativeFailedAttempts
        else:
            e.error = ErrorCode.READ_WRITE_DENIED
        return ret

    def setValue(self, settings, e):
        if e.index == 1:
            self.logicalName = _GXCommon.toLogicalName(e.value)
        elif e.index == 2:
            self.protectionMode = e.value
        elif e.index == 3:
            self.allowedFailedAttempts = e.value
        elif e.index == 4:
            self.initialLockoutTime = e.value
        elif e.index == 5:
            self.steepnessFactor = e.value
        elif e.index == 6:
            self.maxLockoutTime = e.value
        elif e.index == 7:
            self.port = e.value
        elif e.index == 8:
            self.protectionStatus = e.value
        elif e.index == 9:
            self.failedAttempts = e.value
        elif e.index == 10:
            self.cumulativeFailedAttempts = e.value
        else:
            e.error = ErrorCode.READ_WRITE_DENIED

    def load(self, reader):
        self.protectionMode = reader.readElementContentAsInt("protectionMode")
        self.allowedFailedAttempts = reader.readElementContentAsInt("allowedFailedAttempts")
        self.initialLockoutTime = reader.readElementContentAsInt("initialLockoutTime")
        self.steepnessFactor = reader.readElementContentAsInt("steepnessFactor")
        self.maxLockoutTime = reader.readElementContentAsInt("maxLockoutTime")
        self.port = reader.readElementContentAsInt("port")
        self.protectionStatus = reader.readElementContentAsInt("protectionStatus")
        self.failedAttempts = reader.readElementContentAsInt("failedAttempts")
        self.cumulativeFailedAttempts = reader.readElementContentAsInt("cumulativeFailedAttempts")

    def save(self, writer):
        writer.writeElementString("protectionMode", int(self.protectionMode))
        writer.writeElementString("allowedFailedAttempts", self.allowedFailedAttempts)
        writer.writeElementString("initialLockoutTime", self.initialLockoutTime)
        writer.writeElementString("steepnessFactor", self.steepnessFactor)
        writer.writeElementString("port", self.port)
        writer.writeElementString("protectionStatus", self.protectionStatus)
        writer.writeElementString("failedAttempts", self.failedAttempts)
        writer.writeElementString("cumulativeFailedAttempts", self.cumulativeFailedAttempts)

    def reset(self, client):
        return client.method(self, 1, 0, DataType.INT8)
