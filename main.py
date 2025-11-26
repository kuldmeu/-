import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from modules.main_window import MainWindow
from modules.auth import LoginDialog
from modules.database import DatabaseManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("База данных контрагентов")
    app.setApplicationVersion("1.0")

    # Настройки приложения
    settings = QSettings("YourCompany", "CounterpartyDB")

    # Создание директории data если не существует
    if not os.path.exists('data'):
        os.makedirs('data')

    # Инициализация базы данных
    db_manager = DatabaseManager()

    # Окно авторизации
    login_dialog = LoginDialog(db_manager)
    if login_dialog.exec_() == LoginDialog.Accepted:
        user_data = login_dialog.get_user_data()

        # Главное окно
        window = MainWindow(db_manager, user_data, settings)
        window.show()

        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()