from PyQt5.QtWidgets import QSlider, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox
from PyQt5.QtCore import Qt


class CustomSlider(QSlider):
    def __init__(self, minimum, maximum):
        super().__init__(Qt.Horizontal)
        self.setMinimum(minimum)
        self.setMaximum(maximum)


class CustomComboBox(QComboBox):
    def __init__(self, items):
        super().__init__()
        self.addItems(items)


class CustomLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()


class CustomSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()


class CustomDoubleSpinBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
