from PyQt5.QtWidgets import QTabWidget, QTableView
from PyQt5.QtCore import QTimer
from DataFrameModel import DataFrameModel

class TabManager(QTabWidget):
    def __init__(self, tabs_dict: dict, main_window):
        super(TabManager, self).__init__()
        self.tabs_dict = tabs_dict
        self.main_window = main_window
        self.create_tabs()
        self.currentChanged.connect(self.refresh_current_tab)

    def create_tabs(self):
        for tab_name, func in self.tabs_dict.items():
            self.addTab(self.create_tab_content(func), tab_name)

    def create_tab_content(self, func):
        view = QTableView()
        data_frame = func()
        model = DataFrameModel(data_frame)
        view.setModel(model)
        view.setSortingEnabled(True)

        # Resize columns and rows to fit contents after a delay
        QTimer.singleShot(0, lambda: self.resize_view(view))

        return view

    def refresh_content(self, func):
        index = self.currentIndex()
        view = self.widget(index)
        view.setModel(DataFrameModel(func()))

        # Resize columns and rows to fit contents after a delay
        QTimer.singleShot(0, lambda: self.resize_view(view))

    def resize_view(self, view):
        view.resizeColumnsToContents()
        view.resizeRowsToContents()

    def refresh_current_tab(self):
        self.main_window.refresh_current_tab()

