import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QTextEdit, QMessageBox, QDialog, QFormLayout,
    QTabWidget, QHeaderView, QGroupBox, QDateEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon
from database_module import Database
from qr_generator import QRCodeDialog


class LoginWindow(QDialog):
    """Окно авторизации"""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.create_admin_user()
        self.init_ui()

    def create_admin_user(self):
        """Создание пользователя admin"""
        try:
            # Проверяем, есть ли уже admin
            user = self.db.authenticate_user('admin', 'admin')
            if not user:
                # Создаем админа
                self.db.add_user('Администратор', '00000000000', 'admin', 'admin', 'Оператор')
        except:
            pass

    def init_ui(self):
        """Инициализация интерфейса окна авторизации"""
        self.setWindowTitle('Авторизация - Система учёта заявок')
        self.setFixedSize(400, 520)

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton#EyeBtn {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                padding: 0px;
                min-width: 40px;
            }
            QPushButton#EyeBtn:hover {
                background-color: #e0e0e0;
            }
            QPushButton#LoginBtn {
                min-height: 50px;
                background-color: #4CAF50;
                color: white;
                border: 1px solid #3d8b40;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#LoginBtn:hover {
                background-color: #45a049;
            }
            QPushButton#LoginBtn:pressed {
                background-color: #3d8b40;
            }
            QPushButton#RegBtn {
                min-height: 50px;
                background-color: #2196F3;
                border: 1px solid #0b7dda;
                color: white;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#RegBtn:hover {
                background-color: #0b7dda;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        title = QLabel('Вход в систему')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Поле логина
        login_label = QLabel('Логин:')
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Введите логин')
        layout.addWidget(login_label)
        layout.addWidget(self.login_input)

        # Поле пароля
        password_label = QLabel('Пароль:')
        layout.addWidget(password_label)

        # Контейнер для пароля и кнопки "глаз"
        pass_layout = QHBoxLayout()
        pass_layout.setSpacing(5)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.login)

        # Кнопка "Глаз"
        self.show_pass_btn = QPushButton('*')
        self.show_pass_btn.setObjectName("EyeBtn")
        self.show_pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_pass_btn.setToolTip("Показать/Скрыть пароль")
        self.show_pass_btn.setFixedHeight(40)
        self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.show_pass_btn)

        layout.addLayout(pass_layout)

        layout.addSpacing(20)

        # Кнопка входа
        login_btn = QPushButton('Войти')
        login_btn.setObjectName("LoginBtn")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        # Кнопка регистрации
        register_btn = QPushButton('Регистрация')
        register_btn.setObjectName("RegBtn")
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.clicked.connect(self.show_register_dialog)
        layout.addWidget(register_btn)

        layout.addStretch()
        self.setLayout(layout)

    def toggle_password_visibility(self):
        """Переключение видимости пароля"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pass_btn.setText('X')
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pass_btn.setText('*')

    def login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля!')
            return

        user = self.db.authenticate_user(login, password)

        if user:
            self.current_user = user
            QMessageBox.information(
                self, 
                'Успешный вход', 
                f'Добро пожаловать, {user["fio"]}!\nРоль: {user["user_type"]}'
            )
            self.accept()
        else:
            QMessageBox.critical(self, 'Ошибка входа', 'Неверный логин или пароль!')
            self.password_input.clear()
            self.password_input.setFocus()

    def show_register_dialog(self):
        """Показать диалог регистрации"""
        dialog = RegisterDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self,
                'Успешная регистрация',
                'Вы успешно зарегистрированы!\nТеперь вы можете войти в систему.'
            )


class RegisterDialog(QDialog):
    """Диалог регистрации нового пользователя"""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса регистрации"""
        self.setWindowTitle('Регистрация нового пользователя')
        self.setFixedSize(450, 450)

        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: black;
                background-color: white;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)

        # Поля ввода
        self.fio_input = QLineEdit()
        self.fio_input.setPlaceholderText('Иванов Иван Иванович')

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('89991234567')

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('login')

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems([
            'Заказчик', 'Специалист', 'Оператор', 
            'Менеджер', 'Менеджер по качеству'
        ])

        layout.addRow('ФИО:', self.fio_input)
        layout.addRow('Телефон:', self.phone_input)
        layout.addRow('Логин:', self.login_input)
        layout.addRow('Пароль:', self.password_input)
        layout.addRow('Подтверждение:', self.password_confirm)
        layout.addRow('Роль:', self.user_type_combo)

        # Кнопки
        btn_layout = QHBoxLayout()
        register_btn = QPushButton('Зарегистрироваться')
        register_btn.clicked.connect(self.register)
        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def register(self):
        """Регистрация нового пользователя"""
        fio = self.fio_input.text().strip()
        phone = self.phone_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text()
        password_confirm = self.password_confirm.text()
        user_type = self.user_type_combo.currentText()

        # Валидация
        if not all([fio, phone, login, password]):
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля!')
            return

        if password != password_confirm:
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают!')
            return

        if len(password) < 4:
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен содержать минимум 4 символа!')
            return

        # Добавление пользователя
        user_id = self.db.add_user(fio, phone, login, password, user_type)

        if user_id:
            self.accept()
        else:
            QMessageBox.critical(
                self,
                'Ошибка',
                'Не удалось зарегистрировать пользователя.\nВозможно, такой логин уже существует.'
            )


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.current_user = user
        self.is_admin = user.get('login') == 'admin'
        self.init_ui()

    def init_ui(self):
        """Инициализация главного окна"""
        role_display = 'Администратор' if self.is_admin else self.current_user["user_type"]
        self.setWindowTitle(
            f'Система учёта заявок - {self.current_user["fio"]} ({role_display})'
        )
        self.setGeometry(100, 100, 1400, 800)

        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()

        header_layout = QHBoxLayout()

        header = QLabel(f'Пользователь: {self.current_user["fio"]} | Роль: {role_display}')
        header.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
        """)

        logout_btn = QPushButton('Выйти')
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)

        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #4CAF50;")
        header_inner_layout = QHBoxLayout()
        header_inner_layout.setContentsMargins(0, 0, 10, 0)
        header_inner_layout.addWidget(header)
        header_inner_layout.addStretch()
        header_inner_layout.addWidget(logout_btn)
        header_widget.setLayout(header_inner_layout)

        layout.addWidget(header_widget)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)

        self.create_requests_tab()
        self.create_my_requests_tab()
        
        if self.current_user['user_type'] == 'Специалист':
            self.create_available_requests_tab()

        if self.is_admin or self.current_user['user_type'] in ['Менеджер по качеству']:
            self.create_qr_code_tab()

        if self.is_admin or self.current_user['user_type'] in ['Менеджер', 'Оператор', 'Менеджер по качеству']:
            self.create_statistics_tab()

        if self.is_admin:
            self.create_users_tab()

        layout.addWidget(self.tabs)

        main_widget.setLayout(layout)

        if self.current_user['user_type'] in ['Заказчик', 'Специалист'] or self.is_admin:
            self.load_my_requests()

    def logout(self):
        """Выход из аккаунта"""
        reply = QMessageBox.question(
            self,
            'Выход',
            'Вы уверены, что хотите выйти из аккаунта?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            # Открываем окно авторизации заново
            login_window = LoginWindow()
            if login_window.exec() == QDialog.DialogCode.Accepted:
                user = login_window.current_user
                self.new_window = MainWindow(login_window.db, user)
                self.new_window.show()

    def create_users_tab(self):
        """Вкладка управления пользователями (только для админа)"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel('Управление пользователями')
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: black;")
        layout.addWidget(title)

        # Кнопка обновления
        refresh_btn = QPushButton('Обновить список')
        refresh_btn.clicked.connect(self.load_users)
        layout.addWidget(refresh_btn)

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(['ID', 'ФИО', 'Телефон', 'Логин', 'Роль'])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.users_table)

        # Кнопка удаления пользователя
        delete_btn = QPushButton('Удалить выбранного пользователя')
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_btn.clicked.connect(self.delete_user)
        layout.addWidget(delete_btn)

        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Пользователи')

        # Загрузка пользователей
        self.load_users()

    def load_users(self):
        """Загрузка списка пользователей"""
        users = self.db.get_all_users()

        self.users_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.get('user_id', ''))))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.get('fio', '')))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.get('phone', '')))
            self.users_table.setItem(row, 3, QTableWidgetItem(user.get('login', '')))
            self.users_table.setItem(row, 4, QTableWidgetItem(user.get('user_type', '')))

    def delete_user(self):
        """Удаление пользователя"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пользователя для удаления!')
            return

        user_id = int(self.users_table.item(selected_row, 0).text())
        user_login = self.users_table.item(selected_row, 3).text()

        if user_login == 'admin':
            QMessageBox.warning(self, 'Ошибка', 'Нельзя удалить администратора!')
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Вы уверены, что хотите удалить пользователя {user_login}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_user(user_id):
                QMessageBox.information(self, 'Успех', 'Пользователь удален!')
                self.load_users()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось удалить пользователя!')

    def create_requests_tab(self):
        """Вкладка со списком заявок"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Панель управления
        control_panel = QHBoxLayout()

        # Фильтр по статусу
        status_label = QLabel('Фильтр по статусу:')
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            'Все', 'Новая заявка', 'В процессе ремонта', 'Готова к выдаче'
        ])
        self.status_filter.currentTextChanged.connect(self.load_requests)

        # Поиск
        search_label = QLabel('Поиск:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Введите запрос для поиска...')
        self.search_input.setStyleSheet("color: black; background-color: white;")
        search_btn = QPushButton('Найти')
        search_btn.clicked.connect(self.search_requests)

        control_panel.addWidget(status_label)
        control_panel.addWidget(self.status_filter)
        control_panel.addWidget(search_label)
        control_panel.addWidget(self.search_input)
        control_panel.addWidget(search_btn)
        control_panel.addStretch()

        # Кнопка добавления заявки
        if self.is_admin or self.current_user['user_type'] in ['Заказчик', 'Оператор']:
            add_btn = QPushButton('Новая заявка')
            add_btn.clicked.connect(self.show_add_request_dialog)
            control_panel.addWidget(add_btn)

        # Кнопка обновления
        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self.load_requests)
        control_panel.addWidget(refresh_btn)

        layout.addLayout(control_panel)

        # Таблица заявок
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(8)
        self.requests_table.setHorizontalHeaderLabels([
            'ID', 'Дата', 'Тип техники', 'Модель', 'Проблема',
            'Статус', 'Клиент', 'Мастер'
        ])
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.requests_table.doubleClicked.connect(self.show_request_details)

        layout.addWidget(self.requests_table)

        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Все заявки')

        # Загрузка данных
        self.load_requests()

    def create_my_requests_tab(self):
        """Вкладка с моими заявками (для заказчиков и специалистов)"""
        if self.is_admin or self.current_user['user_type'] not in ['Заказчик', 'Специалист']:
            return

        tab = QWidget()
        layout = QVBoxLayout()

        if self.current_user['user_type'] == 'Заказчик':
            title = QLabel('Мои заявки')
        elif self.current_user['user_type'] == 'Специалист':
            title = QLabel('Мои задачи')
        else:
            title = QLabel('Все мои заявки')

        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        refresh_my_btn = QPushButton('Обновить')
        refresh_my_btn.clicked.connect(self.load_my_requests)
        layout.addWidget(refresh_my_btn)

        self.my_requests_table = QTableWidget()
        self.my_requests_table.setColumnCount(6)
        self.my_requests_table.setHorizontalHeaderLabels([
            'ID', 'Дата', 'Тип техники', 'Модель', 'Проблема', 'Статус'
        ])
        self.my_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.my_requests_table.doubleClicked.connect(self.show_my_request_details)

        layout.addWidget(self.my_requests_table)

        tab.setLayout(layout)

        if self.current_user['user_type'] == 'Заказчик':
            self.tabs.addTab(tab, 'Мои заявки')
        elif self.current_user['user_type'] == 'Специалист':
            self.tabs.addTab(tab, 'Мои задачи')
        else:
            self.tabs.addTab(tab, 'Мои заявки')

    def load_my_requests(self):
        """Загрузка заявок текущего пользователя"""
        if not hasattr(self, 'my_requests_table'):
            return

        all_requests = self.db.get_all_requests(None)

        # Фильтруем заявки по текущему пользователю
        my_requests = []
        for req in all_requests:
            if self.current_user['user_type'] == 'Заказчик':
                # Заказчик видит свои заявки (по client_name)
                if req.get('client_name') == self.current_user['fio']:
                    my_requests.append(req)
            elif self.current_user['user_type'] == 'Специалист':
                # Специалист видит назначенные ему заявки
                if req.get('master_name') == self.current_user['fio']:
                    my_requests.append(req)
            elif self.is_admin:
                # Админ видит все
                my_requests.append(req)

        self.my_requests_table.setRowCount(len(my_requests))

        for row, request in enumerate(my_requests):
            self.my_requests_table.setItem(row, 0, QTableWidgetItem(str(request['request_id'])))
            self.my_requests_table.setItem(row, 1, QTableWidgetItem(str(request['start_date'])))
            self.my_requests_table.setItem(row, 2, QTableWidgetItem(request['climate_tech_type']))
            self.my_requests_table.setItem(row, 3, QTableWidgetItem(request['climate_tech_model']))
            problem_short = request['problem_description'][:50] + '...' if len(request['problem_description']) > 50 else request['problem_description']
            self.my_requests_table.setItem(row, 4, QTableWidgetItem(problem_short))
            self.my_requests_table.setItem(row, 5, QTableWidgetItem(request['request_status']))

    def show_my_request_details(self):
        """Показать детали заявки из вкладки Мои заявки"""
        selected_row = self.my_requests_table.currentRow()
        if selected_row < 0:
            return

        request_id = int(self.my_requests_table.item(selected_row, 0).text())
        dialog = RequestDetailsDialog(self.db, self.current_user, request_id, self, is_admin=self.is_admin)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_my_requests()
            self.load_requests()

    def create_statistics_tab(self):
        """Вкладка со статистикой"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel('Статистика и аналитика')
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: black;")
        layout.addWidget(title)

        # Кнопка обновления статистики
        refresh_stats_btn = QPushButton('Обновить статистику')
        refresh_stats_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
        """)
        refresh_stats_btn.clicked.connect(self.load_statistics)
        layout.addWidget(refresh_stats_btn)

        # Область для отображения статистики
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                padding: 15px;
                background-color: #f9f9f9;
                color: black;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.stats_text)

        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Статистика')

        # Загрузка статистики
        self.load_statistics()

    def create_qr_code_tab(self):
        """Вкладка для генерации QR-кода"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel('Генерация QR-кода для оценки качества')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Ссылка на форму опроса
        link_label = QLabel('Ссылка на форму опроса:')
        self.link_input = QLineEdit(
            'https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=sf_link'
        )
        self.link_input.setStyleSheet("color: black; background-color: white;")
        layout.addWidget(link_label)
        layout.addWidget(self.link_input)

        # Кнопка генерации
        generate_btn = QPushButton('Сгенерировать QR-код')
        generate_btn.clicked.connect(self.show_qr_code_dialog)
        layout.addWidget(generate_btn)

        layout.addStretch(1)
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'QR-код')

    def show_qr_code_dialog(self):
        """Показать диалог с QR-кодом"""
        url = self.link_input.text()
        dialog = QRCodeDialog(None, self, url)
        dialog.exec()

    def load_requests(self):
        """Загрузка списка заявок"""
        status = self.status_filter.currentText()
        status = None if status == 'Все' else status

        requests = self.db.get_all_requests(status)

        self.requests_table.setRowCount(len(requests))

        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['request_id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(str(request['start_date'])))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['climate_tech_type']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(request['climate_tech_model']))
            problem_short = request['problem_description'][:50] + '...' if len(request['problem_description']) > 50 else request['problem_description']
            self.requests_table.setItem(row, 4, QTableWidgetItem(problem_short))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['request_status']))
            self.requests_table.setItem(row, 6, QTableWidgetItem(request['client_name']))
            self.requests_table.setItem(row, 7, QTableWidgetItem(request.get('master_name', '') or 'Не назначен'))

    def search_requests(self):
        """Поиск заявок"""
        search_term = self.search_input.text().strip()

        if not search_term:
            QMessageBox.warning(self, 'Предупреждение', 'Введите поисковый запрос!')
            return

        requests = self.db.search_requests(search_term)

        if not requests:
            QMessageBox.information(self, 'Результаты поиска', 'По вашему запросу ничего не найдено.')
            return

        self.requests_table.setRowCount(len(requests))

        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['request_id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(str(request['start_date'])))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['climate_tech_type']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(request['climate_tech_model']))
            problem_short = request['problem_description'][:50] + '...' if len(request['problem_description']) > 50 else request['problem_description']
            self.requests_table.setItem(row, 4, QTableWidgetItem(problem_short))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['request_status']))
            self.requests_table.setItem(row, 6, QTableWidgetItem(request['client_name']))
            self.requests_table.setItem(row, 7, QTableWidgetItem(request.get('master_name', '') or ''))

    def show_add_request_dialog(self):
        """Показать диалог добавления заявки"""
        dialog = AddRequestDialog(self.db, self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_requests()
            QMessageBox.information(self, 'Успех', 'Заявка успешно создана!')

    def show_request_details(self):
        """Показать детали заявки"""
        selected_row = self.requests_table.currentRow()
        if selected_row < 0:
            return

        request_id = int(self.requests_table.item(selected_row, 0).text())
        dialog = RequestDetailsDialog(self.db, self.current_user, request_id, self, is_admin=self.is_admin)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_requests()
            if hasattr(self, 'my_requests_table'):
                self.load_my_requests()

    def load_statistics(self):
        """Загрузка статистики"""
        if not hasattr(self, 'stats_text'):
            return
            
        stats = self.db.get_statistics()

        text = f"""
        <div style="color: black;">
            <h2 style="color: #4CAF50;">Общая статистика</h2>

            <p style="color: black;"><b>Всего заявок:</b> {stats.get('total_requests', 0)}</p>
            <p style="color: black;"><b>Завершённых заявок:</b> {stats.get('completed_requests', 0)}</p>
            <p style="color: black;"><b>Среднее время выполнения:</b> {stats.get('avg_completion_time', 0):.1f} дней</p>

            <h3 style="color: #2196F3;">Статистика по типам оборудования:</h3>
        """

        for item in stats.get('by_tech_type', []):
            text += f"<p style='color: black;'>- {item['type']}: <b>{item['count']}</b> заявок</p>"

        text += "<h3 style='color: #FF9800;'>Статистика по статусам:</h3>"

        for item in stats.get('by_status', []):
            text += f"<p style='color: black;'>- {item['status']}: <b>{item['count']}</b> заявок</p>"

        text += "</div>"

        self.stats_text.setHtml(text)

    def create_available_requests_tab(self):
        """Вкладка с доступными заявками для специалистов"""
        tab = QWidget()
        layout = QVBoxLayout()

        title = QLabel('Доступные заявки (без назначенного специалиста)')
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: black;")
        layout.addWidget(title)

        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self.load_available_requests)
        layout.addWidget(refresh_btn)

        self.available_requests_table = QTableWidget()
        self.available_requests_table.setColumnCount(6)
        self.available_requests_table.setHorizontalHeaderLabels([
            'ID', 'Дата', 'Тип техники', 'Модель', 'Проблема', 'Статус'
        ])
        self.available_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.available_requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.available_requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.available_requests_table)

        # Кнопка "Откликнуться на заявку"
        respond_btn = QPushButton('Откликнуться на заявку')
        respond_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        respond_btn.clicked.connect(self.respond_to_request)
        layout.addWidget(respond_btn)

        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Доступные заявки')

        self.load_available_requests()

    def load_available_requests(self):
        """Загрузка заявок без назначенного специалиста"""
        if not hasattr(self, 'available_requests_table'):
            return

        all_requests = self.db.get_all_requests(None)

        # Фильтруем заявки без назначенного мастера
        available = [
            req for req in all_requests 
            if not req.get('master_name') or req.get('master_name') == 'Не назначен'
        ]

        self.available_requests_table.setRowCount(len(available))

        for row, request in enumerate(available):
            self.available_requests_table.setItem(row, 0, QTableWidgetItem(str(request['request_id'])))
            self.available_requests_table.setItem(row, 1, QTableWidgetItem(str(request['start_date'])))
            self.available_requests_table.setItem(row, 2, QTableWidgetItem(request['climate_tech_type']))
            self.available_requests_table.setItem(row, 3, QTableWidgetItem(request['climate_tech_model']))
            problem_short = request['problem_description'][:50] + '...' if len(request['problem_description']) > 50 else request['problem_description']
            self.available_requests_table.setItem(row, 4, QTableWidgetItem(problem_short))
            self.available_requests_table.setItem(row, 5, QTableWidgetItem(request['request_status']))

    def respond_to_request(self):
        """Специалист откликается на заявку"""
        selected_row = self.available_requests_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите заявку для отклика!')
            return

        request_id = int(self.available_requests_table.item(selected_row, 0).text())

        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Вы хотите взять заявку #{request_id} в работу?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Используем метод assign_master из database_module
            success = self.db.assign_master(request_id, self.current_user['user_id'])
            if success:
                QMessageBox.information(self, 'Успех', f'Вы успешно взяли заявку #{request_id} в работу!')
                self.load_available_requests()
                self.load_my_requests()
                self.load_requests()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось взять заявку!')


class AddRequestDialog(QDialog):
    """Диалог добавления новой заявки"""

    def __init__(self, db, user, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_user = user
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('Новая заявка')
        self.setFixedSize(500, 400)

        layout = QFormLayout()

        # Поля ввода
        self.tech_type_combo = QComboBox()
        self.tech_type_combo.addItems([
            'Кондиционер', 'Увлажнитель воздуха', 'Сушилка для рук', 
            'Вентиляция', 'Отопление'
        ])

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText('Например: Samsung AR09')
        self.model_input.setStyleSheet("color: black; background-color: white;")

        self.problem_input = QTextEdit()
        self.problem_input.setPlaceholderText('Опишите проблему подробно...')
        self.problem_input.setMaximumHeight(150)
        self.problem_input.setStyleSheet("color: black; background-color: white;")

        layout.addRow('Тип оборудования:', self.tech_type_combo)
        layout.addRow('Модель:', self.model_input)
        layout.addRow('Описание проблемы:', self.problem_input)

        # Кнопки
        btn_layout = QHBoxLayout()
        create_btn = QPushButton('Создать заявку')
        create_btn.clicked.connect(self.create_request)
        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def create_request(self):
        """Создание заявки"""
        tech_type = self.tech_type_combo.currentText()
        model = self.model_input.text().strip()
        problem = self.problem_input.toPlainText().strip()

        if not model or not problem:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля!')
            return

        request_id = self.db.add_request(
            tech_type,
            model,
            problem,
            self.current_user['user_id']
        )

        if request_id:
            self.accept()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось создать заявку!')


class RequestDetailsDialog(QDialog):
    """Диалог с деталями заявки"""

    def __init__(self, db, user, request_id, parent=None, is_admin=False):
        super().__init__(parent)
        self.db = db
        self.current_user = user
        self.request_id = request_id
        self.is_admin = is_admin
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(f'Детали заявки #{self.request_id}')
        self.setFixedSize(500, 650)

        layout = QFormLayout()

        # Получаем данные заявки через метод get_request_by_id
        request_data = self.db.get_request_by_id(self.request_id)
        
        # Если метод не нашел заявку, ищем вручную
        if not request_data:
            all_requests = self.db.get_all_requests(None)
            for req in all_requests:
                if req['request_id'] == self.request_id:
                    request_data = req
                    break

        if not request_data:
            QMessageBox.warning(self, 'Ошибка', 'Заявка не найдена!')
            self.reject()
            return
        
        self.request_data = request_data

        # Поля для отображения
        self.type_label = QLabel(request_data.get('climate_tech_type', ''))
        self.model_label = QLabel(request_data.get('climate_tech_model', ''))
        self.problem_text = QTextEdit()
        self.problem_text.setPlainText(request_data.get('problem_description', ''))
        self.problem_text.setReadOnly(True)
        self.problem_text.setStyleSheet("color: black; background-color: #f0f0f0;")

        self.status_combo = QComboBox()
        self.status_combo.addItems([
            'Новая заявка', 'В процессе ремонта', 'Готова к выдаче'
        ])
        self.status_combo.setCurrentText(request_data.get('request_status', 'Новая заявка'))

        if not self.is_admin and self.current_user['user_type'] == 'Заказчик':
            self.status_combo.setEnabled(False)

        layout.addRow('Тип:', self.type_label)
        layout.addRow('Модель:', self.model_label)
        layout.addRow('Описание:', self.problem_text)
        layout.addRow('Статус:', self.status_combo)

        client_label = QLabel(request_data.get('client_name', 'Не указан'))
        layout.addRow('Клиент:', client_label)
        
        can_assign_master = self.is_admin or self.current_user['user_type'] in ['Менеджер', 'Оператор']
        
        if can_assign_master:
            self.master_combo = QComboBox()
            self.master_combo.addItem('Не назначен', None)
            
            # Получаем список специалистов через метод get_specialists
            specialists = self.db.get_specialists()
            for spec in specialists:
                self.master_combo.addItem(spec['fio'], spec['user_id'])
            
            # Устанавливаем текущего мастера если есть
            current_master = request_data.get('master_name')
            if current_master and current_master != 'Не назначен':
                index = self.master_combo.findText(current_master)
                if index >= 0:
                    self.master_combo.setCurrentIndex(index)
            
            layout.addRow('Специалист:', self.master_combo)
        else:
            master_label = QLabel(request_data.get('master_name', 'Не назначен') or 'Не назначен')
            layout.addRow('Мастер:', master_label)

        save_btn = QPushButton('Сохранить изменения')
        save_btn.clicked.connect(self.save_changes)

        cancel_btn = QPushButton('Закрыть')
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        if self.is_admin or self.current_user['user_type'] not in ['Заказчик']:
            btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def save_changes(self):
        """Сохранение изменений"""
        new_status = self.status_combo.currentText()
        
        can_assign_master = self.is_admin or self.current_user['user_type'] in ['Менеджер', 'Оператор']
        
        try:
            # Сначала назначаем мастера (до изменения статуса!)
            if can_assign_master and hasattr(self, 'master_combo'):
                master_id = self.master_combo.currentData()
                if master_id:
                    success = self.db.assign_master(self.request_id, master_id)
                    if not success:
                        QMessageBox.warning(
                            self, 
                            'Предупреждение', 
                            'Не удалось назначить специалиста.\n'
                            'Возможно, заявка уже завершена.'
                        )
            
            # Потом обновляем статус
            self.db.update_request_status(self.request_id, new_status)
            
            QMessageBox.information(self, 'Успех', 'Заявка обновлена!')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось обновить заявку: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Запуск с окна авторизации
    login_window = LoginWindow()

    if login_window.exec() == QDialog.DialogCode.Accepted:
        user = login_window.current_user
        window = MainWindow(login_window.db, user)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)