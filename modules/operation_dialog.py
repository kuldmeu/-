from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
                             QDateEdit, QPushButton, QMessageBox, QGroupBox)
from PyQt5.QtCore import QDate

class AddOperationDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Добавить операцию (начисление)")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        
        # Вид услуги
        service_group = QGroupBox("Вид услуги")
        service_layout = QFormLayout(service_group)
        
        self.service_type_combo = QComboBox()
        self.service_type_combo.addItems(["Водоснабжение", "Водоотведение"])
        self.service_type_combo.currentIndexChanged.connect(self.on_service_changed)
        service_layout.addRow("Вид услуги:", self.service_type_combo)
        
        self.subservice_combo = QComboBox()
        service_layout.addRow("Тип услуги:", self.subservice_combo)
        
        self.on_service_changed(0)  # Инициализация
        
        # Параметры операции
        params_group = QGroupBox("Параметры операции")
        params_layout = QFormLayout(params_group)
        
        self.old_value_edit = QDoubleSpinBox()
        self.old_value_edit.setMaximum(999999)
        params_layout.addRow("Предыдущее показание:", self.old_value_edit)
        
        self.new_value_edit = QDoubleSpinBox()
        self.new_value_edit.setMaximum(999999)
        params_layout.addRow("Текущее показание:", self.new_value_edit)
        
        self.consumption_label = QLabel("0.0")
        params_layout.addRow("Расход:", self.consumption_label)
        
        self.volume_edit = QDoubleSpinBox()
        self.volume_edit.setMaximum(999999)
        params_layout.addRow("Объем:", self.volume_edit)
        
        self.trips_edit = QSpinBox()
        self.trips_edit.setMaximum(999)
        params_layout.addRow("Рейс:", self.trips_edit)
        
        self.operation_date = QDateEdit()
        self.operation_date.setDate(QDate.currentDate())
        self.operation_date.setCalendarPopup(True)
        params_layout.addRow("Дата операции:", self.operation_date)
        
        # Автоматический расчет расхода
        self.new_value_edit.valueChanged.connect(self.calculate_consumption)
        self.old_value_edit.valueChanged.connect(self.calculate_consumption)
        
        layout.addWidget(service_group)
        layout.addWidget(params_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить операцию")
        save_btn.clicked.connect(self.save_operation)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_service_changed(self, index):
        """Обновление типов услуг при изменении вида услуги"""
        self.subservice_combo.clear()
        
        if index == 0:  # Водоснабжение
            self.subservice_combo.addItems(["Водопровод", "Автотранспорт", "Автотранспорт организации"])
        else:  # Водоотведение
            self.subservice_combo.addItems(["Канализация", "Ассенизатор", "Ассенизатор организации"])
    
    def calculate_consumption(self):
        """Расчет расхода"""
        consumption = self.new_value_edit.value() - self.old_value_edit.value()
        self.consumption_label.setText(f"{consumption:.2f}")
    
    def save_operation(self):
        """Сохранение операции"""
        try:
            # Проверка данных
            if self.new_value_edit.value() <= self.old_value_edit.value():
                QMessageBox.warning(self, "Ошибка", "Текущее показание должно быть больше предыдущего")
                return
            
            # Сохранение в базу данных
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                INSERT INTO operations 
                (counterparty_id, service_type, operation_type, old_value, new_value, 
                 consumption, volume, trips, operation_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.counterparty_id,
                self.service_type_combo.currentText(),
                self.subservice_combo.currentText(),
                self.old_value_edit.value(),
                self.new_value_edit.value(),
                self.new_value_edit.value() - self.old_value_edit.value(),
                self.volume_edit.value(),
                self.trips_edit.value(),
                self.operation_date.date().toString("yyyy-MM-dd"),
                self.user_data['id']
            ))
            
            self.db_manager.conn.commit()
            QMessageBox.information(self, "Успех", "Операция успешно сохранена")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения операции: {e}")