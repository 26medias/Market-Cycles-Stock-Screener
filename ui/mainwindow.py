from PyQt5.QtWidgets import QSpinBox, QAction, QMenu, QToolButton, QStackedLayout, QFileDialog, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QStatusBar, QProgressBar
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon

import time
import json
from datetime import datetime
from tabmanager import TabManager
from custom_widgets import CustomComboBox, CustomSpinBox, CustomDoubleSpinBox
from screener.Screener import Screener
from Worker import Worker
from DataFrameModel import DataFrameModel

class MainWindow(QMainWindow):
    def __init__(self, QApplication):
        super().__init__()
        self.total_tasks = 0
        self.current_task = 0
        self.current_worker = None
        self.loading_queue = []
        self.data_cache = None
        self.statusBars = {}

        self.QApplication = QApplication
        self.setWindowTitle('Stock Screener')
        self.resize(1200, 800)
        self.screener = Screener()

        self.tabs = {
            'Buys': self.screener.get_buySignals,
            'Sells': self.screener.get_sellSignals,
            'Buys (trend)': self.screener.get_buySignalsInTrend,
            'Sells (trend)': self.screener.get_sellSignalsInTrend,
            'Buys (counter)': self.screener.get_buySignalsCounterTrend,
            'Sells (counter)': self.screener.get_sellSignalsCounterTrend
        }

        # Initialize options dict with default values
        self.options = {"timeframe": "Daily", "overbought": 80, "oversold": 20, 
                        "donchian_period": 14, "rsi_period": 14, "srsi_period": 20, 
                        "donchian_weight": 0.5, "rsi_weight": 1, "srsi_weight": 1}

        
        self.setup_ui()

        # Create a Worker to run the refresh_data() function
        #self.refresh_worker = Worker(self.refresh_data)
        #self.refresh_worker.dataReady.connect(self.nope)
        # Start the Worker after the UI has been rendered
        #self.refresh_worker.start()

    # Setup the UI
    def setup_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()


        self.setup_ui_loading()
        self.options_layout = self.setup_ui_options()
        self.buttons_layout = self.setup_ui_buttons()
        self.tab_manager = TabManager(self.tabs, self)

        layout.addLayout(self.options_layout)
        layout.addLayout(self.buttons_layout)

        stacked_layout = QStackedLayout()
        stacked_layout.addWidget(self.tab_manager)
        stacked_layout.addWidget(self.loading_widget)

        layout.addLayout(stacked_layout)

        self.statusBar().addWidget(self.createStatusBar("status"), 1)
        self.statusBar().addWidget(self.createStatusBar("signalDate"), 1)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def createStatusBar(self, name):
        status_label = QLabel('...')  # Initialize the QLabel
        status_label.setAlignment(Qt.AlignCenter)  # Center the QLabel
        status_label.setFont(QFont("Arial", 10))  # Make the QLabel small
        status_label.font().setItalic(True)  # Set the font to italic
        self.statusBars[name] = status_label
        return status_label

    def setStatus(self, name, status: str):
        self.statusBars[name].setText(status)
        self.QApplication.processEvents()
    

    def nope(self):
        pass

    # Progress Loader
    def load_all(self, functions, onComplete=None):
        self.loadAllOnComplete = onComplete
        self.total_tasks = len(functions)  # Save the total number of tasks
        self.current_task = 0  # Start with the first task
        for func, params, label in functions:
            worker = Worker(func, params)
            worker.finished.connect(self.on_worker_finished)
            worker.dataReady.connect(self.on_worker_data_ready)
            self.loading_queue.append((worker, label))

        # If there are any tasks in the loading queue, start the first one
        if self.loading_queue:
            self.start_next_worker()

    def start_next_worker(self):
        if self.loading_queue:
            self.current_worker, label = self.loading_queue.pop(0)
            self.set_loading_status(True)
            self.set_loading_settings(self.current_task, self.total_tasks, label)
            self.current_worker.start()
        else:
            self.current_worker = None  # Clear the current worker when the queue is empty
            self.set_loading_status(False)
            if self.loadAllOnComplete is not None:
                self.loadAllOnComplete()

    def on_worker_finished(self):
        self.current_task += 1  # Increment the current task
        self.set_loading_settings(self.current_task, self.total_tasks, "Task completed.")
        self.start_next_worker()

    def on_worker_data_ready(self, data):
        # Put your logic here to handle the returned data
        pass

    def setup_ui_loading(self):
        self.loading_label = QLabel()  # Initialize the loading label
        self.loading_progress = QProgressBar()  # Initialize the progress bar

        # Initialize and setup the loading layout
        self.loading_layout = QVBoxLayout()
        self.loading_layout.addWidget(self.loading_progress)
        self.loading_layout.addWidget(self.loading_label)
        self.loading_layout.setAlignment(Qt.AlignCenter)  # Center the loading layout

        # Initialize and setup the loading widget
        self.loading_widget = QWidget()
        self.loading_widget.setLayout(self.loading_layout)
        self.loading_widget.hide()  # Hide the loading screen by default
    
    def set_loading_status(self, status):
        if status:
            self.tab_manager.hide()  # Hide the tabs
            self.loading_widget.show()  # Show the loading screen
        else:
            self.loading_widget.hide()  # Hide the loading screen
            self.tab_manager.show()  # Show the tabs

    def set_loading_settings(self, current, total, label):
        progress = int((current / total) * 100)
        self.loading_progress.setValue(progress)  # Set the progress bar value
        self.loading_label.setText(f"{current}/{total} - {label}")  # Set the label text
        if progress >= 100:  # If the progress is 100 or more
            self.set_loading_status(False)  # Hide the loading screen


    def setup_ui_buttons(self):
        buttons_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")

        # Export Settings button with icon
        export_settings_button = QPushButton()
        export_settings_button.setIcon(QIcon("res/export.png"))
        export_settings_button.setIconSize(QSize(16, 16))
        export_settings_button.setFixedWidth(32)

        # Import Settings button with icon
        import_settings_button = QPushButton()
        import_settings_button.setIcon(QIcon("res/import.png"))
        import_settings_button.setIconSize(QSize(16, 16))
        import_settings_button.setFixedWidth(32)

        menuSelector = self.createDropdownMenu("Options", [
            ("res/export.png", "Export Settings", self.export_settings),
            ("res/import.png", "Import Settings", self.import_settings),
            ("res/export.png", "Export Watchlists", self.exportWatchlists),
            ("res/export.png", "Import Historical Data", self.loadHistoricalData),
            ("res/export.png", "Use latest Data", self.loadLatestData),
        ])

        # Add widgets to the layout
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(import_settings_button)
        buttons_layout.addWidget(export_settings_button)
        buttons_layout.addWidget(menuSelector)

        # Click handlers
        refresh_button.clicked.connect(self.refresh_data)

        import_settings_button.clicked.connect(self.import_settings)
        export_settings_button.clicked.connect(self.export_settings)

        return buttons_layout

    def refresh_current_tab(self):
        self.setStatus("status", "Refreshing the data...")
        tab_name = self.tab_manager.tabText(self.tab_manager.currentIndex())
        func = self.tab_manager.tabs_dict.get(tab_name)
        if func is not None:
            self.worker = Worker(func, [self.get_options()])
            self.worker.dataReady.connect(self.update_current_tab)
            self.worker.start()

    def update_current_tab(self, data):
        self.tab_manager.widget(self.tab_manager.currentIndex()).setModel(DataFrameModel(data))
        self.setStatus("status", "Tab data updated.")
    
    def createDropdownMenu(self, title, options):
        # Create the QToolButton
        tool_button = QToolButton()
        tool_button.setPopupMode(QToolButton.InstantPopup)  # Set the popup mode
        tool_button.setText(title)  # Set the button text

        # Create the QMenu
        menu = QMenu()

        for icon, text, func in options:
            # Create the QAction
            action = QAction(QIcon(icon), text, self)
            action.triggered.connect(func)
            menu.addAction(action)  # Add the action to the menu

        # Set the button's menu
        tool_button.setMenu(menu)
        
        return tool_button
    
    # get the symbols export data
    def getWatchlistData(self, df):
        try:
            return df[['Exchange', 'Symbol']].apply(lambda x: f"{x['Exchange'].upper()}:{x['Symbol'].upper()}", axis=1).to_list()
        except:
            return []

    def exportWatchlists(self):
        settings = self.get_options()
        timeframe = settings["timeframe"]
        default_file_name = f"{timeframe}-{self.screener.date}.txt"

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
            exportData.extend(self.getWatchlistData(exportRules[k]))
        
        self.save_as(filename=default_file_name, data=','.join(exportData))

    def loadHistoricalData(self):
        filename = self.open_file(default_ext=".pkl")
        if filename is not None:
            self.data_cache = filename
            self.refresh_data()

    def loadLatestData(self):
        self.data_cache = None
        self.refresh_data()


    # Refresh the data
    def refresh_data(self):
        settings = self.get_options()
        
        self.setStatus("status", "Refreshing...")
        self.setStatus("signalDate", "Please wait...")

        fnList = [
            (self.screener.pullData, [self.data_cache], "Downloading the new data..."),
        ]
        if settings["timeframe"] == "Daily":
            fnList.append((self.screener.build_daily, [settings], "Building the daily data..."))
        elif settings["timeframe"] == "Monthly":
            fnList.append((self.screener.build_monthly, [settings], "Building the monthly data..."))
        
        fnList.append((self.screener.filter, [settings], "Filtering the daily data..."))
        fnList.append((self.refresh_current_tab, None, "Refreshing the tab..."))
        
        self.load_all(fnList, lambda: self.setStatus("signalDate", self.screener.date))

    # Export the settings
    def export_settings(self):
        self.save_as("settings.screener", json.dumps(self.get_options(), indent=4))
        self.setStatus("status", "Settings exported.")

    # Import the settings
    def import_settings(self):
        filename = self.open_file(default_ext="screener")
        print("filename", filename)
        try:
            settings = self.read_json_file(filename)
            print("settings", settings)
            self.set_options(settings)
            self.setStatus("status", "New settings imported.")
        except:
            self.setStatus("status", "Settings import failed.")

    # Read a JSON file
    def read_json_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"Failed to read file: {e}")
            return None

    #
    # UI

    # Save As
    def save_as(self, filename="output.txt", data="", default_dir=None):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if default_dir is not None:
            filepath, _ = QFileDialog.getSaveFileName(self, "Save as", default_dir + filename, "Text Files (*.txt)", options=options)
        else:
            filepath, _ = QFileDialog.getSaveFileName(self, "Save as", filename, "Text Files (*.txt)", options=options)

        if filepath:  # If a file path is given (i.e., the dialog wasn't cancelled)
            try:
                with open(filepath, 'w') as f:
                    f.write(data)
                return True
            except Exception as e:
                print(f"Failed to save file: {e}")
                return False
        else:
            return False
    
    # Open As
    def open_file(self, filename=None, default_ext=".txt", default_dir=None):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        if default_dir is not None:
            filepath, _ = QFileDialog.getOpenFileName(self, "Open", default_dir + filename, "Text Files (*" + default_ext + ")", options=options)
        else:
            filepath, _ = QFileDialog.getOpenFileName(self, "Open", filename, "Text Files (*" + default_ext + ")", options=options)
        
        if filepath:  # If a file path is given (i.e., the dialog wasn't cancelled)
            return filepath
        else:
            return None
        
    # Returns the option values as a dict
    def get_options(self):
        return {"timeframe": self.timeframe.currentText(), "curr": self.curr.value(), "overbought": self.overbought.value(), 
                "oversold": self.oversold.value(), "donchian_period": self.donchian_period.value(), 
                "rsi_period": self.rsi_period.value(), "srsi_period": self.srsi_period.value(), 
                "donchian_weight": self.donchian_weight.value(), "rsi_weight": self.rsi_weight.value(), 
                "srsi_weight": self.srsi_weight.value()}

    # Set the option values
    def set_options(self, values):
        self.timeframe.setCurrentText(values.get("timeframe", self.options.get("timeframe")))
        self.curr.setValue(values.get("curr", self.options.get("curr")))
        self.overbought.setValue(values.get("overbought", self.options.get("overbought")))
        self.oversold.setValue(values.get("oversold", self.options.get("oversold")))
        self.donchian_period.setValue(values.get("donchian_period", self.options.get("donchian_period")))
        self.rsi_period.setValue(values.get("rsi_period", self.options.get("rsi_period")))
        self.srsi_period.setValue(values.get("srsi_period", self.options.get("srsi_period")))
        self.donchian_weight.setValue(values.get("donchian_weight", self.options.get("donchian_weight")))
        self.rsi_weight.setValue(values.get("rsi_weight", self.options.get("rsi_weight")))
        self.srsi_weight.setValue(values.get("srsi_weight", self.options.get("srsi_weight")))

    # Build the options UI
    def setup_ui_options(self):
        options_layout = QHBoxLayout()
        
        timeframe_layout = QVBoxLayout()
        timeframe_layout.addWidget(QLabel("Timeframe"))
        self.timeframe = CustomComboBox(["Daily", "Monthly"])  # Use self.timeframe instead of timeframe
        timeframe_layout.addWidget(self.timeframe)

        curr_layout = QVBoxLayout()
        curr_layout.addWidget(QLabel("Index"))
        self.curr = QSpinBox()
        self.curr.setRange(-10000, -1)
        self.curr.setValue(-1)
        curr_layout.addWidget(self.curr)

        overbought_layout = QVBoxLayout()
        overbought_layout.addWidget(QLabel("Overbought"))
        self.overbought = CustomSpinBox()  # Use self.overbought instead of overbought
        self.overbought.setValue(80)
        overbought_layout.addWidget(self.overbought)

        oversold_layout = QVBoxLayout()
        oversold_layout.addWidget(QLabel("Oversold"))
        self.oversold = CustomSpinBox()  # Use self.oversold instead of oversold
        self.oversold.setValue(20)
        oversold_layout.addWidget(self.oversold)

        donchian_period_layout = QVBoxLayout()
        donchian_period_layout.addWidget(QLabel("Donchian Period"))
        self.donchian_period = CustomSpinBox()  # Use self.donchian_period instead of donchian_period
        self.donchian_period.setValue(14)
        donchian_period_layout.addWidget(self.donchian_period)

        rsi_period_layout = QVBoxLayout()
        rsi_period_layout.addWidget(QLabel("Rsi Period"))
        self.rsi_period = CustomSpinBox()  # Use self.rsi_period instead of rsi_period
        self.rsi_period.setValue(14)
        rsi_period_layout.addWidget(self.rsi_period)

        srsi_period_layout = QVBoxLayout()
        srsi_period_layout.addWidget(QLabel("sRsi Period"))
        self.srsi_period = CustomSpinBox()  # Use self.srsi_period instead of srsi_period
        self.srsi_period.setValue(20)
        srsi_period_layout.addWidget(self.srsi_period)

        donchian_weight_layout = QVBoxLayout()
        donchian_weight_layout.addWidget(QLabel("Donchian Weight"))
        self.donchian_weight = CustomDoubleSpinBox()  # Use self.donchian_weight instead of donchian_weight
        self.donchian_weight.setValue(0.5)
        donchian_weight_layout.addWidget(self.donchian_weight)

        rsi_weight_layout = QVBoxLayout()
        rsi_weight_layout.addWidget(QLabel("Rsi Weight"))
        self.rsi_weight = CustomDoubleSpinBox()  # Use self.rsi_weight instead of rsi_weight
        self.rsi_weight.setValue(1)
        rsi_weight_layout.addWidget(self.rsi_weight)

        srsi_weight_layout = QVBoxLayout()
        srsi_weight_layout.addWidget(QLabel("sRsi Weight"))
        self.srsi_weight = CustomDoubleSpinBox()  # Use self.srsi_weight instead of srsi_weight
        self.srsi_weight.setValue(1)
        srsi_weight_layout.addWidget(self.srsi_weight)

        options_layout.addLayout(timeframe_layout)
        options_layout.addLayout(curr_layout)
        options_layout.addLayout(overbought_layout)
        options_layout.addLayout(oversold_layout)
        options_layout.addLayout(donchian_period_layout)
        options_layout.addLayout(rsi_period_layout)
        options_layout.addLayout(srsi_period_layout)
        options_layout.addLayout(donchian_weight_layout)
        options_layout.addLayout(rsi_weight_layout)
        options_layout.addLayout(srsi_weight_layout)
        return options_layout

        
