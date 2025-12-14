import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QTextEdit, QMessageBox, QDialog, QFormLayout,
    QTabWidget, QHeaderView, QGroupBox, QDateEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon
from database import Database
from qr_generator import QRCodeDialog

class LoginWindow(QDialog):
    """Окно авторизации"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса окна авторизации"""
        self.setWindowTitle('Авторизация - Система учёта заявок')
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel('🔐 Вход в систему')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Поле логина
        login_label = QLabel('Логин:')
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Введите логин')
        layout.addWidget(login_label)
        layout.addWidget(self.login_input)
        
        # Поле пароля
        password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Кнопка входа
        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        # Кнопка регистрации
        register_btn = QPushButton('Регистрация')
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        register_btn.clicked.connect(self.show_register_dialog)
        layout.addWidget(register_btn)
        
        self.setLayout(layout)
    
    def login(self):
        """Обработка входа в систему"""
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
            QMessageBox.critical(
                self, 
                'Ошибка входа', 
                'Неверный логин или пароль!\nПроверьте правильность введённых данных.'
            )
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
        self.user_type_combo.addItems(['Заказчик', 'Специалист', 'Оператор', 'Менеджер'])
        
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
        self.init_ui()
    
    def init_ui(self):
        """Инициализация главного окна"""
        self.setWindowTitle(f'Система учёта заявок - {self.current_user["fio"]} ({self.current_user["user_type"]})')
        self.setGeometry(100, 100, 1400, 800)
        
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel(f'👤 {self.current_user["fio"]} | Роль: {self.current_user["user_type"]}')
        header.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(header)
        
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
        
        # Добавление вкладок в зависимости от роли
        self.create_requests_tab()
        self.create_my_requests_tab()
        
        if self.current_user['user_type'] in ['Менеджер', 'Оператор']:
            self.create_statistics_tab()
        
        layout.addWidget(self.tabs)
        
        main_widget.setLayout(layout)
    
    def create_requests_tab(self):
        """Вкладка со списком заявок"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Панель управления
        control_panel = QHBoxLayout()
        
        # Фильтр по статусу
        status_label = QLabel('Фильтр по статусу:')
        self.status_filter = QComboBox()
        self.status_filter.addItems(['Все', 'Новая заявка', 'В процессе ремонта', 'Готова к выдаче'])
        self.status_filter.currentTextChanged.connect(self.load_requests)
        
        # Поиск
        search_label = QLabel('Поиск:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Введите запрос для поиска...')
        search_btn = QPushButton('🔍 Найти')
        search_btn.clicked.connect(self.search_requests)
        
        control_panel.addWidget(status_label)
        control_panel.addWidget(self.status_filter)
        control_panel.addWidget(search_label)
        control_panel.addWidget(self.search_input)
        control_panel.addWidget(search_btn)
        control_panel.addStretch()
        
        # Кнопка добавления заявки
        if self.current_user['user_type'] in ['Заказчик', 'Оператор']:
            add_btn = QPushButton('➕ Новая заявка')
            add_btn.clicked.connect(self.show_add_request_dialog)
            control_panel.addWidget(add_btn)
        
        # Кнопка обновления
        refresh_btn = QPushButton('🔄 Обновить')
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
        self.tabs.addTab(tab, '📋 Все заявки')
        
        # Загрузка данных
        self.load_requests()
    
    def create_my_requests_tab(self):
        """Вкладка с моими заявками (для заказчиков и специалистов)"""
        if self.current_user['user_type'] not in ['Заказчик', 'Специалист']:
            return
        
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        if self.current_user['user_type'] == 'Заказчик':
            title = QLabel('📝 Мои заявки')
        else:
            title = QLabel('🔧 Мои задачи')
        
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Таблица
        self.my_requests_table = QTableWidget()
        self.my_requests_table.setColumnCount(6)
        self.my_requests_table.setHorizontalHeaderLabels([
            'ID', 'Дата', 'Тип техники', 'Модель', 'Проблема', 'Статус'
        ])
        self.my_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.my_requests_table.doubleClicked.connect(self.show_request_details)
        
        layout.addWidget(self.my_requests_table)
        
        tab.setLayout(layout)
        
        if self.current_user['user_type'] == 'Заказчик':
            self.tabs.addTab(tab, '📝 Мои заявки')
        else:
            self.tabs.addTab(tab, '🔧 Мои задачи')
    
    def create_statistics_tab(self):
        """Вкладка со статистикой"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel('📊 Статистика и аналитика')
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Кнопка обновления статистики
        refresh_stats_btn = QPushButton('🔄 Обновить статистику')
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
            }
        """)
        layout.addWidget(self.stats_text)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, '📊 Статистика')
        
        # Загрузка статистики
        self.load_statistics()
    
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
            self.requests_table.setItem(row, 4, QTableWidgetItem(request['problem_description'][:50] + '...'))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['request_status']))
            self.requests_table.setItem(row, 6, QTableWidgetItem(request['client_name']))
            self.requests_table.setItem(row, 7, QTableWidgetItem(request['master_name'] or 'Не назначен'))
    
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
            self.requests_table.setItem(row, 4, QTableWidgetItem(request['problem_description'][:50] + '...'))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['request_status']))
            self.requests_table.setItem(row, 6, QTableWidgetItem(request['client_name']))
            self.requests_table.setItem(row, 7, QTableWidgetItem(''))
    
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
        dialog = RequestDetailsDialog(self.db, self.current_user, request_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_requests()
    
    def load_statistics(self):
        """Загрузка статистики"""
        stats = self.db.get_statistics()
        
        text = f"""
