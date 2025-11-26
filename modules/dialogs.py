import os
from datetime import datetime, date
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
                             QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QGroupBox, QGridLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QRadioButton, QButtonGroup, QScrollArea, QFormLayout,
                             QListWidget, QListWidgetItem, QSplitter, QFrame,
                             QProgressBar, QFileDialog, QInputDialog, QToolButton,
                             QSizePolicy, QStyledItemDelegate, QApplication,
                             QDialogButtonBox)
from PyQt5.QtCore import QDate, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter
import json


class AddCounterpartyDialog(QDialog):
    def __init__(self, db_manager, user_id, parent=None, counterparty_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.counterparty_data = counterparty_data
        self.counterparty_id = counterparty_data['id'] if counterparty_data else None
        self.is_edit_mode = counterparty_data is not None

        self.setWindowTitle("Редактировать контрагента" if self.is_edit_mode else "Добавить контрагента")
        self.setGeometry(100, 100, 1000, 700)

        self.init_ui()
        self.load_reference_data()

        if self.is_edit_mode:
            self.load_counterparty_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Создание вкладок
        self.tabs = QTabWidget()

        # Вкладка "Контрагент"
        self.counterparty_tab = QWidget()
        self.init_counterparty_tab()
        self.tabs.addTab(self.counterparty_tab, "Контрагент")

        # Вкладка "Плановый объем услуг"
        self.plan_tab = QWidget()
        self.init_plan_tab()
        self.tabs.addTab(self.plan_tab, "Плановый объем услуг")

        layout.addWidget(self.tabs)

        # Кнопки сохранения/отмены
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_counterparty)
        self.save_btn.setDefault(True)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def init_counterparty_tab(self):
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Часть 1: Основная информация
        basic_info_group = QGroupBox("Основная информация")
        basic_layout = QGridLayout(basic_info_group)

        # Поля ввода
        row = 0

        # ID
        basic_layout.addWidget(QLabel("ID:"), row, 0)
        self.id_edit = QLineEdit()
        if not self.is_edit_mode:
            # Генерация ID для нового контрагента
            count = len(self.db_manager.get_counterparties())
            self.id_edit.setText(f"CTR{count + 1:06d}")
        self.id_edit.setReadOnly(True)
        basic_layout.addWidget(self.id_edit, row, 1)

        basic_layout.addWidget(QLabel("Категория:"), row, 2)
        self.category_combo = QComboBox()
        basic_layout.addWidget(self.category_combo, row, 3)
        row += 1

        # Место оказания услуг
        basic_layout.addWidget(QLabel("Место оказания услуг:"), row, 0)
        self.service_location_combo = QComboBox()
        self.service_location_combo.currentIndexChanged.connect(self.on_service_location_changed)
        basic_layout.addWidget(self.service_location_combo, row, 1)

        basic_layout.addWidget(QLabel("Участок:"), row, 2)
        self.section_combo = QComboBox()
        self.section_combo.currentIndexChanged.connect(self.on_section_changed)
        basic_layout.addWidget(self.section_combo, row, 3)
        row += 1

        # Улица, дом, квартира
        basic_layout.addWidget(QLabel("Улица:"), row, 0)
        self.street_combo = QComboBox()
        basic_layout.addWidget(self.street_combo, row, 1)

        basic_layout.addWidget(QLabel("Дом:"), row, 2)
        self.house_edit = QLineEdit()
        basic_layout.addWidget(self.house_edit, row, 3)
        row += 1

        basic_layout.addWidget(QLabel("Квартира:"), row, 0)
        self.apartment_edit = QLineEdit()
        basic_layout.addWidget(self.apartment_edit, row, 1)

        basic_layout.addWidget(QLabel("Статус договора:"), row, 2)
        self.contract_status_combo = QComboBox()
        self.contract_status_combo.addItems(["активный", "расторгнут", "приостановлен"])
        basic_layout.addWidget(self.contract_status_combo, row, 3)
        row += 1

        # Наличие договора
        basic_layout.addWidget(QLabel("Наличие договора:"), row, 0)
        self.contract_availability_combo = QComboBox()
        self.contract_availability_combo.addItems(["Есть в наличии", "Нет в наличии"])
        basic_layout.addWidget(self.contract_availability_combo, row, 1)

        basic_layout.addWidget(QLabel("Номер договора:"), row, 2)
        self.contract_number_edit = QLineEdit()
        basic_layout.addWidget(self.contract_number_edit, row, 3)
        row += 1

        # Дата договора
        basic_layout.addWidget(QLabel("Дата договора:"), row, 0)
        self.contract_date_edit = QDateEdit()
        self.contract_date_edit.setDate(QDate.currentDate())
        self.contract_date_edit.setCalendarPopup(True)
        basic_layout.addWidget(self.contract_date_edit, row, 1)

        basic_layout.addWidget(QLabel("ИИН/БИН:"), row, 2)
        self.iin_bin_edit = QLineEdit()
        basic_layout.addWidget(self.iin_bin_edit, row, 3)
        row += 1

        # Название контрагента
        basic_layout.addWidget(QLabel("Контрагент:"), row, 0)
        self.name_edit = QLineEdit()
        basic_layout.addWidget(self.name_edit, row, 1, 1, 3)
        row += 1

        # Телефон
        basic_layout.addWidget(QLabel("Телефон:"), row, 0)
        self.phone_edit = QLineEdit()
        basic_layout.addWidget(self.phone_edit, row, 1)

        basic_info_group.setLayout(basic_layout)
        content_layout.addWidget(basic_info_group)

        # Часть 2: Виды услуг и тарифы
        services_group = QGroupBox("Виды услуг и тарифы")
        services_layout = QGridLayout(services_group)

        # Водоснабжение
        water_supply_group = QGroupBox("Водоснабжение")
        water_layout = QGridLayout(water_supply_group)

        water_layout.addWidget(QLabel("Водопровод:"), 0, 0)
        self.water_tariff_edit = QDoubleSpinBox()
        self.water_tariff_edit.setMaximum(10000)
        self.water_tariff_edit.setSuffix(" ₸/м³")
        water_layout.addWidget(self.water_tariff_edit, 0, 1)

        water_layout.addWidget(QLabel("Автотранспорт:"), 1, 0)
        self.auto_water_tariff_edit = QDoubleSpinBox()
        self.auto_water_tariff_edit.setMaximum(10000)
        self.auto_water_tariff_edit.setSuffix(" ₸/м³")
        water_layout.addWidget(self.auto_water_tariff_edit, 1, 1)

        water_layout.addWidget(QLabel("Автотранспорт организации:"), 2, 0)
        self.org_auto_water_tariff_edit = QDoubleSpinBox()
        self.org_auto_water_tariff_edit.setMaximum(10000)
        self.org_auto_water_tariff_edit.setSuffix(" ₸/м³")
        water_layout.addWidget(self.org_auto_water_tariff_edit, 2, 1)

        water_supply_group.setLayout(water_layout)
        services_layout.addWidget(water_supply_group, 0, 0)

        # Водоотведение
        water_disposal_group = QGroupBox("Водоотведение")
        disposal_layout = QGridLayout(water_disposal_group)

        disposal_layout.addWidget(QLabel("Канализация:"), 0, 0)
        self.sewer_tariff_edit = QDoubleSpinBox()
        self.sewer_tariff_edit.setMaximum(10000)
        self.sewer_tariff_edit.setSuffix(" ₸/м³")
        disposal_layout.addWidget(self.sewer_tariff_edit, 0, 1)

        disposal_layout.addWidget(QLabel("Ассенизатор:"), 1, 0)
        self.ass_tariff_edit = QDoubleSpinBox()
        self.ass_tariff_edit.setMaximum(10000)
        self.ass_tariff_edit.setSuffix(" ₸/м³")
        disposal_layout.addWidget(self.ass_tariff_edit, 1, 1)

        disposal_layout.addWidget(QLabel("Ассенизатор организации:"), 2, 0)
        self.org_ass_tariff_edit = QDoubleSpinBox()
        self.org_ass_tariff_edit.setMaximum(10000)
        self.org_ass_tariff_edit.setSuffix(" ₸/м³")
        disposal_layout.addWidget(self.org_ass_tariff_edit, 2, 1)

        water_disposal_group.setLayout(disposal_layout)
        services_layout.addWidget(water_disposal_group, 0, 1)

        services_group.setLayout(services_layout)
        content_layout.addWidget(services_group)

        # Часть 3: Примечание
        notes_group = QGroupBox("Примечание")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_edit)

        content_layout.addWidget(notes_group)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        self.counterparty_tab.setLayout(layout)

    def init_plan_tab(self):
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Выбор года
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Год:"))
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 1, current_year + 3):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_year))
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        content_layout.addLayout(year_layout)

        # Вкладки для водоснабжения и водоотведения
        plan_tabs = QTabWidget()

        # Вкладка водоснабжения
        water_supply_plan = QWidget()
        self.init_water_supply_plan(water_supply_plan)
        plan_tabs.addTab(water_supply_plan, "Водоснабжение")

        # Вкладка водоотведения
        water_disposal_plan = QWidget()
        self.init_water_disposal_plan(water_disposal_plan)
        plan_tabs.addTab(water_disposal_plan, "Водоотведение")

        content_layout.addWidget(plan_tabs)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        self.plan_tab.setLayout(layout)

    def init_water_supply_plan(self, widget):
        layout = QGridLayout(widget)

        # Заголовки кварталов
        quarters = ["1 квартал", "2 квартал", "3 квартал", "4 квартал"]
        for i, quarter in enumerate(quarters):
            label = QLabel(quarter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold; background-color: #e0e0e0; padding: 5px;")
            layout.addWidget(label, 0, i * 3, 1, 3)

        # Месяцы по кварталам
        months_quarters = [
            ["Январь", "Февраль", "Март"],  # 1 квартал
            ["Апрель", "Май", "Июнь"],  # 2 квартал
            ["Июль", "Август", "Сентябрь"],  # 3 квартал
            ["Октябрь", "Ноябрь", "Декабрь"]  # 4 квартал
        ]

        self.water_plan_fields = {}

        for quarter_idx, months in enumerate(months_quarters):
            for month_idx, month in enumerate(months):
                row = month_idx * 4 + 1
                col = quarter_idx * 3

                # Название месяца
                month_label = QLabel(month)
                layout.addWidget(month_label, row, col)

                # Поля для водопровода
                water_label = QLabel("Водопровод:")
                water_edit = QDoubleSpinBox()
                water_edit.setMaximum(999999)
                water_edit.setSuffix(" м³")
                layout.addWidget(water_label, row + 1, col)
                layout.addWidget(water_edit, row + 1, col + 1)

                # Поля для автотранспорта
                auto_label = QLabel("Автотранспорт:")
                auto_edit = QDoubleSpinBox()
                auto_edit.setMaximum(999999)
                auto_edit.setSuffix(" м³")
                layout.addWidget(auto_label, row + 2, col)
                layout.addWidget(auto_edit, row + 2, col + 1)

                # Поля для автотранспорта организации
                org_label = QLabel("Автотранспорт орг:")
                org_edit = QDoubleSpinBox()
                org_edit.setMaximum(999999)
                org_edit.setSuffix(" м³")
                layout.addWidget(org_label, row + 3, col)
                layout.addWidget(org_edit, row + 3, col + 1)

                self.water_plan_fields[month] = {
                    'water': water_edit,
                    'auto': auto_edit,
                    'org': org_edit
                }

    def init_water_disposal_plan(self, widget):
        layout = QGridLayout(widget)

        # Аналогично водоснабжению, но для водоотведения
        quarters = ["1 квартал", "2 квартал", "3 квартал", "4 квартал"]
        for i, quarter in enumerate(quarters):
            label = QLabel(quarter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold; background-color: #e0e0e0; padding: 5px;")
            layout.addWidget(label, 0, i * 3, 1, 3)

        months_quarters = [
            ["Январь", "Февраль", "Март"],
            ["Апрель", "Май", "Июнь"],
            ["Июль", "Август", "Сентябрь"],
            ["Октябрь", "Ноябрь", "Декабрь"]
        ]

        self.disposal_plan_fields = {}

        for quarter_idx, months in enumerate(months_quarters):
            for month_idx, month in enumerate(months):
                row = month_idx * 4 + 1
                col = quarter_idx * 3

                month_label = QLabel(month)
                layout.addWidget(month_label, row, col)

                # Поля для канализации
                sewer_label = QLabel("Канализация:")
                sewer_edit = QDoubleSpinBox()
                sewer_edit.setMaximum(999999)
                sewer_edit.setSuffix(" м³")
                layout.addWidget(sewer_label, row + 1, col)
                layout.addWidget(sewer_edit, row + 1, col + 1)

                # Поля для ассенизатора
                ass_label = QLabel("Ассенизатор:")
                ass_edit = QDoubleSpinBox()
                ass_edit.setMaximum(999999)
                ass_edit.setSuffix(" м³")
                layout.addWidget(ass_label, row + 2, col)
                layout.addWidget(ass_edit, row + 2, col + 1)

                # Поля для ассенизатора организации
                org_ass_label = QLabel("Ассенизатор орг:")
                org_ass_edit = QDoubleSpinBox()
                org_ass_edit.setMaximum(999999)
                org_ass_edit.setSuffix(" м³")
                layout.addWidget(org_ass_label, row + 3, col)
                layout.addWidget(org_ass_edit, row + 3, col + 1)

                self.disposal_plan_fields[month] = {
                    'sewer': sewer_edit,
                    'ass': ass_edit,
                    'org_ass': org_ass_edit
                }

    def load_reference_data(self):
        """Загрузка справочных данных"""
        try:
            # Загрузка категорий
            categories = self.db_manager.get_categories()
            self.category_combo.clear()
            self.category_combo.addItem("Выберите категорию", None)
            for category in categories:
                self.category_combo.addItem(category['name'], category['id'])

            # Загрузка мест оказания услуг
            locations = self.db_manager.get_service_locations()
            self.service_location_combo.clear()
            self.service_location_combo.addItem("Выберите место услуг", None)
            for location in locations:
                self.service_location_combo.addItem(location['name'], location['id'])

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")

    def on_service_location_changed(self):
        """Обновление списка участков при изменении места оказания услуг"""
        location_id = self.service_location_combo.currentData()
        if not location_id:
            return

        try:
            sections = self.db_manager.get_sections(location_id)
            self.section_combo.clear()
            self.section_combo.addItem("Выберите участок", None)
            for section in sections:
                self.section_combo.addItem(section['name'], section['id'])
        except Exception as e:
            print(f"Ошибка загрузки участков: {e}")

    def on_section_changed(self):
        """Обновление списка улиц при изменении участка"""
        section_id = self.section_combo.currentData()
        if not section_id:
            return

        try:
            streets = self.db_manager.get_streets(section_id)
            self.street_combo.clear()
            self.street_combo.addItem("Выберите улицу", None)
            for street in streets:
                self.street_combo.addItem(street['name'], street['id'])
        except Exception as e:
            print(f"Ошибка загрузки улиц: {e}")

    def load_counterparty_data(self):
        """Загрузка данных контрагента для редактирования"""
        if not self.counterparty_data:
            return

        try:
            # Основные данные
            self.id_edit.setText(self.counterparty_data.get('custom_id', ''))
            self.name_edit.setText(self.counterparty_data.get('name', ''))
            self.iin_bin_edit.setText(self.counterparty_data.get('iin_bin', ''))
            self.phone_edit.setText(self.counterparty_data.get('phone', ''))
            self.contract_number_edit.setText(self.counterparty_data.get('contract_number', ''))

            # Даты
            contract_date = self.counterparty_data.get('contract_date')
            if contract_date:
                self.contract_date_edit.setDate(QDate.fromString(contract_date, 'yyyy-MM-dd'))

            # Комбобоксы
            self.set_combo_value(self.category_combo, self.counterparty_data.get('category_id'))
            self.set_combo_value(self.contract_status_combo, self.counterparty_data.get('contract_status'))
            self.set_combo_value(self.contract_availability_combo, self.counterparty_data.get('contract_availability'))

            # Адресные данные
            self.set_combo_value(self.service_location_combo, self.counterparty_data.get('service_location_id'))
            QTimer.singleShot(100, self.load_sections_for_edit)

            self.house_edit.setText(self.counterparty_data.get('house', ''))
            self.apartment_edit.setText(self.counterparty_data.get('apartment', ''))
            self.notes_edit.setPlainText(self.counterparty_data.get('notes', ''))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")

    def load_sections_for_edit(self):
        """Загрузка участков для редактирования"""
        location_id = self.counterparty_data.get('service_location_id')
        if location_id:
            self.set_combo_value(self.service_location_combo, location_id)
            self.on_service_location_changed()
            QTimer.singleShot(100, self.load_streets_for_edit)

    def load_streets_for_edit(self):
        """Загрузка улиц для редактирования"""
        section_id = self.counterparty_data.get('section_id')
        if section_id:
            self.set_combo_value(self.section_combo, section_id)
            self.on_section_changed()
            QTimer.singleShot(100,
                              lambda: self.set_combo_value(self.street_combo, self.counterparty_data.get('street_id')))

    def set_combo_value(self, combo, value):
        """Установка значения в комбобокс"""
        if value is None:
            return

        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break

    def save_counterparty(self):
        """Сохранение контрагента"""
        try:
            # Валидация данных
            if not self.validate_data():
                return

            # Подготовка данных
            data = {
                'custom_id': self.id_edit.text().strip(),
                'category_id': self.category_combo.currentData(),
                'iin_bin': self.iin_bin_edit.text().strip(),
                'name': self.name_edit.text().strip(),
                'phone': self.phone_edit.text().strip(),
                'contract_number': self.contract_number_edit.text().strip(),
                'contract_date': self.contract_date_edit.date().toString("yyyy-MM-dd"),
                'contract_status': self.contract_status_combo.currentText(),
                'contract_availability': self.contract_availability_combo.currentText(),
                'notes': self.notes_edit.toPlainText().strip(),
                'service_location_id': self.service_location_combo.currentData(),
                'section_id': self.section_combo.currentData(),
                'street_id': self.street_combo.currentData(),
                'house': self.house_edit.text().strip(),
                'apartment': self.apartment_edit.text().strip(),
                'tariffs': self.prepare_tariffs(),
                'planned_volumes': self.prepare_planned_volumes()
            }

            # Сохранение в базу
            if self.is_edit_mode:
                success = self.db_manager.update_counterparty(
                    self.counterparty_id, data, self.user_id, "Редактирование через форму"
                )
            else:
                self.counterparty_id = self.db_manager.add_counterparty(data, self.user_id)
                success = self.counterparty_id is not None

            if success:
                QMessageBox.information(self, "Успех", "Данные успешно сохранены")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")

    def validate_data(self):
        """Валидация данных"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название контрагента")
            self.name_edit.setFocus()
            return False

        if not self.category_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            self.category_combo.setFocus()
            return False

        return True

    def prepare_tariffs(self):
        """Подготовка данных тарифов"""
        tariffs = []

        # Тарифы водоснабжения
        if self.water_tariff_edit.value() > 0:
            tariffs.append({
                'service_type': 'water_supply',
                'subservice_type': 'water_pipeline',
                'rate': self.water_tariff_edit.value()
            })

        if self.auto_water_tariff_edit.value() > 0:
            tariffs.append({
                'service_type': 'water_supply',
                'subservice_type': 'auto_transport',
                'rate': self.auto_water_tariff_edit.value()
            })

        if self.org_auto_water_tariff_edit.value() > 0:
            tariffs.append({
                'service_type': 'water_supply',
                'subservice_type': 'org_auto_transport',
                'rate': self.org_auto_water_tariff_edit.value()
            })

        # Тарифы водоотведения
        if self.sewer_tariff_edit.value() > 0:
            tariffs.append({
                'service_type': 'water_disposal',
                'subservice_type': 'sewer',
                'rate': self.sewer_tariff_edit.value()
            })

        if self.ass_tariff_edit.value() > 0:
            tariffs.append({
                'service_type': 'water_disposal',
                'subservice_type': 'ass',
                'rate': self.ass_tariff_edit.value()
            })

        if self.org_ass_tariff_edit.value() > 0:
            tariffs.append({
                'service_type': 'water_disposal',
                'subservice_type': 'org_ass',
                'rate': self.org_ass_tariff_edit.value()
            })

        return tariffs

    def prepare_planned_volumes(self):
        """Подготовка плановых объемов"""
        planned_volumes = []
        year = int(self.year_combo.currentText())

        # Водоснабжение
        for subservice, fields_key in [
            ('water_pipeline', 'water'),
            ('auto_transport', 'auto'),
            ('org_auto_transport', 'org')
        ]:
            volumes = {}
            for month in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                          'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']:
                field = self.water_plan_fields[month][fields_key]
                volumes[month.lower()] = field.value()

            if any(volumes.values()):  # Добавляем только если есть значения
                planned_volumes.append({
                    'service_type': 'water_supply',
                    'subservice_type': subservice,
                    'year': year,
                    **volumes
                })

        # Водоотведение
        for subservice, fields_key in [
            ('sewer', 'sewer'),
            ('ass', 'ass'),
            ('org_ass', 'org_ass')
        ]:
            volumes = {}
            for month in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                          'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']:
                field = self.disposal_plan_fields[month][fields_key]
                volumes[month.lower()] = field.value()

            if any(volumes.values()):
                planned_volumes.append({
                    'service_type': 'water_disposal',
                    'subservice_type': subservice,
                    'year': year,
                    **volumes
                })

        return planned_volumes


class ViewCounterpartyDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.user_data = user_data
        self.counterparty_data = None  # Добавьте эту строку
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle(f"Просмотр контрагента")
        self.setGeometry(100, 100, 1200, 800)

        layout = QVBoxLayout()

        # Верхняя часть с основной информацией
        top_info = QGroupBox("Основная информация")
        top_layout = QGridLayout(top_info)

        # Поля информации
        top_layout.addWidget(QLabel("ID:"), 0, 0)
        self.id_label = QLabel()
        top_layout.addWidget(self.id_label, 0, 1)

        top_layout.addWidget(QLabel("Улица:"), 0, 2)
        self.street_label = QLabel()
        top_layout.addWidget(self.street_label, 0, 3)

        top_layout.addWidget(QLabel("Дом:"), 1, 0)
        self.house_label = QLabel()
        top_layout.addWidget(self.house_label, 1, 1)

        top_layout.addWidget(QLabel("Квартира:"), 1, 2)
        self.apartment_label = QLabel()
        top_layout.addWidget(self.apartment_label, 1, 3)

        top_layout.addWidget(QLabel("Контрагент:"), 2, 0)
        self.name_label = QLabel()
        top_layout.addWidget(self.name_label, 2, 1)

        top_layout.addWidget(QLabel("ИИН/БИН:"), 2, 2)
        self.iin_bin_label = QLabel()
        top_layout.addWidget(self.iin_bin_label, 2, 3)

        top_layout.addWidget(QLabel("Телефон:"), 3, 0)
        self.phone_label = QLabel()
        top_layout.addWidget(self.phone_label, 3, 1)

        layout.addWidget(top_info)

        # Вкладки для водоснабжения и водоотведения
        self.tabs = QTabWidget()

        # Вкладка водоснабжения
        self.water_tab = QWidget()
        self.init_water_tab()
        self.tabs.addTab(self.water_tab, "Водоснабжение")

        # Вкладка водоотведения
        self.disposal_tab = QWidget()
        self.init_disposal_tab()
        self.tabs.addTab(self.disposal_tab, "Водоотведение")

        layout.addWidget(self.tabs)

        # Кнопки управления
        button_layout = QHBoxLayout()

        basic_info_btn = QPushButton("Основная информация")
        basic_info_btn.clicked.connect(self.show_basic_info)
        button_layout.addWidget(basic_info_btn)

        meter_info_btn = QPushButton("Информация о счетчиках")
        meter_info_btn.clicked.connect(self.show_meter_info)
        button_layout.addWidget(meter_info_btn)

        plan_volume_btn = QPushButton("Плановый объем услуг")
        plan_volume_btn.clicked.connect(self.show_plan_volume)
        button_layout.addWidget(plan_volume_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_data)
        button_layout.addWidget(save_btn)

        add_meter_btn = QPushButton("Добавить счетчик")
        add_meter_btn.clicked.connect(self.add_meter)
        button_layout.addWidget(add_meter_btn)

        delete_meter_btn = QPushButton("Удалить счетчик")
        delete_meter_btn.clicked.connect(self.delete_meter)
        button_layout.addWidget(delete_meter_btn)

        operations_btn = QPushButton("Операции")
        operations_btn.clicked.connect(self.show_operations)
        button_layout.addWidget(operations_btn)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def init_water_tab(self):
        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        # 1. Водопровод
        water_pipeline_group = QGroupBox("Водопровод")
        water_pipeline_layout = QVBoxLayout(water_pipeline_group)

        self.water_pipeline_table = QTableWidget()
        self.water_pipeline_table.setColumnCount(4)
        self.water_pipeline_table.setHorizontalHeaderLabels(
            ["Объект", "Предыдущее показание", "Текущее показание", "Расход"])
        water_pipeline_layout.addWidget(self.water_pipeline_table)

        # 2. Автотранспорт организации
        org_auto_group = QGroupBox("Автотранспорт организации")
        org_auto_layout = QVBoxLayout(org_auto_group)

        org_auto_form = QFormLayout()
        self.org_auto_location_combo = QComboBox()
        self.org_auto_volume_edit = QDoubleSpinBox()
        self.org_auto_trips_edit = QSpinBox()
        self.org_auto_date_edit = QDateEdit()
        self.org_auto_date_edit.setDate(QDate.currentDate())

        org_auto_form.addRow("Место оказания услуг:", self.org_auto_location_combo)
        org_auto_form.addRow("Объем м³:", self.org_auto_volume_edit)
        org_auto_form.addRow("Рейс:", self.org_auto_trips_edit)
        org_auto_form.addRow("Дата:", self.org_auto_date_edit)

        org_auto_layout.addLayout(org_auto_form)

        # 3. Автотранспорт
        auto_group = QGroupBox("Автотранспорт")
        auto_layout = QVBoxLayout(auto_group)

        auto_form = QFormLayout()
        self.auto_vehicle_edit = QLineEdit()
        self.auto_location_combo = QComboBox()
        self.auto_volume_edit = QDoubleSpinBox()
        self.auto_trips_edit = QSpinBox()

        auto_form.addRow("Номер автотранспорта:", self.auto_vehicle_edit)
        auto_form.addRow("Место оказания услуг:", self.auto_location_combo)
        auto_form.addRow("Объем м³:", self.auto_volume_edit)
        auto_form.addRow("Рейс:", self.auto_trips_edit)

        auto_layout.addLayout(auto_form)

        # 4. Примечание
        notes_group = QGroupBox("Примечание")
        notes_layout = QVBoxLayout(notes_group)
        self.water_notes_edit = QTextEdit()
        notes_layout.addWidget(self.water_notes_edit)

        splitter.addWidget(water_pipeline_group)
        splitter.addWidget(org_auto_group)
        splitter.addWidget(auto_group)
        splitter.addWidget(notes_group)

        splitter.setSizes([300, 250, 250, 200])
        layout.addWidget(splitter)
        self.water_tab.setLayout(layout)

    def init_disposal_tab(self):
        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        # 1. Канализация
        sewer_group = QGroupBox("Канализация")
        sewer_layout = QVBoxLayout(sewer_group)

        self.sewer_table = QTableWidget()
        self.sewer_table.setColumnCount(4)
        self.sewer_table.setHorizontalHeaderLabels(["Объект", "Предыдущее показание", "Текущее показание", "Расход"])
        sewer_layout.addWidget(self.sewer_table)

        # 2. Ассенизатор организации
        org_ass_group = QGroupBox("Ассенизатор организации")
        org_ass_layout = QVBoxLayout(org_ass_group)

        org_ass_form = QFormLayout()
        self.org_ass_location_combo = QComboBox()
        self.org_ass_volume_edit = QDoubleSpinBox()
        self.org_ass_trips_edit = QSpinBox()
        self.org_ass_date_edit = QDateEdit()
        self.org_ass_date_edit.setDate(QDate.currentDate())

        org_ass_form.addRow("Место оказания услуг:", self.org_ass_location_combo)
        org_ass_form.addRow("Объем м³:", self.org_ass_volume_edit)
        org_ass_form.addRow("Рейс:", self.org_ass_trips_edit)
        org_ass_form.addRow("Дата:", self.org_ass_date_edit)

        org_ass_layout.addLayout(org_ass_form)

        # 3. Ассенизатор
        ass_group = QGroupBox("Ассенизатор")
        ass_layout = QVBoxLayout(ass_group)

        ass_form = QFormLayout()
        self.ass_vehicle_edit = QLineEdit()
        self.ass_location_combo = QComboBox()
        self.ass_volume_edit = QDoubleSpinBox()
        self.ass_trips_edit = QSpinBox()

        ass_form.addRow("Номер автотранспорта:", self.ass_vehicle_edit)
        ass_form.addRow("Место оказания услуг:", self.ass_location_combo)
        ass_form.addRow("Объем м³:", self.ass_volume_edit)
        ass_form.addRow("Рейс:", self.ass_trips_edit)

        ass_layout.addLayout(ass_form)

        # 4. Примечание
        disposal_notes_group = QGroupBox("Примечание")
        disposal_notes_layout = QVBoxLayout(disposal_notes_group)
        self.disposal_notes_edit = QTextEdit()
        disposal_notes_layout.addWidget(self.disposal_notes_edit)

        splitter.addWidget(sewer_group)
        splitter.addWidget(org_ass_group)
        splitter.addWidget(ass_group)
        splitter.addWidget(disposal_notes_group)

        splitter.setSizes([300, 250, 250, 200])
        layout.addWidget(splitter)
        self.disposal_tab.setLayout(layout)

    def load_data(self):
        """Загрузка данных контрагента"""
        try:
            # Загрузка основной информации
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                SELECT c.*, cat.name as category_name, sl.name as service_location_name,
                       sec.name as section_name, st.name as street_name
                FROM counterparties c
                LEFT JOIN categories cat ON c.category_id = cat.id
                LEFT JOIN service_locations sl ON c.service_location_id = sl.id
                LEFT JOIN sections sec ON c.section_id = sec.id
                LEFT JOIN streets st ON c.street_id = st.id
                WHERE c.id = ?
            ''', (self.counterparty_id,))

            counterparty = cursor.fetchone()

            if counterparty:
                # Преобразуем Row в словарь
                counterparty_dict = dict(counterparty)

                self.id_label.setText(counterparty_dict.get('custom_id', ''))
                self.street_label.setText(counterparty_dict.get('street_name', ''))
                self.house_label.setText(counterparty_dict.get('house', ''))
                self.apartment_label.setText(counterparty_dict.get('apartment', ''))
                self.name_label.setText(counterparty_dict.get('name', ''))
                self.iin_bin_label.setText(counterparty_dict.get('iin_bin', ''))
                self.phone_label.setText(counterparty_dict.get('phone', ''))

                # Загрузка примечаний
                self.water_notes_edit.setPlainText(counterparty_dict.get('notes', ''))
                self.disposal_notes_edit.setPlainText(counterparty_dict.get('notes', ''))

                # Сохраняем данные контрагента для использования в других методах
                self.counterparty_data = counterparty_dict

                # Загрузка мест оказания услуг в комбобоксы
                self.load_service_locations()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")

    def load_service_locations(self):
        """Загрузка мест оказания услуг"""
        try:
            locations = self.db_manager.get_service_locations()

            for combo in [self.org_auto_location_combo, self.auto_location_combo,
                          self.org_ass_location_combo, self.ass_location_combo]:
                combo.clear()
                for location in locations:
                    combo.addItem(location['name'], location['id'])

        except Exception as e:
            print(f"Ошибка загрузки мест услуг: {e}")

    def show_basic_info(self):
        """Показ основной информации"""

        # Убедитесь, что передаем словарь, а не Row объект
        if hasattr(self.counterparty_data, '_fields'):  # Если это sqlite3.Row
            counterparty_data_dict = dict(self.counterparty_data)
        else:
            counterparty_data_dict = self.counterparty_data

        dialog = BasicInfoDialog(counterparty_data_dict, self.db_manager, self.user_data, self)
        if dialog.exec_():
            self.load_data()  # Перезагружаем данные после закрытия диалога

    def show_meter_info(self):
        """Показ информации о счетчиках"""
        dialog = MeterInfoDialog(self.counterparty_id, self.db_manager, self)
        dialog.exec_()

    def show_plan_volume(self):
        """Показ плановых объемов"""
        # Используем существующий диалог добавления контрагента в режиме просмотра

        dialog = AddCounterpartyDialog(self.db_manager, self.user_data['id'], self, self.counterparty_data)
        dialog.tabs.setCurrentIndex(1)  # Переход на вкладку плановых объемов
        dialog.exec_()

    def add_meter(self):
        """Добавление счетчика"""
        try:

            # Проверяем, что у нас есть корректный counterparty_id
            if not hasattr(self, 'counterparty_id') or not self.counterparty_id:
                QMessageBox.critical(self, "Ошибка", "Не удалось определить ID контрагента")
                return

            dialog = AddMeterDialog(self.counterparty_id, self.db_manager, self)
            if dialog.exec_():
                self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии диалога добавления счетчика: {str(e)}")
            print(f"Подробности ошибки: {e}")
            import traceback
            traceback.print_exc()

    def save_data(self):
        """Сохранение данных"""
        try:
            # Сохранение примечаний
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                UPDATE counterparties SET notes = ? WHERE id = ?
            ''', (self.water_notes_edit.toPlainText(), self.counterparty_id))

            self.db_manager.conn.commit()
            QMessageBox.information(self, "Успех", "Данные успешно сохранены")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")

    def delete_meter(self):
        """Удаление счетчика"""

        dialog = MeterInfoDialog(self.counterparty_id, self.db_manager, self)
        dialog.delete_meter()

    def show_operations(self):
        """Показ операций"""
        dialog = OperationsDialog(self.counterparty_id, self.db_manager, self)
        dialog.exec_()

    def add_operation(self):
        """Добавление операции (начисление)"""
        dialog = AddOperationDialog(self.counterparty_id, self.db_manager, self.user_data, self)
        if dialog.exec_():
            self.load_data()

    def show_plan_volume(self):
        """Показ плановых объемов"""
        dialog = PlanVolumeDialog(self.counterparty_id, self.db_manager, self.user_data, self)
        dialog.exec_()

# Реализация остальных диалогов будет аналогичной, но для экономии места приведу каркасы:

class CategoryManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Управление категориями")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Таблица категорий
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        layout.addWidget(self.categories_table)

        # Кнопки управления
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_category)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_category)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_category)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_data(self):
        try:
            categories = self.db_manager.get_categories()
            self.categories_table.setRowCount(len(categories))
            for row, category in enumerate(categories):
                self.categories_table.setItem(row, 0, QTableWidgetItem(str(category['id'])))
                self.categories_table.setItem(row, 1, QTableWidgetItem(category['name']))
                self.categories_table.setItem(row, 2, QTableWidgetItem(category.get('description', '')))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки категорий: {e}")

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Добавить категорию", "Введите название категории:")
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Категория добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления категории: {e}")

    def edit_category(self):
        selected = self.categories_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для редактирования")
            return

        category_id = int(self.categories_table.item(selected, 0).text())
        current_name = self.categories_table.item(selected, 1).text()

        name, ok = QInputDialog.getText(self, "Редактировать категорию", "Введите новое название:", text=current_name)
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Категория обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления категории: {e}")

    def delete_category(self):
        selected = self.categories_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для удаления")
            return

        category_id = int(self.categories_table.item(selected, 0).text())
        category_name = self.categories_table.item(selected, 1).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить категорию '{category_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Категория удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления категории: {e}")


class ServiceLocationManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Управление местами оказания услуг")
        self.setGeometry(100, 100, 700, 500)

        layout = QVBoxLayout()

        # Таблица мест оказания услуг
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(2)
        self.locations_table.setHorizontalHeaderLabels(["ID", "Название"])
        layout.addWidget(self.locations_table)

        # Кнопки управления
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_location)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_location)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_location)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_data(self):
        try:
            locations = self.db_manager.get_service_locations()
            self.locations_table.setRowCount(len(locations))
            for row, location in enumerate(locations):
                self.locations_table.setItem(row, 0, QTableWidgetItem(str(location['id'])))
                self.locations_table.setItem(row, 1, QTableWidgetItem(location['name']))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки мест услуг: {e}")

    def add_location(self):
        name, ok = QInputDialog.getText(self, "Добавить место услуг", "Введите название места оказания услуг:")
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("INSERT INTO service_locations (name) VALUES (?)", (name,))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Место оказания услуг добавлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def edit_location(self):
        selected = self.locations_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите место услуг для редактирования")
            return

        location_id = int(self.locations_table.item(selected, 0).text())
        current_name = self.locations_table.item(selected, 1).text()

        name, ok = QInputDialog.getText(self, "Редактировать место услуг", "Введите новое название:", text=current_name)
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("UPDATE service_locations SET name = ? WHERE id = ?", (name, location_id))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Место оказания услуг обновлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {e}")

    def delete_location(self):
        selected = self.locations_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите место услуг для удаления")
            return

        location_id = int(self.locations_table.item(selected, 0).text())
        location_name = self.locations_table.item(selected, 1).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить место услуг '{location_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("DELETE FROM service_locations WHERE id = ?", (location_id,))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Место оказания услуг удалено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")


class SectionManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Управление участками")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Выбор места оказания услуг
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Место оказания услуг:"))
        self.location_combo = QComboBox()
        self.location_combo.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.location_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица участков
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(3)
        self.sections_table.setHorizontalHeaderLabels(["ID", "Название", "Место услуг"])
        layout.addWidget(self.sections_table)

        # Кнопки управления
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_section)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_section)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_section)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_locations()

    def load_locations(self):
        """Загрузка мест оказания услуг"""
        try:
            locations = self.db_manager.get_service_locations()
            self.location_combo.clear()
            self.location_combo.addItem("Все места", None)
            for location in locations:
                self.location_combo.addItem(location['name'], location['id'])
        except Exception as e:
            print(f"Ошибка загрузки мест услуг: {e}")

    def load_data(self):
        """Загрузка участков"""
        try:
            location_id = self.location_combo.currentData()

            if location_id:
                sections = self.db_manager.get_sections(location_id)
            else:
                # Загрузка всех участков
                cursor = self.db_manager.conn.cursor()
                cursor.execute('''
                    SELECT s.*, sl.name as location_name 
                    FROM sections s
                    LEFT JOIN service_locations sl ON s.service_location_id = sl.id
                    ORDER BY sl.name, s.name
                ''')
                sections = cursor.fetchall()

            self.sections_table.setRowCount(len(sections))
            for row, section in enumerate(sections):
                self.sections_table.setItem(row, 0, QTableWidgetItem(str(section['id'])))
                self.sections_table.setItem(row, 1, QTableWidgetItem(section['name']))
                self.sections_table.setItem(row, 2, QTableWidgetItem(section.get('location_name', '')))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки участков: {e}")

    def add_section(self):
        location_id = self.location_combo.currentData()
        if not location_id:
            QMessageBox.warning(self, "Ошибка", "Выберите место оказания услуг")
            return

        name, ok = QInputDialog.getText(self, "Добавить участок", "Введите название участка:")
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("INSERT INTO sections (name, service_location_id) VALUES (?, ?)",
                               (name, location_id))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Участок добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления участка: {e}")

    def edit_section(self):
        selected = self.sections_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите участок для редактирования")
            return

        section_id = int(self.sections_table.item(selected, 0).text())
        current_name = self.sections_table.item(selected, 1).text()

        name, ok = QInputDialog.getText(self, "Редактировать участок", "Введите новое название:", text=current_name)
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("UPDATE sections SET name = ? WHERE id = ?", (name, section_id))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Участок обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления участка: {e}")

    def delete_section(self):
        selected = self.sections_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите участок для удаления")
            return

        section_id = int(self.sections_table.item(selected, 0).text())
        section_name = self.sections_table.item(selected, 1).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить участок '{section_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Участок удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления участка: {e}")


class StreetManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Управление улицами")
        self.setGeometry(100, 100, 900, 700)

        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Место оказания услуг:"))
        self.location_combo = QComboBox()
        self.location_combo.currentIndexChanged.connect(self.on_location_changed)
        filter_layout.addWidget(self.location_combo)

        filter_layout.addWidget(QLabel("Участок:"))
        self.section_combo = QComboBox()
        self.section_combo.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.section_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица улиц
        self.streets_table = QTableWidget()
        self.streets_table.setColumnCount(4)
        self.streets_table.setHorizontalHeaderLabels(["ID", "Название", "Участок", "Место услуг"])
        layout.addWidget(self.streets_table)

        # Кнопки управления
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_street)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_street)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_street)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_locations()

    def load_locations(self):
        """Загрузка мест оказания услуг"""
        try:
            locations = self.db_manager.get_service_locations()
            self.location_combo.clear()
            self.location_combo.addItem("Все места", None)
            for location in locations:
                self.location_combo.addItem(location['name'], location['id'])
        except Exception as e:
            print(f"Ошибка загрузки мест услуг: {e}")

    def on_location_changed(self):
        """Обновление списка участков при изменении места оказания услуг"""
        location_id = self.location_combo.currentData()

        try:
            sections = self.db_manager.get_sections(location_id) if location_id else []
            self.section_combo.clear()
            self.section_combo.addItem("Все участки", None)
            for section in sections:
                self.section_combo.addItem(section['name'], section['id'])
        except Exception as e:
            print(f"Ошибка загрузки участков: {e}")

        self.load_data()

    def load_data(self):
        """Загрузка улиц"""
        try:
            location_id = self.location_combo.currentData()
            section_id = self.section_combo.currentData()

            cursor = self.db_manager.conn.cursor()

            if section_id:
                streets = self.db_manager.get_streets(section_id)
            elif location_id:
                cursor.execute('''
                    SELECT st.*, s.name as section_name, sl.name as location_name
                    FROM streets st
                    LEFT JOIN sections s ON st.section_id = s.id
                    LEFT JOIN service_locations sl ON s.service_location_id = sl.id
                    WHERE s.service_location_id = ?
                    ORDER BY sl.name, s.name, st.name
                ''', (location_id,))
                streets = cursor.fetchall()
            else:
                cursor.execute('''
                    SELECT st.*, s.name as section_name, sl.name as location_name
                    FROM streets st
                    LEFT JOIN sections s ON st.section_id = s.id
                    LEFT JOIN service_locations sl ON s.service_location_id = sl.id
                    ORDER BY sl.name, s.name, st.name
                ''')
                streets = cursor.fetchall()

            self.streets_table.setRowCount(len(streets))
            for row, street in enumerate(streets):
                self.streets_table.setItem(row, 0, QTableWidgetItem(str(street['id'])))
                self.streets_table.setItem(row, 1, QTableWidgetItem(street['name']))
                self.streets_table.setItem(row, 2, QTableWidgetItem(street.get('section_name', '')))
                self.streets_table.setItem(row, 3, QTableWidgetItem(street.get('location_name', '')))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки улиц: {e}")

    def add_street(self):
        section_id = self.section_combo.currentData()
        if not section_id:
            QMessageBox.warning(self, "Ошибка", "Выберите участок")
            return

        name, ok = QInputDialog.getText(self, "Добавить улицу", "Введите название улицы:")
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("INSERT INTO streets (name, section_id) VALUES (?, ?)",
                               (name, section_id))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Улица добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления улицы: {e}")

    def edit_street(self):
        selected = self.streets_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите улицу для редактирования")
            return

        street_id = int(self.streets_table.item(selected, 0).text())
        current_name = self.streets_table.item(selected, 1).text()

        name, ok = QInputDialog.getText(self, "Редактировать улицу", "Введите новое название:", text=current_name)
        if ok and name:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("UPDATE streets SET name = ? WHERE id = ?", (name, street_id))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Улица обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления улицы: {e}")

    def delete_street(self):
        selected = self.streets_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите улицу для удаления")
            return

        street_id = int(self.streets_table.item(selected, 0).text())
        street_name = self.streets_table.item(selected, 1).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить улицу '{street_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("DELETE FROM streets WHERE id = ?", (street_id,))
                self.db_manager.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Успех", "Улица удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления улицы: {e}")


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("О программе")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Название программы
        title_label = QLabel("База данных контрагентов")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Версия
        version_label = QLabel("Версия 1.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Описание
        description_label = QLabel(
            "Программа для учета контрагентов и управления договорами.\n\n"
            "Функциональность:\n"
            "• Управление контрагентами\n"
            "• Учет договоров и их статусов\n"
            "• Планирование объемов услуг\n"
            "• Генерация отчетов\n"
            "• Резервное копирование данных"
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

class ReportDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Генерация отчетов")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Вкладка "Отчет по шаблону"
        self.template_tab = QWidget()
        self.init_template_tab()
        self.tabs.addTab(self.template_tab, "Отчет по шаблону")

        # Вкладка "Сводный отчет"
        self.summary_tab = QWidget()
        self.init_summary_tab()
        self.tabs.addTab(self.summary_tab, "Сводный отчет")

        layout.addWidget(self.tabs)

        # Кнопки
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Сгенерировать отчет")
        generate_btn.clicked.connect(self.generate_report)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def init_template_tab(self):
        layout = QVBoxLayout()

        # Выбор полей для отчета
        fields_group = QGroupBox("Выберите поля для отчета")
        fields_layout = QVBoxLayout()

        self.field_checkboxes = {}
        fields = [
            "ID", "ИИН/БИН", "Контрагент", "Место оказание услуг", "Участок",
            "Улица", "Дом", "Кв", "Объект", "Телефон", "Пред.показание",
            "Тек.показание", "Расход", "Номер автотранспорта", "Плановый объем",
            "Фактический объем", "Категория"
        ]

        # Размещение чекбоксов в 3 колонки
        columns_layout = QHBoxLayout()

        for i in range(3):
            column_layout = QVBoxLayout()
            start_idx = i * 6
            end_idx = min((i + 1) * 6, len(fields))

            for j in range(start_idx, end_idx):
                checkbox = QCheckBox(fields[j])
                self.field_checkboxes[fields[j]] = checkbox
                column_layout.addWidget(checkbox)

            column_layout.addStretch()
            columns_layout.addLayout(column_layout)

        fields_layout.addLayout(columns_layout)
        fields_group.setLayout(fields_layout)
        layout.addWidget(fields_group)

        self.template_tab.setLayout(layout)

    def init_summary_tab(self):
        layout = QVBoxLayout()

        # Параметры сводного отчета
        params_group = QGroupBox("Параметры отчета")
        params_layout = QGridLayout()

        params_layout.addWidget(QLabel("Категория:"), 0, 0)
        self.summary_category_combo = QComboBox()
        self.summary_category_combo.addItem("Все категории", None)
        params_layout.addWidget(self.summary_category_combo, 0, 1)

        params_layout.addWidget(QLabel("Место оказания услуг:"), 1, 0)
        self.summary_location_combo = QComboBox()
        self.summary_location_combo.addItem("Все места", None)
        params_layout.addWidget(self.summary_location_combo, 1, 1)

        params_layout.addWidget(QLabel("Участок:"), 2, 0)
        self.summary_section_combo = QComboBox()
        self.summary_section_combo.addItem("Все участки", None)
        params_layout.addWidget(self.summary_section_combo, 2, 1)

        params_layout.addWidget(QLabel("Период с:"), 3, 0)
        self.period_from = QDateEdit()
        self.period_from.setDate(QDate.currentDate().addMonths(-1))
        params_layout.addWidget(self.period_from, 3, 1)

        params_layout.addWidget(QLabel("по:"), 3, 2)
        self.period_to = QDateEdit()
        self.period_to.setDate(QDate.currentDate())
        params_layout.addWidget(self.period_to, 3, 3)

        params_layout.addWidget(QLabel("Год:"), 4, 0)
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_year))
        params_layout.addWidget(self.year_combo, 4, 1)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Тип отчета
        report_type_group = QGroupBox("Тип отчета")
        report_type_layout = QVBoxLayout()

        self.summary_type_combo = QComboBox()
        self.summary_type_combo.addItems([
            "Отчет по договорам",
            "Отчет по плановым объемам",
            "Отчет по фактическим объемам",
            "Сравнительный анализ"
        ])
        report_type_layout.addWidget(self.summary_type_combo)

        report_type_group.setLayout(report_type_layout)
        layout.addWidget(report_type_group)

        layout.addStretch()

        self.summary_tab.setLayout(layout)
        self.load_summary_filters()

    def load_summary_filters(self):
        """Загрузка фильтров для сводного отчета"""
        try:
            # Категории
            categories = self.db_manager.get_categories()
            for category in categories:
                self.summary_category_combo.addItem(category['name'], category['id'])

            # Места оказания услуг
            locations = self.db_manager.get_service_locations()
            for location in locations:
                self.summary_location_combo.addItem(location['name'], location['id'])

        except Exception as e:
            print(f"Ошибка загрузки фильтров: {e}")

    def generate_report(self):
        """Генерация отчета"""
        current_tab = self.tabs.currentIndex()

        if current_tab == 0:  # Отчет по шаблону
            self.generate_template_report()
        elif current_tab == 1:  # Сводный отчет
            self.generate_summary_report()

    def generate_template_report(self):
        """Генерация отчета по шаблону"""
        selected_fields = [field for field, checkbox in self.field_checkboxes.items()
                           if checkbox.isChecked()]

        if not selected_fields:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одно поле для отчета")
            return

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить отчет",
                f"отчет_по_шаблону_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )

            if not file_path:
                return

            progress = QProgressDialog("Генерация отчета...", "Отмена", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            # Получение данных
            progress.setValue(10)
            data = self.db_manager.get_counterparties()

            # Создание книги Excel
            progress.setValue(30)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Отчет по шаблону"

            # Заголовки
            for col, field in enumerate(selected_fields, 1):
                cell = ws.cell(row=1, column=col, value=field)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
                cell.alignment = Alignment(horizontal='center', vertical='center')

            # Соответствие полей данным
            field_mapping = {
                "ID": "custom_id",
                "ИИН/БИН": "iin_bin",
                "Контрагент": "name",
                "Место оказание услуг": "service_location_name",
                "Участок": "section_name",
                "Улица": "street_name",
                "Дом": "house",
                "Кв": "apartment",
                "Категория": "category_name",
                "Телефон": "phone"
            }

            # Данные
            progress.setValue(50)
            for row, counterparty in enumerate(data, 2):
                for col, field in enumerate(selected_fields, 1):
                    db_field = field_mapping.get(field, field.lower())
                    value = counterparty.get(db_field, '')
                    ws.cell(row=row, column=col, value=value)

                if row % 50 == 0:
                    progress.setValue(50 + (row * 40 // len(data)))
                    QApplication.processEvents()

            # Автоподбор ширины колонок
            progress.setValue(90)
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            progress.setValue(100)
            wb.save(file_path)
            progress.close()

            QMessageBox.information(self, "Успех", f"Отчет сохранен:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета: {e}")

    def generate_summary_report(self):
        """Генерация сводного отчета"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить сводный отчет",
                f"сводный_отчет_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )

            if not file_path:
                return

            # Создание книги Excel
            wb = openpyxl.Workbook()

            # Статистика по договорам
            ws_stats = wb.active
            ws_stats.title = "Статистика договоров"

            # Получение данных
            filters = {}
            category_id = self.summary_category_combo.currentData()
            location_id = self.summary_location_combo.currentData()
            section_id = self.summary_section_combo.currentData()

            if category_id:
                filters['category_id'] = category_id
            if location_id:
                filters['service_location_id'] = location_id
            if section_id:
                filters['section_id'] = section_id

            data = self.db_manager.get_counterparties(filters)

            # Заголовки статистики
            headers = ['Показатель', 'Значение']
            for col, header in enumerate(headers, 1):
                cell = ws_stats.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

            # Статистика
            stats = self.db_manager.get_statistics()
            statistics_data = [
                ['Всего договоров', stats.get('total', 0)],
                ['Действующие договоры', stats.get('active', 0)],
                ['Расторгнутые договоры', stats.get('terminated', 0)],
                ['Договоры в наличии', stats.get('available', 0)],
                ['Договоры не в наличии', stats.get('not_available', 0)]
            ]

            for row, (label, value) in enumerate(statistics_data, 2):
                ws_stats.cell(row=row, column=1, value=label)
                ws_stats.cell(row=row, column=2, value=value)

            # Создание диаграммы
            chart = PieChart()
            labels = Reference(ws_stats, min_col=1, min_row=2, max_row=6)
            data_ref = Reference(ws_stats, min_col=2, min_row=1, max_row=6)
            chart.add_data(data_ref, titles_from_data=True)
            chart.set_categories(labels)
            chart.title = "Статистика договоров"
            ws_stats.add_chart(chart, "D2")

            # Лист с детализацией
            ws_detail = wb.create_sheet("Детализация")

            # Заголовки детализации
            detail_headers = ['ID', 'Контрагент', 'Категория', 'Место услуг', 'Статус', 'Наличие']
            for col, header in enumerate(detail_headers, 1):
                cell = ws_detail.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

            # Данные детализации
            for row, counterparty in enumerate(data, 2):
                ws_detail.cell(row=row, column=1, value=counterparty.get('custom_id', ''))
                ws_detail.cell(row=row, column=2, value=counterparty.get('name', ''))
                ws_detail.cell(row=row, column=3, value=counterparty.get('category_name', ''))
                ws_detail.cell(row=row, column=4, value=counterparty.get('service_location_name', ''))
                ws_detail.cell(row=row, column=5, value=counterparty.get('contract_status', ''))
                ws_detail.cell(row=row, column=6, value=counterparty.get('contract_availability', ''))

            # Автоподбор ширины колонок
            for ws in [ws_stats, ws_detail]:
                for column in ws.columns:
                    max_length = 0
                    column_letter = get_column_letter(column[0].column)
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width

            wb.save(file_path)
            QMessageBox.information(self, "Успех", f"Сводный отчет сохранен:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации сводного отчета: {e}")


class MassOperationsDialog(QDialog):
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Массовые операции")
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Выбор типа операции
        operation_group = QGroupBox("Тип операции")
        operation_layout = QVBoxLayout()

        self.mass_termination_radio = QRadioButton("Массовое расторжение договора")
        self.mass_update_radio = QRadioButton("Массовое изменение показаний")
        self.mass_termination_radio.setChecked(True)

        operation_layout.addWidget(self.mass_termination_radio)
        operation_layout.addWidget(self.mass_update_radio)

        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)

        # Параметры фильтрации
        filter_group = QGroupBox("Параметры фильтрации")
        filter_layout = QGridLayout()

        filter_layout.addWidget(QLabel("Категория:"), 0, 0)
        self.mass_category_combo = QComboBox()
        self.mass_category_combo.addItem("Все категории", None)
        filter_layout.addWidget(self.mass_category_combo, 0, 1)

        filter_layout.addWidget(QLabel("Место оказания услуг:"), 1, 0)
        self.mass_location_combo = QComboBox()
        self.mass_location_combo.addItem("Все места", None)
        filter_layout.addWidget(self.mass_location_combo, 1, 1)

        filter_layout.addWidget(QLabel("Участок:"), 2, 0)
        self.mass_section_combo = QComboBox()
        self.mass_section_combo.addItem("Все участки", None)
        filter_layout.addWidget(self.mass_section_combo, 2, 1)

        filter_layout.addWidget(QLabel("Год:"), 3, 0)
        self.mass_year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            self.mass_year_combo.addItem(str(year))
        filter_layout.addWidget(self.mass_year_combo, 3, 1)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Дополнительные параметры
        params_group = QGroupBox("Дополнительные параметры")
        params_layout = QVBoxLayout()

        self.reason_edit = QLineEdit()
        self.reason_edit.setPlaceholderText("Причина массовой операции...")
        params_layout.addWidget(QLabel("Причина:"))
        params_layout.addWidget(self.reason_edit)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Предварительный просмотр
        preview_group = QGroupBox("Предварительный просмотр")
        preview_layout = QVBoxLayout()

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(['ID', 'Контрагент', 'Статус', 'Действие'])
        preview_layout.addWidget(self.preview_table)

        preview_btn = QPushButton("Обновить предпросмотр")
        preview_btn.clicked.connect(self.update_preview)
        preview_layout.addWidget(preview_btn)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Кнопки
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить операцию")
        apply_btn.clicked.connect(self.apply_mass_operation)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_filters()
        self.update_preview()

    def load_filters(self):
        """Загрузка фильтров"""
        try:
            categories = self.db_manager.get_categories()
            for category in categories:
                self.mass_category_combo.addItem(category['name'], category['id'])

            locations = self.db_manager.get_service_locations()
            for location in locations:
                self.mass_location_combo.addItem(location['name'], location['id'])

        except Exception as e:
            print(f"Ошибка загрузки фильтров: {e}")

    def update_preview(self):
        """Обновление предварительного просмотра"""
        try:
            filters = self.get_current_filters()
            data = self.db_manager.get_counterparties(filters)

            self.preview_table.setRowCount(len(data))
            for row, counterparty in enumerate(data):
                self.preview_table.setItem(row, 0, QTableWidgetItem(counterparty.get('custom_id', '')))
                self.preview_table.setItem(row, 1, QTableWidgetItem(counterparty.get('name', '')))
                self.preview_table.setItem(row, 2, QTableWidgetItem(counterparty.get('contract_status', '')))

                # Действие
                if self.mass_termination_radio.isChecked():
                    action = "Расторгнуть договор"
                else:
                    action = "Обновить показания"

                self.preview_table.setItem(row, 3, QTableWidgetItem(action))

        except Exception as e:
            print(f"Ошибка обновления предпросмотра: {e}")

    def get_current_filters(self):
        """Получение текущих фильтров"""
        filters = {}

        category_id = self.mass_category_combo.currentData()
        location_id = self.mass_location_combo.currentData()
        section_id = self.mass_section_combo.currentData()

        if category_id:
            filters['category_id'] = category_id
        if location_id:
            filters['service_location_id'] = location_id
        if section_id:
            filters['section_id'] = section_id

        return filters

    def apply_mass_operation(self):
        """Применение массовой операции"""
        if not self.reason_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Укажите причину массовой операции")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите выполнить массовую операцию?\n"
            "Это действие затронет все отфильтрованные записи.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                filters = self.get_current_filters()
                data = self.db_manager.get_counterparties(filters)

                if self.mass_termination_radio.isChecked():
                    self.mass_terminate_contracts(data)
                else:
                    self.mass_update_readings(data)

                QMessageBox.information(self, "Успех", "Массовая операция выполнена")
                self.accept()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения операции: {e}")

    def mass_terminate_contracts(self, data):
        """Массовое расторжение договоров"""
        try:
            cursor = self.db_manager.conn.cursor()
            reason = self.reason_edit.text().strip()

            for counterparty in data:
                cursor.execute('''
                    UPDATE counterparties 
                    SET contract_status = 'terminated', updated_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (counterparty['id'],))

            self.db_manager.conn.commit()
            self.db_manager.data_updated.emit()

        except Exception as e:
            self.db_manager.conn.rollback()
            raise e

    def mass_update_readings(self, data):
        """Массовое обновление показаний"""
        # Реализация массового обновления показаний
        pass


class SortDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.sort_params = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Сортировка и фильтрация")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Параметры сортировки
        sort_group = QGroupBox("Сортировка")
        sort_layout = QFormLayout(sort_group)

        self.sort_field_combo = QComboBox()
        self.sort_field_combo.addItems([
            "ID", "Категория", "ИИН/БИН", "Контрагент", "Телефон",
            "Номер договора", "Дата договора", "Статус договора"
        ])
        sort_layout.addRow("Поле сортировки:", self.sort_field_combo)

        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["По возрастанию", "По убыванию"])
        sort_layout.addRow("Порядок:", self.sort_order_combo)

        layout.addWidget(sort_group)

        # Кнопки
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self.apply_sorting)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def apply_sorting(self):
        """Применение сортировки"""
        self.sort_params = {
            'field': self.sort_field_combo.currentText(),
            'order': self.sort_order_combo.currentText()
        }
        self.accept()

    def get_sort_params(self):
        return self.sort_params


class BasicInfoDialog(QDialog):
    def __init__(self, counterparty_data, db_manager, user_data, parent=None):
        super().__init__(parent)
        # Убедитесь, что counterparty_data является словарем, а не Row объектом
        if hasattr(counterparty_data, '_fields'):  # Если это sqlite3.Row
            self.counterparty_data = dict(counterparty_data)
        else:
            self.counterparty_data = counterparty_data

        self.db_manager = db_manager
        self.user_data = user_data
        self.counterparty_id = self.counterparty_data['id']
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Основная информация")
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout(info_group)

        self.id_label = QLabel(self.counterparty_data.get('custom_id', ''))
        self.name_label = QLabel(self.counterparty_data.get('name', ''))
        self.iin_bin_label = QLabel(self.counterparty_data.get('iin_bin', ''))
        self.phone_label = QLabel(self.counterparty_data.get('phone', ''))
        self.category_label = QLabel(self.counterparty_data.get('category_name', ''))
        self.location_label = QLabel(self.counterparty_data.get('service_location_name', ''))
        self.section_label = QLabel(self.counterparty_data.get('section_name', ''))
        self.street_label = QLabel(self.counterparty_data.get('street_name', ''))
        self.house_label = QLabel(self.counterparty_data.get('house', ''))
        self.apartment_label = QLabel(self.counterparty_data.get('apartment', ''))

        info_layout.addRow("ID:", self.id_label)
        info_layout.addRow("Контрагент:", self.name_label)
        info_layout.addRow("ИИН/БИН:", self.iin_bin_label)
        info_layout.addRow("Телефон:", self.phone_label)
        info_layout.addRow("Категория:", self.category_label)
        info_layout.addRow("Место услуг:", self.location_label)
        info_layout.addRow("Участок:", self.section_label)
        info_layout.addRow("Улица:", self.street_label)
        info_layout.addRow("Дом:", self.house_label)
        info_layout.addRow("Квартира:", self.apartment_label)

        # Информация о договоре
        contract_group = QGroupBox("Информация о договоре")
        contract_layout = QFormLayout(contract_group)

        self.contract_number_edit = QLineEdit(self.counterparty_data.get('contract_number', ''))
        self.contract_date_edit = QDateEdit()
        contract_date = self.counterparty_data.get('contract_date')
        if contract_date:
            self.contract_date_edit.setDate(QDate.fromString(contract_date, 'yyyy-MM-dd'))
        else:
            self.contract_date_edit.setDate(QDate.currentDate())

        self.contract_status_combo = QComboBox()
        self.contract_status_combo.addItems(["активный", "расторгнут", "приостановлен"])
        self.contract_status_combo.setCurrentText(self.counterparty_data.get('contract_status', 'активный'))

        self.contract_availability_combo = QComboBox()
        self.contract_availability_combo.addItems(["Есть в наличии", "Нет в наличии"])
        self.contract_availability_combo.setCurrentText(
            self.counterparty_data.get('contract_availability', 'Нет в наличии'))

        contract_layout.addRow("Номер договора:", self.contract_number_edit)
        contract_layout.addRow("Дата договора:", self.contract_date_edit)
        contract_layout.addRow("Статус договора:", self.contract_status_combo)
        contract_layout.addRow("Наличие договора:", self.contract_availability_combo)

        # Если пользователь не админ, сделать поля только для чтения
        if self.user_data['role'] != 'admin':
            self.contract_number_edit.setReadOnly(True)
            self.contract_date_edit.setReadOnly(True)
            self.contract_status_combo.setEnabled(False)
            self.contract_availability_combo.setEnabled(False)

        # Кнопки
        button_layout = QHBoxLayout()

        if self.user_data['role'] == 'admin':
            edit_contract_btn = QPushButton("Изменить договор")
            edit_contract_btn.clicked.connect(self.edit_contract)
            button_layout.addWidget(edit_contract_btn)

            edit_data_btn = QPushButton("Редактировать данные")
            edit_data_btn.clicked.connect(self.edit_data)
            button_layout.addWidget(edit_data_btn)

            contract_history_btn = QPushButton("История изменения договора")
            contract_history_btn.clicked.connect(self.show_contract_history)
            button_layout.addWidget(contract_history_btn)

            change_history_btn = QPushButton("История изменений")
            change_history_btn.clicked.connect(self.show_change_history)
            button_layout.addWidget(change_history_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_data)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)

        layout.addWidget(info_group)
        layout.addWidget(contract_group)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_data(self):
        """Загрузка данных"""
        pass

    def edit_contract(self):
        """Редактирование договора (только номер и дата)"""
        self.contract_number_edit.setReadOnly(False)
        self.contract_date_edit.setReadOnly(False)
        QMessageBox.information(self, "Информация", "Теперь можно редактировать номер и дату договора")

    def edit_data(self):
        """Редактирование всех данных"""

        dialog = AddCounterpartyDialog(self.db_manager, self.user_data['id'], self, self.counterparty_data)
        if dialog.exec_():
            self.accept()

    def show_contract_history(self):
        """Показать историю изменений договора"""
        dialog = ContractHistoryDialog(self.counterparty_id, self.db_manager, self)
        dialog.exec_()

    def show_change_history(self):
        """Показать историю изменений данных"""
        dialog = ChangeHistoryDialog(self.counterparty_id, self.db_manager, self)
        dialog.exec_()

    def save_data(self):
        """Сохранение данных"""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                UPDATE counterparties SET 
                contract_number = ?, contract_date = ?, contract_status = ?, 
                contract_availability = ?, updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                self.contract_number_edit.text(),
                self.contract_date_edit.date().toString("yyyy-MM-dd"),
                self.contract_status_combo.currentText(),
                self.contract_availability_combo.currentText(),
                self.counterparty_id
            ))

            # Запись в историю изменений
            cursor.execute('''
                INSERT INTO change_history (counterparty_id, changed_by, reason)
                VALUES (?, ?, ?)
            ''', (self.counterparty_id, self.user_data['id'], "Изменение данных через основную информацию"))

            self.db_manager.conn.commit()
            QMessageBox.information(self, "Успех", "Данные успешно сохранены")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")


class MeterInfoDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.init_ui()
        self.load_meters()

    def init_ui(self):
        self.setWindowTitle("Информация о счетчиках")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Таблица счетчиков
        self.meters_table = QTableWidget()
        self.meters_table.setColumnCount(7)
        self.meters_table.setHorizontalHeaderLabels([
            "ID", "Вид услуг", "Тип услуги", "Объект",
            "Начальное показание", "Текущее показание", "Расход"
        ])
        layout.addWidget(self.meters_table)

        # Кнопки
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить счетчик")
        add_btn.clicked.connect(self.add_meter)
        delete_btn = QPushButton("Удалить счетчик")
        delete_btn.clicked.connect(self.delete_meter)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_meters(self):
        """Загрузка данных о счетчиках"""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                SELECT * FROM meters WHERE counterparty_id = ? AND is_active = 1
            ''', (self.counterparty_id,))
            meters = cursor.fetchall()

            self.meters_table.setRowCount(len(meters))
            for row, meter in enumerate(meters):
                self.meters_table.setItem(row, 0, QTableWidgetItem(str(meter['id'])))
                self.meters_table.setItem(row, 1, QTableWidgetItem(meter['service_type']))
                self.meters_table.setItem(row, 2, QTableWidgetItem(meter['subservice_type']))
                self.meters_table.setItem(row, 3, QTableWidgetItem(meter.get('object_name', '')))
                self.meters_table.setItem(row, 4, QTableWidgetItem(str(meter.get('initial_reading', 0))))
                self.meters_table.setItem(row, 5, QTableWidgetItem(str(meter.get('current_reading', 0))))
                consumption = meter.get('current_reading', 0) - meter.get('initial_reading', 0)
                self.meters_table.setItem(row, 6, QTableWidgetItem(str(consumption)))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки счетчиков: {e}")

    def add_meter(self):
        """Добавление счетчика"""
        dialog = AddMeterDialog(self.counterparty_id, self.db_manager, self)
        if dialog.exec_():
            self.load_meters()

    def delete_meter(self):
        """Удаление счетчика"""
        selected = self.meters_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите счетчик для удаления")
            return

        meter_id = int(self.meters_table.item(selected, 0).text())

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить счетчик?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute('''
                    UPDATE meters SET is_active = 0 WHERE id = ?
                ''', (meter_id,))
                self.db_manager.conn.commit()
                self.load_meters()
                QMessageBox.information(self, "Успех", "Счетчик удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")


class AddMeterDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.init_ui()
        self.load_counterparty_data()

    def init_ui(self):
        self.setWindowTitle("Добавить счетчик")
        self.setGeometry(100, 100, 500, 600)

        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Основная информация
        basic_group = QGroupBox("Основная информация")
        basic_layout = QFormLayout(basic_group)

        self.location_combo = QComboBox()
        self.section_combo = QComboBox()
        self.street_combo = QComboBox()
        self.house_edit = QLineEdit()
        self.apartment_edit = QLineEdit()
        self.object_edit = QLineEdit()

        basic_layout.addRow("Место оказания услуг:", self.location_combo)
        basic_layout.addRow("Участок:", self.section_combo)
        basic_layout.addRow("Улица:", self.street_combo)
        basic_layout.addRow("Дом:", self.house_edit)
        basic_layout.addRow("Квартира:", self.apartment_edit)
        basic_layout.addRow("Объект:", self.object_edit)

        # Виды услуг
        services_group = QGroupBox("Виды услуг")
        services_layout = QVBoxLayout(services_group)

        self.water_supply_check = QCheckBox("Водоснабжение")
        self.water_disposal_check = QCheckBox("Водоотведение")
        self.link_services_check = QCheckBox("Связать оба вида услуг")

        services_layout.addWidget(self.water_supply_check)
        services_layout.addWidget(self.water_disposal_check)
        services_layout.addWidget(self.link_services_check)

        # Показания
        readings_group = QGroupBox("Показания")
        readings_layout = QFormLayout(readings_group)

        self.initial_reading_edit = QDoubleSpinBox()
        self.initial_reading_edit.setMaximum(999999)
        self.current_reading_edit = QDoubleSpinBox()
        self.current_reading_edit.setMaximum(999999)

        readings_layout.addRow("Начальное показание:", self.initial_reading_edit)
        readings_layout.addRow("Текущее показание:", self.current_reading_edit)

        content_layout.addWidget(basic_group)
        content_layout.addWidget(services_group)
        content_layout.addWidget(readings_group)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_meter)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_counterparty_data(self):
        """Загрузка данных контрагента"""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                SELECT * FROM counterparties WHERE id = ?
            ''', (self.counterparty_id,))

            counterparty = cursor.fetchone()

            if counterparty:
                # Преобразуем в словарь если нужно
                if hasattr(counterparty, '_fields'):
                    counterparty = dict(counterparty)

                self.house_edit.setText(counterparty.get('house', ''))
                self.apartment_edit.setText(counterparty.get('apartment', ''))

            # Загрузка мест оказания услуг
            locations = self.db_manager.get_service_locations()
            for location in locations:
                self.location_combo.addItem(location['name'], location['id'])

            # Подключаем сигналы для обновления участков и улиц
            self.location_combo.currentIndexChanged.connect(self.on_location_changed)
            self.section_combo.currentIndexChanged.connect(self.on_section_changed)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            print(f"Подробности ошибки загрузки: {e}")

    def on_location_changed(self):
        """Обновление участков при изменении места услуг"""
        try:
            location_id = self.location_combo.currentData()
            if location_id:
                sections = self.db_manager.get_sections(location_id)
                self.section_combo.clear()
                for section in sections:
                    self.section_combo.addItem(section['name'], section['id'])
        except Exception as e:
            print(f"Ошибка загрузки участков: {e}")

    def on_section_changed(self):
        """Обновление улиц при изменении участка"""
        try:
            section_id = self.section_combo.currentData()
            if section_id:
                streets = self.db_manager.get_streets(section_id)
                self.street_combo.clear()
                for street in streets:
                    self.street_combo.addItem(street['name'], street['id'])
        except Exception as e:
            print(f"Ошибка загрузки улиц: {e}")

    def save_meter(self):
        """Сохранение счетчика"""
        try:
            if not self.water_supply_check.isChecked() and not self.water_disposal_check.isChecked():
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один вид услуг")
                return

            cursor = self.db_manager.conn.cursor()

            # Водоснабжение
            if self.water_supply_check.isChecked():
                cursor.execute('''
                    INSERT INTO meters (counterparty_id, service_type, subservice_type, 
                    object_name, initial_reading, current_reading, consumption)
                    VALUES (?, 'water_supply', 'water_pipeline', ?, ?, ?, ?)
                ''', (
                    self.counterparty_id,
                    self.object_edit.text(),
                    self.initial_reading_edit.value(),
                    self.current_reading_edit.value(),
                    self.current_reading_edit.value() - self.initial_reading_edit.value()
                ))

            # Водоотведение
            if self.water_disposal_check.isChecked():
                initial_reading = self.initial_reading_edit.value()
                current_reading = self.current_reading_edit.value()

                # Если связать услуги, используем те же показания
                if self.link_services_check.isChecked():
                    initial_reading = self.initial_reading_edit.value()
                    current_reading = self.current_reading_edit.value()

                cursor.execute('''
                    INSERT INTO meters (counterparty_id, service_type, subservice_type, 
                    object_name, initial_reading, current_reading, consumption)
                    VALUES (?, 'water_disposal', 'sewer', ?, ?, ?, ?)
                ''', (
                    self.counterparty_id,
                    self.object_edit.text(),
                    initial_reading,
                    current_reading,
                    current_reading - initial_reading
                ))

            self.db_manager.conn.commit()
            QMessageBox.information(self, "Успех", "Счетчик успешно добавлен")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")
            print(f"Подробности ошибки сохранения: {e}")
            import traceback
            traceback.print_exc()


class OperationsDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.init_ui()
        self.load_operations()

    def init_ui(self):
        self.setWindowTitle("Операции")
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout()

        # Таблица операций
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(7)
        self.operations_table.setHorizontalHeaderLabels([
            "Дата", "Вид услуг", "Было", "Стало", "Расход", "Объем", "Рейс"
        ])
        layout.addWidget(self.operations_table)

        # Кнопки
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_operations(self):
        """Загрузка операций"""
        try:
            # В реальной реализации здесь будет запрос к таблице операций
            # Покажем заглушку
            operations = [
                {"date": "2024-01-15", "service_type": "Водоснабжение", "old_value": 100, "new_value": 150,
                 "consumption": 50, "volume": 50, "trips": 1},
                {"date": "2024-01-10", "service_type": "Водоотведение", "old_value": 80, "new_value": 120,
                 "consumption": 40, "volume": 40, "trips": 1}
            ]

            self.operations_table.setRowCount(len(operations))
            for row, operation in enumerate(operations):
                self.operations_table.setItem(row, 0, QTableWidgetItem(operation['date']))
                self.operations_table.setItem(row, 1, QTableWidgetItem(operation['service_type']))
                self.operations_table.setItem(row, 2, QTableWidgetItem(str(operation['old_value'])))
                self.operations_table.setItem(row, 3, QTableWidgetItem(str(operation['new_value'])))
                self.operations_table.setItem(row, 4, QTableWidgetItem(str(operation['consumption'])))
                self.operations_table.setItem(row, 5, QTableWidgetItem(str(operation['volume'])))
                self.operations_table.setItem(row, 6, QTableWidgetItem(str(operation['trips'])))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки операций: {e}")


class ContractHistoryDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.init_ui()
        self.load_history()

    def init_ui(self):
        self.setWindowTitle("История изменения договора")
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()

        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Дата изменения", "Поле", "Было", "Стало", "Кто изменил", "Причина"
        ])
        layout.addWidget(self.history_table)

        # Кнопки
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_history(self):
        """Загрузка истории изменений договора"""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                SELECT ch.*, u.username 
                FROM change_history ch 
                LEFT JOIN users u ON ch.changed_by = u.id 
                WHERE ch.counterparty_id = ? AND ch.field_name IN ('contract_number', 'contract_date')
                ORDER BY ch.change_date DESC
            ''', (self.counterparty_id,))

            history = cursor.fetchall()

            self.history_table.setRowCount(len(history))
            for row, record in enumerate(history):
                self.history_table.setItem(row, 0, QTableWidgetItem(record['change_date']))
                self.history_table.setItem(row, 1, QTableWidgetItem(record.get('field_name', '')))
                self.history_table.setItem(row, 2, QTableWidgetItem(record.get('old_value', '')))
                self.history_table.setItem(row, 3, QTableWidgetItem(record.get('new_value', '')))
                self.history_table.setItem(row, 4, QTableWidgetItem(record.get('username', '')))
                self.history_table.setItem(row, 5, QTableWidgetItem(record.get('reason', '')))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки истории: {e}")


