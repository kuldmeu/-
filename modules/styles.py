from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class AppStyles:
    @staticmethod
    def get_dark_theme():
        """Темная тема оформления"""
        palette = QPalette()
        
        # Настройка цветов палитры
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        return palette
    
    @staticmethod
    def get_light_theme():
        """Светлая тема оформления"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(233, 231, 227))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        return palette
    
    @staticmethod
    def get_blue_theme():
        """Синяя тема оформления"""
        palette = QPalette()
        
        palette.setColor(QPalette.Window, QColor(240, 245, 255))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(233, 240, 255))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(200, 220, 255))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 100, 200))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        return palette
    
    @staticmethod
    def get_stylesheet(theme_name):
        """Получение CSS стилей для выбранной темы"""
        if theme_name == "dark":
            return """
                QMainWindow {
                    background-color: #353535;
                    color: white;
                }
                QWidget {
                    background-color: #353535;
                    color: white;
                }
                QTableView {
                    background-color: #252525;
                    color: white;
                    gridline-color: #555555;
                    alternate-background-color: #353535;
                    selection-background-color: #2a82da;
                }
                QTableView::item:selected {
                    background-color: #2a82da;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #454545;
                    color: white;
                    padding: 4px;
                    border: 1px solid #555555;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #454545;
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px 10px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QPushButton:pressed {
                    background-color: #2a82da;
                }
                QPushButton:disabled {
                    background-color: #333333;
                    color: #777777;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                    background-color: #252525;
                    color: white;
                    border: 1px solid #555555;
                    padding: 2px 5px;
                    border-radius: 2px;
                }
                QTextEdit {
                    background-color: #252525;
                    color: white;
                    border: 1px solid #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #353535;
                }
                QTabBar::tab {
                    background-color: #454545;
                    color: white;
                    padding: 8px 12px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #2a82da;
                    color: white;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #555555;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QMenuBar {
                    background-color: #454545;
                    color: white;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #2a82da;
                }
                QMenu {
                    background-color: #454545;
                    color: white;
                    border: 1px solid #555555;
                }
                QMenu::item {
                    padding: 4px 20px;
                }
                QMenu::item:selected {
                    background-color: #2a82da;
                }
                QToolBar {
                    background-color: #454545;
                    border: none;
                    spacing: 3px;
                }
                QStatusBar {
                    background-color: #454545;
                    color: white;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 3px;
                    text-align: center;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: #2a82da;
                }
                QScrollBar:vertical {
                    background-color: #454545;
                    width: 15px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #666666;
                    border-radius: 7px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #888888;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
            """
        elif theme_name == "blue":
            return """
                QMainWindow {
                    background-color: #f0f5ff;
                }
                QTableView {
                    alternate-background-color: #f8f8f8;
                    selection-background-color: #c8dcff;
                }
                QHeaderView::section {
                    background-color: #c8dcff;
                    padding: 4px;
                    border: 1px solid #a0c0ff;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #c8dcff;
                    border: 1px solid #a0c0ff;
                    padding: 5px 10px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #d8e8ff;
                }
                QPushButton:pressed {
                    background-color: #a0c0ff;
                }
                QTabBar::tab {
                    background-color: #e0e8ff;
                    padding: 8px 12px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #a0c0ff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #a0c0ff;
                    border-radius: 4px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #f8fbff;
                }
                QMenuBar {
                    background-color: #e0e8ff;
                }
                QMenu {
                    background-color: #e0e8ff;
                    border: 1px solid #a0c0ff;
                }
                QToolBar {
                    background-color: #e0e8ff;
                    border: none;
                }
                QStatusBar {
                    background-color: #e0e8ff;
                }
            """
        else:  # light theme
            return """
                QTableView {
                    alternate-background-color: #f8f8f8;
                    selection-background-color: #e0e0e0;
                }
                QHeaderView::section {
                    background-color: #e0e0e0;
                    padding: 4px;
                    border: 1px solid #c0c0c0;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #c0c0c0;
                    padding: 5px 10px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
                QTabBar::tab {
                    background-color: #e8e8e8;
                    padding: 8px 12px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 2px solid #0078d7;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #c0c0c0;
                    border-radius: 4px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #f8f8f8;
                }
            """