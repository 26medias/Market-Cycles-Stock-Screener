from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt

def lerp(a, b, t):
    return a + (b - a) * t

def create_gradient_color(min_value, max_value, value, color1, color2):
    ratio = (value - min_value) / (max_value - min_value)
    return QColor(
        lerp(color1[0], color2[0], ratio),
        lerp(color1[1], color2[1], ratio),
        lerp(color1[2], color2[2], ratio),
    )

class CustomStandardItem(QStandardItem):
    def __init__(self, value=None, color_rule=None):
        super().__init__(str(value))
        
        self.value = value

        color = QColor(22, 26, 37)  # Default color

        if color_rule and isinstance(value, (int, float)):
            if value < 0:
                value = max(color_rule['min'], value)
                color = create_gradient_color(color_rule['min'], 0, value, (235, 51, 51), (38, 92, 153))
            elif value > 0:
                value = min(color_rule['max'], value)
                color = create_gradient_color(0, color_rule['max'], value, (38, 92, 153), (49, 206, 83))
            else:
                color = QColor(38, 92, 153)

        self.setBackground(color)
        self.setForeground(QColor(Qt.white))
    
    def __lt__(self, other):
        return self.value < other.value




class DataFrameModel(QStandardItemModel):
    def __init__(self, data=None):
        super(DataFrameModel, self).__init__()
        color_rules = {
            'DCO': {'min': 0, 'max': 100},
            'MarketCycle': {'min': 0, 'max': 100},
            'MarketCycle_prev': {'min': 0, 'max': 100},
            '1M-change': {'min': -50, 'max': 50},
            '1D-change': {'min': -50, 'max': 50},
            '5D-change': {'min': -50, 'max': 50},
            '20D-change': {'min': -50, 'max': 50},
        }
        self.color_rules = color_rules or {}
        self.load_data(data)

    def load_data(self, data):
        if data is not None:
            self.setHorizontalHeaderLabels(data.columns)
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    color_rule = self.color_rules.get(data.columns[j])
                    self.setItem(i, j, CustomStandardItem(data.iat[i, j], color_rule))

    def sort(self, column, order):
        self.sortRole = Qt.EditRole
        super().sort(column, order)
