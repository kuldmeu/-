import hashlib
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QCheckBox,
                             QMessageBox, QTableWidget, QTableWidgetItem,
                             QTabWidget, QWidget, QHeaderView, QGroupBox,
                             QFormLayout)
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Авторизация в системе")
        self.setFixedSize(350, 250)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("База данных контрагентов")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Поля ввода
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите имя пользователя")
        form_layout.addRow("Имя пользователя:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("Вход")
        login_btn.clicked.connect(self.authenticate)
        login_btn.setDefault(True)
        
        cancel_btn = QPushButton("Выход")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Подсказка
        hint_label = QLabel("По умолчанию: admin / admin123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 10px;")
        layout.addWidget(hint_label)
        
        self.setLayout(layout)
    
    def authenticate(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        self.user_data = self.db_manager.authenticate_user(username, password)
        
        if self.user_data:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def get_user_data(self):
        return self.user_data

class ChangePasswordDialog(QDialog):
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Смена пароля")
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Старый пароль:", self.old_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Новый пароль:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Подтвердите пароль:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.change_password)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def change_password(self):
        old_password = self.old_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        if not old_password or not new_password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        
        if len(new_password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 4 символа")
            return
        
        if self.db_manager.change_password(self.user_id, old_password, new_password):
            QMessageBox.information(self, "Успех", "Пароль успешно изменен")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный старый пароль")

class UserManagementDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        self.setWindowTitle("Управление пользователями")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Имя пользователя", "Роль", "Активен", "Дата создания", "Последний вход"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.users_table)
        
        # Группа управления
        management_group = QGroupBox("Действия")
        management_layout = QHBoxLayout(management_group)
        
        add_user_btn = QPushButton("Добавить пользователя")
        add_user_btn.clicked.connect(self.add_user)
        
        edit_user_btn = QPushButton("Редактировать")
        edit_user_btn.clicked.connect(self.edit_user)
        
        toggle_user_btn = QPushButton("Активировать/Деактивировать")
        toggle_user_btn.clicked.connect(self.toggle_user)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_users)
        
        management_layout.addWidget(add_user_btn)
        management_layout.addWidget(edit_user_btn)
        management_layout.addWidget(toggle_user_btn)
        management_layout.addStretch()
        management_layout.addWidget(refresh_btn)
        
        layout.addWidget(management_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_users(self):
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                SELECT id, username, role, is_active, created_date, last_login 
                FROM users ORDER BY username
            ''')
            users = cursor.fetchall()
            
            self.users_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['role']))
                self.users_table.setItem(row, 3, QTableWidgetItem("Да" if user['is_active'] else "Нет"))
                self.users_table.setItem(row, 4, QTableWidgetItem(user['created_date']))
                self.users_table.setItem(row, 5, QTableWidgetItem(user['last_login'] or ''))
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки пользователей: {e}")
    
    def add_user(self):
        dialog = AddUserDialog(self.db_manager, self)
        if dialog.exec_():
            self.load_users()
    
    def edit_user(self):
        selected = self.users_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для редактирования")
            return
        
        user_id = int(self.users_table.item(selected, 0).text())
        # Реализация редактирования пользователя...
    
    def toggle_user(self):
        selected = self.users_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя")
            return
        
        user_id = int(self.users_table.item(selected, 0).text())
        username = self.users_table.item(selected, 1).text()
        current_status = self.users_table.item(selected, 3).text() == "Да"
        
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                UPDATE users SET is_active = ? WHERE id = ?
            ''', (not current_status, user_id))
            self.db_manager.conn.commit()
            
            self.load_users()
            QMessageBox.information(self, "Успех", f"Статус пользователя {username} изменен")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка изменения статуса: {e}")

class AddUserDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Добавить пользователя")
        self.setFixedSize(300, 250)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        form_layout.addRow("Имя пользователя:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_edit)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "user", "operator"])
        form_layout.addRow("Роль:", self.role_combo)
        
        self.is_active_check = QCheckBox()
        self.is_active_check.setChecked(True)
        form_layout.addRow("Активен:", self.is_active_check)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_user)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_user(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        role = self.role_combo.currentText()
        is_active = self.is_active_check.isChecked()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        try:
            cursor = self.db_manager.conn.cursor()
            
            # Проверка существования пользователя
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует")
                return
            
            # Создание пользователя
            import hashlib
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, is_active)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, role, is_active))
            
            self.db_manager.conn.commit()
            QMessageBox.information(self, "Успех", "Пользователь успешно создан")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания пользователя: {e}")