import sys

from PyQt5.QtWidgets import QApplication

from libs.FileUploader import FileUploader


def main():
    app = QApplication(sys.argv)
    ex = FileUploader()
    ex.show()
    sys.exit(app.exec_())




if __name__ == '__main__':
    main()
