from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd

class Worker(QThread):
    dataReady = pyqtSignal(pd.DataFrame)

    def __init__(self, func, options=None):
        super().__init__()
        self.func = func
        self.options = options

    def run(self):
        if self.options is None:
            data = self.func()
        else:
            data = self.func(*self.options)
        if data is not None:
            self.dataReady.emit(data)

