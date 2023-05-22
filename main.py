import sys
import webbrowser
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTableView, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel
import pandas as pd
from Screener import Screener

class StockScreenerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Screener")

        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)

        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.tab_widget)  # Add tab widget to layout
        self.setLayout(self.layout)

        self.buys_df = pd.DataFrame()
        self.sells_df = pd.DataFrame()

    def refresh_data(self):
        screener = Screener()
        screener.screen()
        sells = screener.summary(screener.sellList)
        buys = screener.summary(screener.buyList)
        sellSignals = screener.summary(screener.sellSignals)
        buySignals = screener.summary(screener.buySignals)

        self.tab_widget.clear()

        buys_table = self.create_table(buys)
        sells_table = self.create_table(sells)
        buySignals_table = self.create_table(buySignals)
        sellSignals_table = self.create_table(sellSignals)

        self.tab_widget.addTab(buys_table, "Oversold Watchlist")
        self.tab_widget.addTab(sells_table, "Overbought Watchlist")
        self.tab_widget.addTab(buySignals_table, "Buy Signals")
        self.tab_widget.addTab(sellSignals_table, "Sell Signals")

    def create_table(self, df):
        table = QTableView()
        table.setEditTriggers(QTableView.NoEditTriggers)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus)

        model = PandasModel(df)
        table.setModel(model)

        return table

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(PandasModel, self).__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[section])
        return None

    def sort(self, column, order):
        if order == Qt.AscendingOrder:
            self._data = self._data.sort_values(self._data.columns[column], ascending=True)
        else:
            self._data = self._data.sort_values(self._data.columns[column], ascending=False)
        self.layoutChanged.emit()

def open_tradingview(exchange, symbol):
    url = f"https://www.tradingview.com/symbols/{exchange}-{symbol}/"
    webbrowser.open(url)

def show_ui():
    app = QApplication(sys.argv)
    window = StockScreenerUI()
    window.refresh_data()
    window.show()
    sys.exit(app.exec_())

show_ui()
