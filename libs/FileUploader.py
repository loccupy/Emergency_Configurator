import os
import sys
import pandas as pd

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal, QSortFilterProxyModel, Qt, QStringListModel
from PyQt5.QtGui import QIntValidator, QTextCursor, QStandardItemModel
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QTextEdit, QMessageBox, QApplication, QComboBox, \
    QVBoxLayout, QDialogButtonBox, QDialog, QSizePolicy, QCompleter
from gurux_dlms import GXUInt32, GXUInt16, GXReplyData
from gurux_dlms.enums import DataType, ObjectType
from gurux_dlms.objects import GXDLMSData, GXDLMSObject

from libs.WorkerThread import WorkerThreadForReadCollection
from libs.configur import server, login, password, folder
from libs.connect import connect
from libs.reader_objects import read_obj
from libs.recorded_objects import set_value
from libs.utils import parse_data_type


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass  # Необходимо для совместимости с sys.stdout


class InputDialog(QDialog):
    value_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Введите новое значение')

        layout = QVBoxLayout()

        self.input_field = QTextEdit()
        # self.input_field.setWhatsThis("Введите новое значение в поле. Формат соответствует значению при считывании.")
        self.input_field.setLineWrapMode(QTextEdit.WidgetWidth)
        self.input_field.setReadOnly(False)
        # Настраиваем политику размера
        self.input_field.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        layout.addWidget(self.input_field, stretch=2)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_value(self):
        """Показать диалог и вернуть введённое значение"""
        if self.exec_() == QDialog.Accepted:
            self.value = self.input_field.toPlainText().strip()
            return self.value
        else:
            return None

    def accept(self):
        value = self.input_field.toPlainText()
        self.value_submitted.emit(value)
        super().accept()


class FileUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.method_categories = None
        self.attribute_categories = None
        self.add_attr = None
        self.delete_all = None
        self.delete_last = None
        self.attributes_for_recording = None
        self.method = None
        self.original_obis_list = None
        self.attribute = QComboBox()
        self.objects_list = None
        self.completer_model = QStringListModel()
        self.proxy_model = QSortFilterProxyModel()
        self.initUI()

    def initUI(self):
        current_dir = os.path.dirname(__file__)
        ui_path = os.path.join(current_dir, 'maket.ui')

        uic.loadUi(ui_path, self)

        self.attributes_for_recording = []
        self.add_attr = self.findChild(QPushButton, 'add_attribute')
        self.add_attr.clicked.connect(self.show_input_dialog)

        self.delete_last = self.findChild(QPushButton, 'delete_last')
        self.delete_last.clicked.connect(self.clear_last_attributes)

        self.delete_all = self.findChild(QPushButton, 'delete_all')
        self.delete_all.clicked.connect(self.clear_attributes)

        self.text_edit_2 = self.findChild(QTextEdit, 'textEdit_2')
        self.text_edit_2.setReadOnly(True)  # Запрещаем редактирование
        self.text_edit_2.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit_2.setPlaceholderText("Параметры на изменение")

        self.attribute_categories = {}
        self.method_categories = {}

        self.number_com = self.findChild(QLineEdit, 'enter_com')
        self.number_com.setValidator(QIntValidator())

        self.obises = self.findChild(QComboBox, 'obis')
        # Подключаем сигнал изменения выбора
        self.obises.currentIndexChanged.connect(self.update_files)
        self.obises.currentIndexChanged.connect(self.update_files_attr)
        self.get_all_objects_from_excel()

        self.search = self.findChild(QLineEdit, 'search')

        self.attribute = self.findChild(QComboBox, 'attr')
        self.method = self.findChild(QComboBox, 'method')

        self.read_attr = self.findChild(QPushButton, 'read')
        self.read_attr.clicked.connect(self.read_param)

        self.value = None

        self.write_att = self.findChild(QPushButton, 'write')
        self.write_att.clicked.connect(self.write_param)

        self.execute_meth = self.findChild(QPushButton, 'execute')
        self.execute_meth.clicked.connect(self.execute_method)

        self.text_edit = self.findChild(QTextEdit, 'textEdit')
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit.setReadOnly(True)  # Запрещаем редактирование
        self.redirect_stdout()
        self.stream.textWritten.connect(self.on_text_written)

        self.applyDarkTheme()

        self.update_attributes_display()

        # Устанавливаем модель для QComboBox, чтобы можно было фильтровать
        # self.completer_model = QStringListModel()
        # self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.completer_model)

        self.obises.setModel(self.proxy_model)
        # Устанавливаем completer для поиска
        self.completer = QCompleter()
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setModel(self.proxy_model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.obises.setCompleter(self.completer)

        # Подключаем поле поиска к фильтрации
        self.search.textChanged.connect(self.filter_obis_list)

    def filter_obis_list(self):
        """Фильтрация списка OBIS по введённому тексту в поле search"""
        filter_text = self.search.text().strip()
        all_items = self.original_obis_list  # Должен храниться при загрузке
        filtered_items = [item for item in all_items if filter_text.lower() in item.lower()]
        self.completer_model.setStringList(filtered_items)

    def update_attributes_display(self):
        """Обновляет отображение атрибутов в textEdit_2"""
        text = self.attributes_for_recording
        if self.attributes_for_recording:
            text = "\n".join([f'Ожидается запись значения "{attr[1]}" в атрибут №{attr[2]} объекта {attr[0]}..' for attr in text])
            self.text_edit_2.setPlainText(text)
        else:
            self.text_edit_2.setPlainText('')

    def clear_attributes(self):
        self.attributes_for_recording.clear()
        self.update_attributes_display()

    def clear_last_attributes(self):
        if self.text_edit_2.toPlainText():
            self.attributes_for_recording.pop(-1)
            self.update_attributes_display()
        else:
            print("Список параметров для записи уже пуст..")

    def show_input_dialog(self):
        if not self.number_com.text().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Введите COM соединения!",
                QMessageBox.Ok
            )
            return
        dialog = InputDialog(self)
        dialog.value_submitted.connect(self.add_attributes)
        dialog.exec_()

    def update_text(self, message, color):
        self.text_edit.append(f"<font color={color} size='4'>{message}</font>")
        self.text_edit.append(f"<font color='white' size='4'></font>")

    def redirect_stdout(self):
        self.stream = EmittingStream()
        sys.stdout = self.stream
        sys.stderr = self.stream

    def on_text_written(self, text):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
        QApplication.processEvents()

    def applyDarkTheme(self):
        # Определяем стили для темной темы
        dark_stylesheet = """
        QWidget {
            background-color: #2c313c;
            color: #ffffff;
        }

        QLineEdit {
            background-color: #363d47;
            color: #ffffff;
            border: 1px solid #444950;
            border-radius: 4px;
            padding: 5px;
        }

        QLineEdit:focus {
            border: 1px solid #61dafb;
        }

        QPushButton {
            background-color: #363d47;
            color: #ffffff;
            border: 1px solid #444950;
            border-radius: 4px;
            padding: 5px 10px;
        }

        QPushButton:hover {
            background-color: #444950;
        }

        QPushButton:pressed {
            background-color: #2c313c;
        }
        """

        # Применяем стиль к приложению
        self.setStyleSheet(dark_stylesheet)

    def get_all_objects_from_excel(self):
        try:
            current_dir = os.path.dirname(__file__)
            file_path = os.path.join(current_dir, 'All_OBIS.xlsx')
            df = pd.read_excel(file_path)

            temp_description = {}
            for index, row in df.iterrows():
                temp_description[row['OBIS']] = row['Класс'], row['Описание']

            self.objects_list = temp_description

            self.attribute_categories = {}
            self.method_categories = {}
            arr_obis = []
            for key, value in self.objects_list.items():
                obis = key
                object_type = value[0]
                description = value[1]
                obj = parse_data_type(obis, object_type)
                if object_type == ObjectType.ASSOCIATION_LOGICAL_NAME:
                    obj.version = -1 # Модернизирую Association чтобы избежать list_out_of_range (obj.getNames только 8 когда атрибутов 11)getMethodNames
                list_attr = [f'{y} {obj.getNames()[y - 1]}' for y in range(1, obj.getAttributeCount() + 1)]
                self.attribute_categories[obis] = list_attr

                list_method = [f'{y} {obj.getMethodNames()[y - 1]}' for y in range(1, obj.getMethodCount() + 1)]
                self.method_categories[obis] = list_method

                arr_obis.append(obis + ' ' + description)

            self.original_obis_list = arr_obis
            self.completer_model.setStringList(self.original_obis_list)
            self.proxy_model.setSourceModel(self.completer_model)

            self.obises.addItems(arr_obis)
        except Exception as e:
            print('Ошибка при получении списка атрибутов и методов с помощью excel файла >>', e)

    def update_files(self):
        if self.obises:
            try:
                # Получаем выбранную категорию
                selected_category = self.obises.currentText().split()[0]

                # Очищаем второй комбобокс
                self.attribute.clear()

                # Заполняем второй комбобокс соответствующими файлами
                if selected_category in self.attribute_categories:
                    self.attribute.addItems(self.attribute_categories[selected_category])
            except Exception as e:
                print('Ошибка в update_files после получения списков из excel файла >>', e)

    def update_files_attr(self):
        if self.obises:
            try:
                # Получаем выбранную категорию
                selected_category = self.obises.currentText().split()[0]

                # Очищаем комбобокс
                self.method.clear()

                # Заполняем второй комбобокс соответствующими файлами
                if selected_category in self.method_categories:
                    self.method.addItems(self.method_categories[selected_category])
            except Exception as e:
                print('Ошибка в update_files после получения списков из excel файла >>', e)

    def read_param(self):
        if not self.obises.currentText().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Отсутствует значение в поле OBIS!",
                QMessageBox.Ok
            )
            return
        obis = self.obises.currentText().split()[0]
        attribute = self.attribute.currentText().split()[0]
        atr_description = self.attribute.currentText().split(" ", 1)[1]
        temp_object = None

        for key, value in self.objects_list.items():
            if key == obis:
                temp_object = parse_data_type(key, value[0])
                break

        if not self.number_com.text().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Введите COM соединения!",
                QMessageBox.Ok
            )
            return

        com = self.number_com.text()
        reader, settings = connect(com)
        try:
            settings.media.open()
            reader.initializeConnection()
            print("Соединение установлено")

            value = read_obj(temp_object, reader, attribute) # если значение невозможно преобразовать в строку, возвращает ошибку - надо доработать

            print(f'Для атрибута #{attribute} {atr_description}# объекта {temp_object.logicalName} считано значение >> \n{value}')

            reader.close()
            print("Соединение разорвано\n")
        except Exception as e:
            settings.media.close()
            self.update_text(f"Ошибка при считывании >> {e}.", "red")
            print("Соединение разорвано\n")

    def add_attributes(self, value):
        attribute = None
        atr_description = None
        obis = None
        temp_object = None
        try:
            attribute = self.attribute.currentText()[0]
            atr_description = self.attribute.currentText()[1:]
            obis = self.obises.currentText().split()[0]
            for key, val in self.objects_list.items():
                if key == obis:
                    temp_object = parse_data_type(key, val[0])
                    break
            self.attributes_for_recording.append([temp_object, value, attribute, atr_description])
            self.update_attributes_display()
            print(f'Для атрибута #{attribute} {atr_description}# объекта {obis} добавлено значение >> ', value)
        except Exception as e:
            print(f"Ошибка при добавлении атрибута #{attribute} {atr_description}# объекта {obis} на запись в очередь", e)
            raise

    def write_param(self):
        if not self.number_com.text().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Введите COM соединения!",
                QMessageBox.Ok
            )
            return

        if not self.attributes_for_recording:
            print("НЕТ ДАННЫХ ДЛЯ ЗАПИСИ!!!")
            return
        com = self.number_com.text()
        reader, settings = connect(com)
        try:
            settings.media.open()
            reader.initializeConnection()
            print("Соединение установлено")
            if self.attributes_for_recording:
                for i in self.attributes_for_recording:
                    if not set_value(i[0], reader, i[1], i[2]):
                        continue

                    print(f'Для атрибута #{i[2]} {i[3]}# объекта {i[0].logicalName} установлено значение >>\n',
                          read_obj(i[0], reader, i[2]))
            else:
                print("НЕТ ДАННЫХ ДЛЯ ЗАПИСИ!!!")
            reader.close()
            print("Соединение разорвано\n")
        except Exception as e:
            settings.media.close()
            self.update_text(f"Ошибка при записи >> {e}.", "red")
            print("Соединение разорвано\n")


    def execute_method(self):
        if not self.obises.currentText().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Отсутствует значение в поле OBIS!",
                QMessageBox.Ok
            )
            return
        obis = self.obises.currentText().split()[0]
        if not self.method.currentText().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Отсутствует методы для выполнения!",
                QMessageBox.Ok
            )
            return
        method_number = self.method.currentText().split()[0]
        method_description = self.method.currentText().split(" ", 1)[1]
        temp_object = None

        for key, value in self.objects_list.items():
            if key == obis:
                temp_object = parse_data_type(key, value[0])
                break

        if not self.number_com.text().strip():
            # Показываем предупреждение
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Введите COM соединения!",
                QMessageBox.Ok
            )
            return

        com = self.number_com.text()
        reader, settings = connect(com)
        try:
            settings.media.open()
            reader.initializeConnection()
            print("Соединение установлено")

            if temp_object.getObjectType() == ObjectType.CLOCK:
                if method_number == '6':
                    dialog = InputDialog(self)
                    value = dialog.get_value()
                    reply = GXReplyData()
                    reader.readDataBlock(temp_object.shiftTime(reader.client, int(value)), reply)
                elif method_number == '3':
                    reply = GXReplyData()
                    reader.readDataBlock(temp_object.adjustToMinute(reader.client), reply)
                else:
                    raise Exception ('Метод с уровнем NO ACCESS')
            elif temp_object.getObjectType() == ObjectType.PROFILE_GENERIC:
                if method_number == '1':
                    reply = GXReplyData()
                    reader.readDataBlock(temp_object.reset(reader.client), reply)
                elif method_number == '2':
                    reply = GXReplyData()
                    reader.readDataBlock(temp_object.capture(reader.client), reply)
            elif temp_object.getObjectType() == ObjectType.ACTIVITY_CALENDAR:
                reply = GXReplyData()
                reader.readDataBlock(temp_object.activatePassiveCalendar(reader.client), reply)
            elif temp_object.getObjectType() == ObjectType.DISCONNECT_CONTROL:
                if method_number == '1':
                    reply = GXReplyData()
                    reader.readDataBlock(temp_object.remoteDisconnect(reader.client), reply)
                elif method_number == '2':
                    reply = GXReplyData()
                    reader.readDataBlock(temp_object.remoteReconnect(reader.client), reply)
            elif temp_object.getObjectType() == ObjectType.COMMUNICATION_PORT_PROTECTION:
                reply = GXReplyData()
                try:
                    reader.readDataBlock(temp_object.reset(reader.client), reply) # включил в блок, потому что возвращает ошибку - мб связано с совместимостью библиотек
                except:
                    pass
            else:
                raise Exception("Выполнение методов в данном объекте пока не обрабатываются!!!")

            print(
                f'Метод #{method_number} {method_description}# объекта {temp_object.logicalName} выполнен')

            reader.close()
            print("Соединение разорвано\n")
        except Exception as e:
            settings.media.close()
            self.update_text(f"Ошибка при выполнении метода >> {e}.", "red")
            print("Соединение разорвано\n")
