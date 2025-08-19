from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import time

from libs.utils import get_obises


class WorkerThreadForReadCollection(QThread):
    finished = pyqtSignal()  # Сигнал завершения
    progress = pyqtSignal(int)  # Сигнал прогресса
    result = pyqtSignal(object)  # Сигнал для возврата результата

    def __init__(self):
        super().__init__()
        self.com = None

    def run(self):
        try:
            # Получаем результат выполнения функции
            result = get_obises(self.com)
            # Отправляем результат через сигнал
            self.result.emit(result)
        except Exception as e:
            print(f"Ошибка при выполнении: {e}")
        finally:
            self.finished.emit()