class ChangeHistoryDialog(QDialog):
    def __init__(self, counterparty_id, db_manager, parent=None):
        super().__init__(parent)
        self.counterparty_id = counterparty_id
        self.db_manager = db_manager
        self.init_ui()
        self.load_history()

    def init_ui(self):
        self.setWindowTitle("История изменений")
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()

        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Дата изменения", "Поле", "Было", "Стало", "Кто изменил", "Причина"
        ])
        layout.addWidget(self.history_table)

        # Кнопки
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_history(self):
        """Загрузка полной истории изменений"""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                SELECT ch.*, u.username 
                FROM change_history ch 
                LEFT JOIN users u ON ch.changed_by = u.id 
                WHERE ch.counterparty_id = ? 
                ORDER BY ch.change_date DESC
            ''', (self.counterparty_id,))

            history = cursor.fetchall()

            self.history_table.setRowCount(len(history))
            for row, record in enumerate(history):
                self.history_table.setItem(row, 0, QTableWidgetItem(record['change_date']))
                self.history_table.setItem(row, 1, QTableWidgetItem(record.get('field_name', '')))
                self.history_table.setItem(row, 2, QTableWidgetItem(record.get('old_value', '')))
                self.history_table.setItem(row, 3, QTableWidgetItem(record.get('new_value', '')))
                self.history_table.setItem(row, 4, QTableWidgetItem(record.get('username', '')))
                self.history_table.setItem(row, 5, QTableWidgetItem(record.get('reason', '')))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки истории: {e}")