from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.main_window = MainWindow(QApplication)
        self.main_window.show()
