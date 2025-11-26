from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QComboBox, QCheckBox, QPushButton, 
                             QDateEdit, QRadioButton, QButtonGroup)
from PyQt5.QtCore import QDate

class SortDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.sort_params = {}
        self.init_ui()
        self.load_filters()
    
    def init_ui(self):
        self.setWindowTitle("Расширенная сортировка и фильтрация")
        self.setGeometry(100, 100, 500, 600)
        
        layout = QVBoxLayout()
        
        # Сортировка
        sort_group = QGroupBox("Сортировка")
        sort_layout = QFormLayout(sort_group)
        
        self.sort_field_combo = QComboBox()
        self.sort_field_combo.addItems([
            "ID", "Категория", "ИИН/БИН", "Контрагент", "Телефон",
            "Номер договора", "Дата договора", "Статус договора",
            "Наличие договора", "Место услуг", "Участок", "Улица"
        ])
        sort_layout.addRow("Поле сортировки:", self.sort_field_combo)
        
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["По возрастанию (А-Я)", "По убыванию (Я-А)"])
        sort_layout.addRow("Порядок:", self.sort_order_combo)
        
        layout.addWidget(sort_group)
        
        # Фильтрация
        filter_group = QGroupBox("Фильтрация")
        filter_layout = QFormLayout(filter_group)
        
        # Категория
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории", None)
        filter_layout.addRow("Категория:", self.category_combo)
        
        # Место оказания услуг
        self.location_combo = QComboBox()
        self.location_combo.addItem("Все места", None)
        filter_layout.addRow("Место оказания услуг:", self.location_combo)
        
        # Участок
        self.section_combo = QComboBox()
        self.section_combo.addItem("Все участки", None)
        filter_layout.addRow("Участок:", self.section_combo)
        
        # Статус договора
        self.status_combo = QComboBox()
        self.status_combo.addItem("Все статусы", None)
        self.status_combo.addItems(["активный", "расторгнут", "приостановлен"])
        filter_layout.addRow("Статус договора:", self.status_combo)
        
        # Наличие договора
        self.availability_combo = QComboBox()
        self.availability_combo.addItem("Все", None)
        self.availability_combo.addItems(["Есть в наличии", "Нет в наличии"])
        filter_layout.addRow("Наличие договора:", self.availability_combo)
        
        # Период
        self.period_from = QDateEdit()
        self.period_from.setDate(QDate.currentDate().addMonths(-12))
        self.period_from.setCalendarPopup(True)
        filter_layout.addRow("Период с:", self.period_from)
        
        self.period_to = QDateEdit()
        self.period_to.setDate(QDate.currentDate())
        self.period_to.setCalendarPopup(True)
        filter_layout.addRow("по:", self.period_to)
        
        # Год
        self.year_combo = QComboBox()
        self.year_combo.addItem("Все годы", None)
        current_year = QDate.currentDate().year()
        for year in range(current_year - 5, current_year + 1):
            self.year_combo.addItem(str(year), year)
        filter_layout.addRow("Год:", self.year_combo)
        
        layout.addWidget(filter_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self.apply_filters)
        
        export_btn = QPushButton("Экспорт в Excel")
        export_btn.clicked.connect(self.export_with_volumes)
        
        reset_btn = QPushButton("Сбросить")
        reset_btn.clicked.connect(self.reset_filters)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_filters(self):
        """Загрузка данных для фильтров"""
        try:
            # Категории
            categories = self.db_manager.get_categories()
            for category in categories:
                self.category_combo.addItem(category['name'], category['id'])
            
            # Места оказания услуг
            locations = self.db_manager.get_service_locations()
            for location in locations:
                self.location_combo.addItem(location['name'], location['id'])
                
        except Exception as e:
            print(f"Ошибка загрузки фильтров: {e}")
    
    def apply_filters(self):
        """Применение фильтров"""
        self.sort_params = {
            'sort_field': self.sort_field_combo.currentText(),
            'sort_order': self.sort_order_combo.currentText(),
            'category': self.category_combo.currentData(),
            'location': self.location_combo.currentData(),
            'section': self.section_combo.currentData(),
            'status': self.status_combo.currentText() if self.status_combo.currentIndex() > 0 else None,
            'availability': self.availability_combo.currentText() if self.availability_combo.currentIndex() > 0 else None,
            'period_from': self.period_from.date().toString("yyyy-MM-dd"),
            'period_to': self.period_to.date().toString("yyyy-MM-dd"),
            'year': self.year_combo.currentData()
        }
        self.accept()
    
    def export_with_volumes(self):
        """Экспорт с объемами"""
        self.apply_filters()
        # Сигнал для главного окна на экспорт с объемами
        self.done(2)
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.category_combo.setCurrentIndex(0)
        self.location_combo.setCurrentIndex(0)
        self.section_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.availability_combo.setCurrentIndex(0)
        self.period_from.setDate(QDate.currentDate().addMonths(-12))
        self.period_to.setDate(QDate.currentDate())
        self.year_combo.setCurrentIndex(0)
    
    def get_sort_params(self):
        return self.sort_params