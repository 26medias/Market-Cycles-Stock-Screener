import sys
import webbrowser
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTableView, QTableWidgetItem, QHeaderView, QPushButton, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel
import pandas as pd
from datetime import datetime
from Screener import Screener

class StockScreenerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Screener")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)  # Add tab widget to layout

        # Create QHBoxLayout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.export_button = QPushButton("Export")  # New Export button
        self.buttons_layout.addWidget(self.refresh_button)
        self.buttons_layout.addWidget(self.export_button)  # Add buttons to QHBoxLayout

        # Connect the buttons
        self.refresh_button.clicked.connect(self.refresh_data)
        self.export_button.clicked.connect(self.export_data)  # New export_data function

        # Add buttons layout to main layout
        self.layout.addLayout(self.buttons_layout)
        
        self.setLayout(self.layout)

        self.buys_df = pd.DataFrame()
        self.sells_df = pd.DataFrame()

    def export_data_old(self):
        current_tab_label = self.tab_widget.tabText(self.tab_widget.currentIndex())
        date_string = datetime.now().strftime("%Y-%m-%d")
        default_file_name = f"{current_tab_label} - {date_string}.txt"
        
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', default_file_name)
        if file_name:
            current_widget = self.tab_widget.currentWidget()
            df = current_widget.model().get_data()
            export_data = df[['Exchange', 'Symbol']].apply(lambda x: f"{x['Exchange'].upper()}:{x['Symbol'].upper()}", axis=1).to_list()
            with open(file_name, 'w') as f:
                f.write(','.join(export_data))

    def export_data(self):
        date_string = datetime.now().strftime("%Y-%m-%d")
        default_file_name = f"MarketCycles - {date_string}.txt"

        exportRules = {
            "Buy Signals In Trend": self.screener.buySignalsInTrend,
            "Sell Signals In Trend": self.screener.sellSignalsInTrend,
            "Buy Signals Counter Trend": self.screener.buySignalsCounterTrend,
            "Sell Signals Counter Trend": self.screener.sellSignalsCounterTrend,
            "Buy Signals": self.screener.buySignals,
            "Sell Signals": self.screener.sellSignals,
        }
        exportData = []
        for k in exportRules:
            exportData.extend(["### "+k])
            exportData.extend(self.getExportData(exportRules[k]))
        
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', default_file_name)
        if file_name:
            with open(file_name, 'w') as f:
                f.write(','.join(exportData))
    
    def getExportData(self, df):
        return df[['Exchange', 'Symbol']].apply(lambda x: f"{x['Exchange'].upper()}:{x['Symbol'].upper()}", axis=1).to_list()
    
    def refresh_data(self):
        self.screener = Screener()
        self.screener.screen()
        buySignals = self.screener.buySignals
        sellSignals = self.screener.sellSignals
        buySignalsInTrend = self.screener.buySignalsInTrend
        sellSignalsInTrend = self.screener.sellSignalsInTrend
        buySignalsCounterTrend = self.screener.buySignalsCounterTrend
        sellSignalsCounterTrend = self.screener.sellSignalsCounterTrend

        self.tab_widget.clear()

        buySignals_table = self.create_table(buySignals)
        sellSignals_table = self.create_table(sellSignals)
        buySignalsInTrend_table = self.create_table(buySignalsInTrend)
        sellSignalsInTrend_table = self.create_table(sellSignalsInTrend)
        buySignalsCounterTrend_table = self.create_table(buySignalsCounterTrend)
        sellSignalsCounterTrend_table = self.create_table(sellSignalsCounterTrend)

        self.tab_widget.addTab(buySignals_table, "Buy Signals")
        self.tab_widget.addTab(sellSignals_table, "Sell Signals")
        self.tab_widget.addTab(buySignalsInTrend_table, "Buy Signals In Trend")
        self.tab_widget.addTab(sellSignalsInTrend_table, "Sell Signals In Trend")
        self.tab_widget.addTab(buySignalsCounterTrend_table, "Buy Signals Counter Trend")
        self.tab_widget.addTab(sellSignalsCounterTrend_table, "Sell Signals Counter Trend")

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
    
    def get_data(self):
        return self._data

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
