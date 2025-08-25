from gurux_dlms import GXIntEnum


class ProtectionStatus(GXIntEnum):
    COM_PORT_STATUS_UNLOCKED = 0

    COM_PORT_STATUS_TEMPORARILY_LOCKED = 1

    COM_PORT_STATUS_LOCKED = 2
