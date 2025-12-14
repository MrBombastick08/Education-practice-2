import psycopg2
from psycopg2 import sql, Error
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class Database:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self, host='localhost', database='climate_service', 
                 user='postgres', password='postgres', port=5432):
        """
        Инициализация подключения к PostgreSQL
        
        Args:
            host: hocalhost
            database: climate_service
            user: postgres
            password: p4v17102006
            port: 5432
        """
        try:
            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            self.cursor = self.connection.cursor()
            self.create_tables()
            print("✅ Подключение к PostgreSQL успешно установлено")
        except Error as e:
            print(f"❌ Ошибка при подключении к PostgreSQL: {e}")
            raise
    
    def create_tables(self):
        """Создание таблиц в БД согласно ER-диаграмме в 3НФ"""
        
        try:
            # Таблица пользователей
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    fio VARCHAR(255) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    login VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    user_type VARCHAR(20) NOT NULL CHECK(user_type IN ('Менеджер', 'Специалист', 'Оператор', 'Заказчик', 'Менеджер по качеству'))
                )
            ''')
            
            # Таблица заявок
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    request_id SERIAL PRIMARY KEY,
                    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    climate_tech_type VARCHAR(100) NOT NULL,
                    climate_tech_model VARCHAR(255) NOT NULL,
                    problem_description TEXT NOT NULL,
                    request_status VARCHAR(30) NOT NULL DEFAULT 'Новая заявка' 
                        CHECK(request_status IN ('Новая заявка', 'В процессе ремонта', 'Готова к выдаче', 'Ожидание комплектующих')),
                    completion_date DATE,
                    repair_parts TEXT,
                    master_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                    client_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Таблица комментариев
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    comment_id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    master_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    request_id INTEGER NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE
                )
            ''')
            
            # Индексы для оптимизации запросов
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(request_status)
            ''')
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requests_master ON requests(master_id)
            ''')
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_requests_client ON requests(client_id)
            ''')
            
            self.connection.commit()
            print("✅ Таблицы успешно созданы")
            
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при создании таблиц: {e}")
            raise
    
    def add_user(self, fio: str, phone: str, login: str, 
                 password: str, user_type: str) -> Optional[int]:
        """
        Добавление нового пользователя
        
        Returns:
            user_id нового пользователя или None при ошибке
        """
        try:
            self.cursor.execute('''
                INSERT INTO users (fio, phone, login, password, user_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id
            ''', (fio, phone, login, password, user_type))
            
            user_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return user_id
            
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при добавлении пользователя: {e}")
            return None
    
    def authenticate_user(self, login: str, password: str) -> Optional[Dict]:
        """
        Аутентификация пользователя
        
        Returns:
            Словарь с данными пользователя или None
        """
        try:
            self.cursor.execute('''
                SELECT user_id, fio, phone, login, user_type
                FROM users
                WHERE login = %s AND password = %s
            ''', (login, password))
            
            result = self.cursor.fetchone()
            if result:
                return {
                    'user_id': result[0],
                    'fio': result[1],
                    'phone': result[2],
                    'login': result[3],
                    'user_type': result[4]
                }
            return None
            
        except Error as e:
            print(f"❌ Ошибка при аутентификации: {e}")
            return None
    
    def add_request(self, climate_tech_type: str, climate_tech_model: str,
                    problem_description: str, client_id: int) -> Optional[int]:
        """
        Добавление новой заявки
        
        Returns:
            request_id новой заявки или None при ошибке
        """
        try:
            self.cursor.execute('''
                INSERT INTO requests (climate_tech_type, climate_tech_model, 
                                     problem_description, client_id, request_status)
                VALUES (%s, %s, %s, %s, 'Новая заявка')
                RETURNING request_id
            ''', (climate_tech_type, climate_tech_model, problem_description, client_id))
            
            request_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return request_id
            
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при добавлении заявки: {e}")
            return None
    
    def get_all_requests(self, status: Optional[str] = None) -> List[Dict]:
        """
        Получение всех заявок с возможностью фильтрации по статусу
        
        Args:
            status: статус для фильтрации (опционально)
        
        Returns:
            Список заявок
        """
        try:
            if status:
                query = '''
                    SELECT r.request_id, r.start_date, r.climate_tech_type, 
                           r.climate_tech_model, r.problem_description, r.request_status,
                           r.completion_date, r.repair_parts,
                           u_client.fio as client_name, u_client.phone as client_phone,
                           u_master.fio as master_name
                    FROM requests r
                    JOIN users u_client ON r.client_id = u_client.user_id
                    LEFT JOIN users u_master ON r.master_id = u_master.user_id
                    WHERE r.request_status = %s
                    ORDER BY r.request_id DESC
                '''
                self.cursor.execute(query, (status,))
            else:
                query = '''
                    SELECT r.request_id, r.start_date, r.climate_tech_type, 
                           r.climate_tech_model, r.problem_description, r.request_status,
                           r.completion_date, r.repair_parts,
                           u_client.fio as client_name, u_client.phone as client_phone,
                           u_master.fio as master_name
                    FROM requests r
                    JOIN users u_client ON r.client_id = u_client.user_id
                    LEFT JOIN users u_master ON r.master_id = u_master.user_id
                    ORDER BY r.request_id DESC
                '''
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            requests = []
            
            for row in results:
                requests.append({
                    'request_id': row[0],
                    'start_date': row[1],
                    'climate_tech_type': row[2],
                    'climate_tech_model': row[3],
                    'problem_description': row[4],
                    'request_status': row[5],
                    'completion_date': row[6],
                    'repair_parts': row[7],
                    'client_name': row[8],
                    'client_phone': row[9],
                    'master_name': row[10]
                })
            
            return requests
            
        except Error as e:
            print(f"❌ Ошибка при получении заявок: {e}")
            return []
    
    def update_request_status(self, request_id: int, new_status: str) -> bool:
        """Обновление статуса заявки"""
        try:
            self.cursor.execute('''
                UPDATE requests
                SET request_status = %s,
                    completion_date = CASE 
                        WHEN %s = 'Готова к выдаче' THEN CURRENT_DATE 
                        ELSE completion_date 
                    END
                WHERE request_id = %s
            ''', (new_status, new_status, request_id))
            
            self.connection.commit()
            return True
            
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при обновлении статуса: {e}")
            return False
    
    def assign_master(self, request_id: int, master_id: int) -> bool:
        """Назначение мастера на заявку"""
        try:
            self.cursor.execute('''
                UPDATE requests
                SET master_id = %s,
                    request_status = 'В процессе ремонта'
                WHERE request_id = %s
            ''', (master_id, request_id))
            
            self.connection.commit()
            return True
            
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при назначении мастера: {e}")
            return False
    
    def add_comment(self, message: str, master_id: int, request_id: int) -> bool:
        """Добавление комментария к заявке"""
        try:
            self.cursor.execute('''
                INSERT INTO comments (message, master_id, request_id)
                VALUES (%s, %s, %s)
            ''', (message, master_id, request_id))
            
            self.connection.commit()
            return True
            
        except Error as e:
            self.connection.rollback()
            print(f"❌ Ошибка при добавлении комментария: {e}")
            return False
    
    def get_comments_by_request(self, request_id: int) -> List[Dict]:
        """Получение всех комментариев по заявке"""
        try:
            self.cursor.execute('''
                SELECT c.comment_id, c.message, c.created_at, u.fio
                FROM comments c
                JOIN users u ON c.master_id = u.user_id
                WHERE c.request_id = %s
                ORDER BY c.created_at DESC
            ''', (request_id,))
            
            results = self.cursor.fetchall()
            comments = []
            
            for row in results:
                comments.append({
                    'comment_id': row[0],
                    'message': row[1],
                    'created_at': row[2],
                    'master_name': row[3]
                })
            
            return comments
            
        except Error as e:
            print(f"❌ Ошибка при получении комментариев: {e}")
            return []
    
    def get_masters(self) -> List[Dict]:
        """Получение списка всех специалистов"""
        try:
            self.cursor.execute('''
                SELECT user_id, fio, phone
                FROM users
                WHERE user_type = 'Специалист'
                ORDER BY fio
            ''')
            
            results = self.cursor.fetchall()
            masters = []
            
            for row in results:
                masters.append({
                    'user_id': row[0],
                    'fio': row[1],
                    'phone': row[2]
                })
            
            return masters
            
        except Error as e:
            print(f"❌ Ошибка при получении списка мастеров: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Расчёт статистики по заявкам"""
        try:
            stats = {}
            
            # Общее количество заявок
            self.cursor.execute('SELECT COUNT(*) FROM requests')
            stats['total_requests'] = self.cursor.fetchone()[0]
            
            # Количество завершённых заявок
            self.cursor.execute('''
                SELECT COUNT(*) FROM requests 
                WHERE request_status = 'Готова к выдаче'
            ''')
            stats['completed_requests'] = self.cursor.fetchone()[0]
            
            # Среднее время выполнения заявки (в днях)
            self.cursor.execute('''
                SELECT AVG(completion_date - start_date) 
                FROM requests 
                WHERE completion_date IS NOT NULL
            ''')
            avg_time = self.cursor.fetchone()[0]
            stats['avg_completion_time'] = float(avg_time) if avg_time else 0
            
            # Статистика по типам оборудования
            self.cursor.execute('''
                SELECT climate_tech_type, COUNT(*) as count
                FROM requests
                GROUP BY climate_tech_type
                ORDER BY count DESC
            ''')
            tech_stats = self.cursor.fetchall()
            stats['by_tech_type'] = [
                {'type': row[0], 'count': row[1]} 
                for row in tech_stats
            ]
            
            # Статистика по статусам
            self.cursor.execute('''
                SELECT request_status, COUNT(*) as count
                FROM requests
                GROUP BY request_status
            ''')
            status_stats = self.cursor.fetchall()
            stats['by_status'] = [
                {'status': row[0], 'count': row[1]} 
                for row in status_stats
            ]
            
            return stats
            
        except Error as e:
            print(f"❌ Ошибка при расчёте статистики: {e}")
            return {}
    
    def search_requests(self, search_term: str) -> List[Dict]:
        """
        Поиск заявок по различным параметрам
        
        Args:
            search_term: поисковый запрос
        
        Returns:
            Список найденных заявок
        """
        try:
            query = '''
                SELECT r.request_id, r.start_date, r.climate_tech_type, 
                       r.climate_tech_model, r.problem_description, r.request_status,
                       u_client.fio as client_name, u_client.phone as client_phone
                FROM requests r
                JOIN users u_client ON r.client_id = u_client.user_id
                WHERE CAST(r.request_id AS TEXT) LIKE %s
                   OR r.climate_tech_type ILIKE %s
                   OR r.climate_tech_model ILIKE %s
                   OR r.problem_description ILIKE %s
                   OR u_client.fio ILIKE %s
                   OR u_client.phone LIKE %s
                ORDER BY r.request_id DESC
            '''
            
            search_pattern = f'%{search_term}%'
            self.cursor.execute(query, (search_pattern,) * 6)
            
            results = self.cursor.fetchall()
            requests = []
            
            for row in results:
                requests.append({
                    'request_id': row[0],
                    'start_date': row[1],
                    'climate_tech_type': row[2],
                    'climate_tech_model': row[3],
                    'problem_description': row[4],
                    'request_status': row[5],
                    'client_name': row[6],
                    'client_phone': row[7]
                })
            
            return requests
            
        except Error as e:
            print(f"❌ Ошибка при поиске заявок: {e}")
            return []
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("✅ Соединение с PostgreSQL закрыто")
