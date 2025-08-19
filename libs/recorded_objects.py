from gurux_dlms.enums import DataType


def set_value_for_data(obj, settings, reader, value, attribute):
    try:
        if reader.readType(obj, int(attribute)) != DataType.STRING:
            value = int(value)
        settings.client.updateValue(obj, int(attribute), value)
        reader.write(obj, int(attribute))
        return True
    except Exception as e:
        print("Ошибка при записи параметра класса Data >>", e)
        return False