<h2 style="color: #4CAF50;">📊 Общая статистика</h2>

<p><b>Всего заявок:</b> {stats.get('total_requests', 0)}</p>
<p><b>Завершённых заявок:</b> {stats.get('completed_requests', 0)}</p>
<p><b>Среднее время выполнения:</b> {stats.get('avg_completion_time', 0):.1f} дней</p>

<h3 style="color: #2196F3;">📈 Статистика по типам оборудования:</h3>
"""
        
        for item in stats.get('by_tech_type', []):
            text += f"<p>• {item['type']}: <b>{item['count']}</b> заявок</p>"
        
        text += "<h3 style='color: #FF9800;'>📊 Статистика по статусам:</h3>"
        
        for item in stats.get('by_status', []):
            text += f"<p>• {item['status']}: <b>{item['count']}</b> заявок</p>"
        
        self.stats_text.setHtml(text)

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
        self.tech_type_combo.addItems(['Кондиционер', 'Увлажнитель воздуха', 'Сушилка для рук', 'Вентиляция', 'Отопление'])
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText('Например: Samsung AR09')
        
        self.problem_input = QTextEdit()
        self.problem_input.setPlaceholderText('Опишите проблему подробно...')
        self.problem_input.setMaximumHeight(150)
        
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
    
    def __init__(self, db, user, request_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_user = user
        self.request_id = request_id
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(f'Заявка #{self.request_id}')
        self.setFixedSize(700, 600)
        
        layout = QVBoxLayout()
        
        # Детали заявки
        details_group = QGroupBox('Информация о заявке')
        details_layout = QFormLayout()
        
        # Загружаем данные заявки
        requests = self.db.get_all_requests()
        request_data = next((r for r in requests if r['request_id'] == self.request_id), None)
        
        if request_data:
            details_layout.addRow('ID:', QLabel(str(request_data['request_id'])))
            details_layout.addRow('Дата:', QLabel(str(request_data['start_date'])))
            details_layout.addRow('Тип:', QLabel(request_data['climate_tech_type']))
            details_layout.addRow('Модель:', QLabel(request_data['climate_tech_model']))
            details_layout.addRow('Проблема:', QLabel(request_data['problem_description']))
            details_layout.addRow('Статус:', QLabel(request_data['request_status']))
            details_layout.addRow('Клиент:', QLabel(request_data['client_name']))
            details_layout.addRow('Мастер:', QLabel(request_data['master_name'] or 'Не назначен'))
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Кнопки действий
        if self.current_user['user_type'] in ['Оператор', 'Менеджер']:
            actions_group = QGroupBox('Действия')
            actions_layout = QHBoxLayout()
            
            assign_btn = QPushButton('Назначить мастера')
            assign_btn.clicked.connect(self.assign_master)
            
            status_btn = QPushButton('Изменить статус')
            status_btn.clicked.connect(self.change_status)
            
            actions_layout.addWidget(assign_btn)
            actions_layout.addWidget(status_btn)
            actions_group.setLayout(actions_layout)
            layout.addWidget(actions_group)
        
        # Комментарии
        comments_group = QGroupBox('Комментарии')
        comments_layout = QVBoxLayout()
        
        self.comments_text = QTextEdit()
        self.comments_text.setReadOnly(True)
        self.load_comments()
        
        comments_layout.addWidget(self.comments_text)
        
        if self.current_user['user_type'] == 'Специалист':
            comment_input_layout = QHBoxLayout()
            self.new_comment_input = QLineEdit()
            self.new_comment_input.setPlaceholderText('Введите комментарий...')
            add_comment_btn = QPushButton('Добавить')
            add_comment_btn.clicked.connect(self.add_comment)
            
            comment_input_layout.addWidget(self.new_comment_input)
            comment_input_layout.addWidget(add_comment_btn)
            comments_layout.addLayout(comment_input_layout)
        
        comments_group.setLayout(comments_layout)
        layout.addWidget(comments_group)
        
        # Кнопки в нижней части
        bottom_buttons = QHBoxLayout()
        
        # Кнопка QR-кода (для завершённых заявок)
        if request_data and request_data['request_status'] == 'Готова к выдаче':
            qr_btn = QPushButton('📱 QR-код для отзыва')
            qr_btn.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            qr_btn.clicked.connect(self.show_qr_code)
            bottom_buttons.addWidget(qr_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton('Закрыть')
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        close_btn.clicked.connect(self.accept)
        bottom_buttons.addWidget(close_btn)
        
        layout.addLayout(bottom_buttons)
        
        self.setLayout(layout)
    
    def load_comments(self):
        """Загрузка комментариев"""
        comments = self.db.get_comments_by_request(self.request_id)
        
        text = ""
        for comment in comments:
            text += f"<p><b>{comment['master_name']}</b> ({comment['created_at']})<br>"
            text += f"{comment['message']}</p><hr>"
        
        self.comments_text.setHtml(text if text else "<p>Комментариев пока нет</p>")
    
    def add_comment(self):
        """Добавление комментария"""
        comment_text = self.new_comment_input.text().strip()
        
        if not comment_text:
            QMessageBox.warning(self, 'Предупреждение', 'Введите текст комментария!')
            return
        
        success = self.db.add_comment(
            comment_text,
            self.current_user['user_id'],
            self.request_id
        )
        
        if success:
            self.new_comment_input.clear()
            self.load_comments()
            QMessageBox.information(self, 'Успех', 'Комментарий добавлен!')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось добавить комментарий!')
    
    def assign_master(self):
        """Назначение мастера на заявку"""
        masters = self.db.get_masters()
        
        if not masters:
            QMessageBox.warning(self, 'Предупреждение', 'В системе нет доступных специалистов!')
            return
        
        master_names = [f"{m['fio']} (ID: {m['user_id']})" for m in masters]
        
        from PyQt6.QtWidgets import QInputDialog
        
        master_choice, ok = QInputDialog.getItem(
            self,
            'Выбор мастера',
            'Выберите специалиста для назначения:',
            master_names,
            0,
            False
        )
        
        if ok and master_choice:
            master_id = int(master_choice.split('ID: ')[1].rstrip(')'))
            
            success = self.db.assign_master(self.request_id, master_id)
            
            if success:
                QMessageBox.information(self, 'Успех', 'Мастер успешно назначен!')
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось назначить мастера!')
    
    def change_status(self):
        """Изменение статуса заявки"""
        statuses = ['Новая заявка', 'В процессе ремонта', 'Готова к выдаче', 'Ожидание комплектующих']
        
        from PyQt6.QtWidgets import QInputDialog
        
        status, ok = QInputDialog.getItem(
            self,
            'Изменение статуса',
            'Выберите новый статус заявки:',
            statuses,
            0,
            False
        )
        
        if ok and status:
            success = self.db.update_request_status(self.request_id, status)
            
            if success:
                QMessageBox.information(self, 'Успех', f'Статус изменён на: {status}')
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось изменить статус!')
    
    def show_qr_code(self):
        """Показать QR-код для отзыва о качестве работы"""
        qr_dialog = QRCodeDialog(self.request_id, self)
        qr_dialog.exec()


def main():
    """Главная функция приложения"""
    app = QApplication(sys.argv)
    
    # Применяем общий стиль
    app.setStyle('Fusion')
    
    # Окно входа
    login_window = LoginWindow()
    
    if login_window.exec() == QDialog.DialogCode.Accepted:
        # Если вход успешен, открываем главное окно
        main_window = MainWindow(login_window.db, login_window.current_user)
        main_window.show()
        sys.exit(app.exec())
    else:
        # Если вход отменён, закрываем БД и выходим
        login_window.db.close()
        sys.exit(0)


if __name__ == '__main__':
    main()