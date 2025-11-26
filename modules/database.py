import sqlite3
import json
import shutil
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class DatabaseManager(QObject):
    connection_changed = pyqtSignal()
    data_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.conn = None
        self.connect_database()
        self.init_database()

    def connect_database(self):
        """Подключение к базе данных"""
        try:
            self.conn = sqlite3.connect('data/database.db', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")

    def init_database(self):
        """Инициализация таблиц базы данных"""
        try:
            cursor = self.conn.cursor()

            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    permissions TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            # Таблица операций
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    counterparty_id INTEGER,
                    service_type TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    old_value REAL,
                    new_value REAL,
                    consumption REAL,
                    volume REAL,
                    trips INTEGER,
                    operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (counterparty_id) REFERENCES counterparties (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')

            # Таблица категорий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            ''')

            # Таблица мест оказания услуг
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            ''')

            # Таблица участков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    service_location_id INTEGER,
                    FOREIGN KEY (service_location_id) REFERENCES service_locations (id),
                    UNIQUE(name, service_location_id)
                )
            ''')

            # Таблица улиц
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS streets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    section_id INTEGER,
                    FOREIGN KEY (section_id) REFERENCES sections (id),
                    UNIQUE(name, section_id)
                )
            ''')

            # Таблица контрагентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS counterparties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    custom_id TEXT UNIQUE,
                    category_id INTEGER,
                    iin_bin TEXT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    contract_number TEXT,
                    contract_date DATE,
                    contract_status TEXT DEFAULT 'active',
                    contract_availability TEXT DEFAULT 'Нет в наличии',
                    notes TEXT,
                    service_location_id INTEGER,
                    section_id INTEGER,
                    street_id INTEGER,
                    house TEXT,
                    apartment TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    FOREIGN KEY (service_location_id) REFERENCES service_locations (id),
                    FOREIGN KEY (section_id) REFERENCES sections (id),
                    FOREIGN KEY (street_id) REFERENCES streets (id)
                )
            ''')

            # Таблица тарифов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tariffs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    counterparty_id INTEGER,
                    service_type TEXT NOT NULL,
                    subservice_type TEXT NOT NULL,
                    rate REAL NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (counterparty_id) REFERENCES counterparties (id)
                )
            ''')

            # Таблица плановых объемов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS planned_volumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    counterparty_id INTEGER,
                    service_type TEXT NOT NULL,
                    subservice_type TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    january REAL DEFAULT 0,
                    february REAL DEFAULT 0,
                    march REAL DEFAULT 0,
                    april REAL DEFAULT 0,
                    may REAL DEFAULT 0,
                    june REAL DEFAULT 0,
                    july REAL DEFAULT 0,
                    august REAL DEFAULT 0,
                    september REAL DEFAULT 0,
                    october REAL DEFAULT 0,
                    november REAL DEFAULT 0,
                    december REAL DEFAULT 0,
                    FOREIGN KEY (counterparty_id) REFERENCES counterparties (id)
                )
            ''')

            # Таблица счетчиков
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    counterparty_id INTEGER,
                    service_type TEXT NOT NULL,
                    subservice_type TEXT NOT NULL,
                    object_name TEXT,
                    initial_reading REAL,
                    current_reading REAL,
                    consumption REAL,
                    vehicle_number TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (counterparty_id) REFERENCES counterparties (id)
                )
            ''')

            # Таблица истории изменений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS change_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    counterparty_id INTEGER,
                    changed_by INTEGER,
                    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    reason TEXT,
                    FOREIGN KEY (counterparty_id) REFERENCES counterparties (id),
                    FOREIGN KEY (changed_by) REFERENCES users (id)
                )
            ''')

            # Создание администратора по умолчанию
            import hashlib
            password_hash = hashlib.md5('admin123'.encode()).hexdigest()

            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role, permissions)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'admin', json.dumps({'all': True})))

            # Создание тестовых категорий
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name) VALUES 
                ('Физическое лицо'), ('Юридическое лицо'), ('Индивидуальный предприниматель')
            ''')

            self.conn.commit()

        except Exception as e:
            print(f"Ошибка инициализации БД: {e}")

    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        try:
            import hashlib
            password_hash = hashlib.md5(password.encode()).hexdigest()

            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, username, role, is_active FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))

            user = cursor.fetchone()

            if user:
                # Обновление времени последнего входа
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user['id'],))
                self.conn.commit()

                return dict(user)

            return None

        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return None

    def change_password(self, user_id, old_password, new_password):
        """Смена пароля"""
        try:
            import hashlib
            old_password_hash = hashlib.md5(old_password.encode()).hexdigest()
            new_password_hash = hashlib.md5(new_password.encode()).hexdigest()

            cursor = self.conn.cursor()

            # Проверка старого пароля
            cursor.execute('''
                SELECT id FROM users WHERE id = ? AND password_hash = ?
            ''', (user_id, old_password_hash))

            if not cursor.fetchone():
                return False

            # Обновление пароля
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE id = ?
            ''', (new_password_hash, user_id))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Ошибка смены пароля: {e}")
            return False

    def get_counterparties(self, filters=None):
        """Получение списка контрагентов с фильтрами"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT c.*, cat.name as category_name, sl.name as service_location_name,
                       sec.name as section_name, st.name as street_name
                FROM counterparties c
                LEFT JOIN categories cat ON c.category_id = cat.id
                LEFT JOIN service_locations sl ON c.service_location_id = sl.id
                LEFT JOIN sections sec ON c.section_id = sec.id
                LEFT JOIN streets st ON c.street_id = st.id
            '''

            params = []
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    if value:
                        if key in ['id', 'category_id', 'service_location_id', 'section_id']:
                            where_clauses.append(f"c.{key} = ?")
                            params.append(value)
                        else:
                            where_clauses.append(f"c.{key} LIKE ?")
                            params.append(f"%{value}%")

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY c.name"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"Ошибка получения контрагентов: {e}")
            return []

    def add_counterparty(self, data, user_id):
        """Добавление нового контрагента"""
        try:
            cursor = self.conn.cursor()

            # Вставка основной информации
            cursor.execute('''
                INSERT INTO counterparties (
                    custom_id, category_id, iin_bin, name, phone, contract_number, contract_date,
                    contract_status, contract_availability, notes, service_location_id,
                    section_id, street_id, house, apartment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['custom_id'], data['category_id'], data['iin_bin'], data['name'], data['phone'],
                data['contract_number'], data['contract_date'], data['contract_status'],
                data['contract_availability'], data['notes'], data['service_location_id'],
                data['section_id'], data['street_id'], data['house'], data['apartment']
            ))

            counterparty_id = cursor.lastrowid

            # Вставка тарифов
            for tariff in data.get('tariffs', []):
                cursor.execute('''
                    INSERT INTO tariffs (counterparty_id, service_type, subservice_type, rate)
                    VALUES (?, ?, ?, ?)
                ''', (counterparty_id, tariff['service_type'], tariff['subservice_type'], tariff['rate']))

            # Вставка плановых объемов
            for volume in data.get('planned_volumes', []):
                cursor.execute('''
                    INSERT INTO planned_volumes (
                        counterparty_id, service_type, subservice_type, year,
                        january, february, march, april, may, june,
                        july, august, september, october, november, december
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    counterparty_id, volume['service_type'], volume['subservice_type'], volume['year'],
                    volume.get('январь', 0), volume.get('февраль', 0), volume.get('март', 0),
                    volume.get('апрель', 0), volume.get('май', 0), volume.get('июнь', 0),
                    volume.get('июль', 0), volume.get('август', 0), volume.get('сентябрь', 0),
                    volume.get('октябрь', 0), volume.get('ноябрь', 0), volume.get('декабрь', 0)
                ))

            # Запись в историю изменений
            cursor.execute('''
                INSERT INTO change_history (counterparty_id, changed_by, reason)
                VALUES (?, ?, ?)
            ''', (counterparty_id, user_id, "Создание контрагента"))

            self.conn.commit()
            self.data_updated.emit()
            return counterparty_id

        except Exception as e:
            print(f"Ошибка добавления контрагента: {e}")
            return None

    def update_counterparty(self, counterparty_id, data, user_id, reason):
        """Обновление контрагента"""
        try:
            cursor = self.conn.cursor()

            # Обновление основной информации
            cursor.execute('''
                UPDATE counterparties SET
                    custom_id = ?, category_id = ?, iin_bin = ?, name = ?, phone = ?,
                    contract_number = ?, contract_date = ?, contract_status = ?,
                    contract_availability = ?, notes = ?, service_location_id = ?,
                    section_id = ?, street_id = ?, house = ?, apartment = ?,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data['custom_id'], data['category_id'], data['iin_bin'], data['name'], data['phone'],
                data['contract_number'], data['contract_date'], data['contract_status'],
                data['contract_availability'], data['notes'], data['service_location_id'],
                data['section_id'], data['street_id'], data['house'], data['apartment'],
                counterparty_id
            ))

            # Удаление старых тарифов и плановых объемов
            cursor.execute('DELETE FROM tariffs WHERE counterparty_id = ?', (counterparty_id,))
            cursor.execute('DELETE FROM planned_volumes WHERE counterparty_id = ?', (counterparty_id,))

            # Вставка новых тарифов
            for tariff in data.get('tariffs', []):
                cursor.execute('''
                    INSERT INTO tariffs (counterparty_id, service_type, subservice_type, rate)
                    VALUES (?, ?, ?, ?)
                ''', (counterparty_id, tariff['service_type'], tariff['subservice_type'], tariff['rate']))

            # Вставка новых плановых объемов
            for volume in data.get('planned_volumes', []):
                cursor.execute('''
                    INSERT INTO planned_volumes (
                        counterparty_id, service_type, subservice_type, year,
                        january, february, march, april, may, june,
                        july, august, september, october, november, december
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    counterparty_id, volume['service_type'], volume['subservice_type'], volume['year'],
                    volume.get('январь', 0), volume.get('февраль', 0), volume.get('март', 0),
                    volume.get('апрель', 0), volume.get('май', 0), volume.get('июнь', 0),
                    volume.get('июль', 0), volume.get('август', 0), volume.get('сентябрь', 0),
                    volume.get('октябрь', 0), volume.get('ноябрь', 0), volume.get('декабрь', 0)
                ))

            # Запись в историю изменений
            cursor.execute('''
                INSERT INTO change_history (counterparty_id, changed_by, reason)
                VALUES (?, ?, ?)
            ''', (counterparty_id, user_id, reason))

            self.conn.commit()
            self.data_updated.emit()
            return True

        except Exception as e:
            print(f"Ошибка обновления контрагента: {e}")
            return False

    def get_categories(self):
        """Получение списка категорий"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []

    def get_service_locations(self):
        """Получение списка мест оказания услуг"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM service_locations ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка получения мест услуг: {e}")
            return []

    def get_sections(self, location_id):
        """Получение участков по месту оказания услуг"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM sections WHERE service_location_id = ? ORDER BY name", (location_id,))
            sections = cursor.fetchall()
            return [dict(section) for section in sections]
        except Exception as e:
            print(f"Ошибка получения участков: {e}")
            return []

    def get_streets(self, section_id):
        """Получение улиц по участку"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM streets WHERE section_id = ? ORDER BY name", (section_id,))
            streets = cursor.fetchall()
            return [dict(street) for street in streets]
        except Exception as e:
            print(f"Ошибка получения улиц: {e}")
            return []

    def get_statistics(self):
        """Получение статистики по договорам"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN contract_status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN contract_status = 'terminated' THEN 1 ELSE 0 END) as terminated,
                    SUM(CASE WHEN contract_availability = 'Есть в наличии' THEN 1 ELSE 0 END) as available,
                    SUM(CASE WHEN contract_availability = 'Нет в наличии' THEN 1 ELSE 0 END) as not_available
                FROM counterparties
            ''')
            result = cursor.fetchone()
            return dict(result) if result else {}
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}

    def backup_database(self, backup_path):
        """Создание резервной копии базы данных"""
        try:
            # Создание директории если не существует
            import os
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            shutil.copy2('data/database.db', backup_path)
            return True
        except Exception as e:
            print(f"Ошибка резервного копирования: {e}")
            return False

    def restore_database(self, backup_path):
        """Восстановление базы данных из резервной копии"""
        try:
            shutil.copy2(backup_path, 'data/database.db')
            self.connect_database()
            self.connection_changed.emit()
            self.data_updated.emit()
            return True
        except Exception as e:
            print(f"Ошибка восстановления: {e}")
            return False