from gurux_dlms import GXIntEnum


class ProtectionMode(GXIntEnum):
    COM_PORT_MODE_LOCKED = 0

    COM_PORT_MODE_LOCKED_ON_FAILED_ATTEMPTS = 1

    COM_PORT_MODE_UNLOCKED = 2
