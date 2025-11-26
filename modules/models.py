from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QColor, QFont


class CounterpartyTableModel(QAbstractTableModel):
    def __init__(self, data, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._data = data  # переименовали внутреннюю переменную
        self._headers = [
            'ID', 'Категория', 'ИИН/БИН', 'Контрагент', 'Телефон',
            'Номер договора', 'Дата договора', 'Статус договора',
            'Наличие договора', 'Место услуг', 'Участок', 'Улица',
            'Дом', 'Квартира', 'Примечание'
        ]
        self._column_keys = [
            'custom_id', 'category_name', 'iin_bin', 'name', 'phone',
            'contract_number', 'contract_date', 'contract_status',
            'contract_availability', 'service_location_name', 'section_name',
            'street_name', 'house', 'apartment', 'notes'
        ]

    # ЗАМЕНА: свойство data -> counterparty_data
    @property
    def counterparty_data(self):
        return self._data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            value = self._data[row].get(self._column_keys[col], '')
            return str(value) if value is not None else ''

        elif role == Qt.BackgroundRole:
            # Подсветка строк в зависимости от статуса
            status = self._data[row].get('contract_status')
            availability = self._data[row].get('contract_availability')

            if status == 'terminated':
                return QColor(255, 230, 230)  # Светло-красный для расторгнутых
            elif status == 'active':
                return QColor(230, 255, 230)  # Светло-зеленый для активных
            elif availability == 'Есть в наличии':
                return QColor(230, 240, 255)  # Светло-синий для наличия договора

        elif role == Qt.ForegroundRole:
            status = self._data[row].get('contract_status')
            if status == 'terminated':
                return QColor(139, 0, 0)  # Темно-красный текст

        elif role == Qt.FontRole:
            font = QFont()
            if self._data[row].get('contract_status') == 'active':
                font.setBold(True)
            return font

        elif role == Qt.TextAlignmentRole:
            if col in [0, 5, 6]:  # ID, номер договора, дата договора
                return Qt.AlignCenter
            return Qt.AlignLeft

        elif role == Qt.ToolTipRole:
            # Всплывающая подсказка с полной информацией
            counterparty = self._data[row]
            tooltip = f"""
            Контрагент: {counterparty.get('name', '')}
            ИИН/БИН: {counterparty.get('iin_bin', '')}
            Телефон: {counterparty.get('phone', '')}
            Договор: {counterparty.get('contract_number', '')} от {counterparty.get('contract_date', '')}
            Статус: {counterparty.get('contract_status', '')}
            Примечание: {counterparty.get('notes', '')}
            """
            return tooltip.strip()

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]

        if orientation == Qt.Horizontal and role == Qt.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        return None

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    def get_counterparty(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def sort(self, column, order=Qt.AscendingOrder):
        """Сортировка данных"""
        self.layoutAboutToBeChanged.emit()

        reverse = order == Qt.DescendingOrder
        key = self._column_keys[column]

        self._data.sort(key=lambda x: x.get(key, ''), reverse=reverse)

        self.layoutChanged.emit()