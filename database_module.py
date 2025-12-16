import psycopg2
from psycopg2 import Error
from typing import List, Dict, Optional
import bcrypt


class Database:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(
        self,
        host='localhost',
        database='climate_service',
        user='postgres',
        password='p4v17102006',
        port=5432
    ):
        try:
            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            print("✅ Подключение к PostgreSQL успешно")
        except Error as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise

    # ===================== USERS =====================

    def add_user(
        self,
        fio: str,
        phone: str,
        login: str,
        password: str,
        user_type: str
    ) -> Optional[int]:
        """
        Добавление пользователя.
        Если логин уже существует — возвращает его user_id.
        """
        try:
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            self.cursor.execute("""
                INSERT INTO users (fio, phone, login, password, user_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id
            """, (fio, phone, login, hashed_password, user_type))

            return self.cursor.fetchone()[0]

        except Error:
            # Пользователь уже существует — возвращаем его id
            self.cursor.execute(
                "SELECT user_id FROM users WHERE login = %s",
                (login,)
            )
            row = self.cursor.fetchone()
            return row[0] if row else None

    def authenticate_user(self, login: str, password: str) -> Optional[Dict]:
        try:
            self.cursor.execute("""
                SELECT user_id, fio, phone, login, user_type, password
                FROM users
                WHERE login = %s
            """, (login,))

            row = self.cursor.fetchone()
            if row and bcrypt.checkpw(password.encode(), row[5].encode()):
                return {
                    'user_id': row[0],
                    'fio': row[1],
                    'phone': row[2],
                    'login': row[3],
                    'user_type': row[4]
                }
            return None

        except Error as e:
            print(f"❌ authenticate_user error: {e}")
            return None

    def get_all_users(self) -> List[Dict]:
        self.cursor.execute("""
            SELECT user_id, fio, phone, login, user_type
            FROM users
            ORDER BY user_id
        """)
        return [
            {
                'user_id': r[0],
                'fio': r[1],
                'phone': r[2],
                'login': r[3],
                'user_type': r[4]
            }
            for r in self.cursor.fetchall()
        ]

    def delete_user(self, user_id: int) -> bool:
        try:
            self.cursor.execute(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,)
            )
            return True
        except Error:
            return False

    def get_specialists(self) -> List[Dict]:
        self.cursor.execute("""
            SELECT user_id, fio, phone
            FROM users
            WHERE user_type = 'Специалист'
            ORDER BY fio
        """)
        return [
            {'user_id': r[0], 'fio': r[1], 'phone': r[2]}
            for r in self.cursor.fetchall()
        ]

    # ===================== REQUESTS =====================

    def add_request(
        self,
        climate_tech_type: str,
        climate_tech_model: str,
        problem_description: str,
        client_id: int
    ) -> Optional[int]:
        try:
            self.cursor.execute("""
                INSERT INTO requests (
                    climate_tech_type,
                    climate_tech_model,
                    problem_description,
                    client_id,
                    request_status,
                    start_date
                )
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
                RETURNING request_id
            """, (
                climate_tech_type,
                climate_tech_model,
                problem_description,
                client_id,
                'Новая заявка'
            ))
            return self.cursor.fetchone()[0]

        except Error as e:
            print(f"❌ add_request error: {e}")
            return None

    def get_all_requests(self, status: Optional[str] = None) -> List[Dict]:
        query = """
            SELECT r.request_id, r.start_date, r.climate_tech_type,
                   r.climate_tech_model, r.problem_description,
                   r.request_status,
                   u_client.fio,
                   u_master.fio
            FROM requests r
            JOIN users u_client ON r.client_id = u_client.user_id
            LEFT JOIN users u_master ON r.master_id = u_master.user_id
        """

        params = ()
        if status:
            query += " WHERE r.request_status = %s"
            params = (status,)

        query += " ORDER BY r.request_id DESC"

        self.cursor.execute(query, params)

        return [
            {
                'request_id': r[0],
                'start_date': r[1],
                'climate_tech_type': r[2],
                'climate_tech_model': r[3],
                'problem_description': r[4],
                'request_status': r[5],
                'client_name': r[6],
                'master_name': r[7]
            }
            for r in self.cursor.fetchall()
        ]

    def get_request_by_id(self, request_id: int) -> Optional[Dict]:
        self.cursor.execute("""
            SELECT r.request_id, r.start_date, r.climate_tech_type,
                   r.climate_tech_model, r.problem_description,
                   r.request_status,
                   u_client.fio,
                   u_master.fio
            FROM requests r
            JOIN users u_client ON r.client_id = u_client.user_id
            LEFT JOIN users u_master ON r.master_id = u_master.user_id
            WHERE r.request_id = %s
        """, (request_id,))

        r = self.cursor.fetchone()
        if not r:
            return None

        return {
            'request_id': r[0],
            'start_date': r[1],
            'climate_tech_type': r[2],
            'climate_tech_model': r[3],
            'problem_description': r[4],
            'request_status': r[5],
            'client_name': r[6],
            'master_name': r[7]
        }

    def assign_master(self, request_id: int, master_id: int) -> bool:
        """
        Назначение мастера.
        Нельзя назначить мастера на завершённую заявку.
        """
        try:
            self.cursor.execute("""
                UPDATE requests
                SET master_id = %s,
                    request_status = 'В процессе ремонта'
                WHERE request_id = %s
                  AND request_status != 'Готова к выдаче'
            """, (master_id, request_id))
            return True
        except Error:
            return False

    def update_request_status(self, request_id: int, new_status: str) -> bool:
        try:
            self.cursor.execute("""
                UPDATE requests
                SET request_status = %s,
                    completion_date = CASE
                        WHEN %s = 'Готова к выдаче'
                        THEN CURRENT_DATE
                        ELSE completion_date
                    END
                WHERE request_id = %s
            """, (new_status, new_status, request_id))
            return True
        except Error:
            return False

    # ===================== COMMENTS =====================

    def add_comment(self, message: str, master_id: int, request_id: int) -> bool:
        try:
            self.cursor.execute("""
                INSERT INTO comments (
                    message,
                    master_id,
                    request_id,
                    created_at
                )
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (message, master_id, request_id))
            return True
        except Error as e:
            print(f"❌ add_comment error: {e}")
            return False

    def get_comments_by_request(self, request_id: int) -> List[Dict]:
        self.cursor.execute("""
            SELECT c.comment_id, c.message, c.created_at, u.fio
            FROM comments c
            JOIN users u ON c.master_id = u.user_id
            WHERE c.request_id = %s
            ORDER BY c.created_at DESC
        """, (request_id,))

        return [
            {
                'comment_id': r[0],
                'message': r[1],
                'created_at': r[2],
                'master_name': r[3]
            }
            for r in self.cursor.fetchall()
        ]

    # ===================== SEARCH =====================

    def search_requests(self, search_term: str) -> List[Dict]:
        try:
            pattern = f"%{search_term}%"

            self.cursor.execute("""
                SELECT r.request_id, r.start_date, r.climate_tech_type,
                       r.climate_tech_model, r.problem_description,
                       r.request_status,
                       u_client.fio, u_client.phone,
                       u_master.fio
                FROM requests r
                JOIN users u_client ON r.client_id = u_client.user_id
                LEFT JOIN users u_master ON r.master_id = u_master.user_id
                WHERE
                    r.request_id::TEXT LIKE %s OR
                    r.climate_tech_type ILIKE %s OR
                    r.climate_tech_model ILIKE %s OR
                    r.problem_description ILIKE %s OR
                    u_client.fio ILIKE %s OR
                    u_client.phone LIKE %s
                ORDER BY r.request_id DESC
            """, (pattern,) * 6)

            return [
                {
                    'request_id': r[0],
                    'start_date': r[1],
                    'climate_tech_type': r[2],
                    'climate_tech_model': r[3],
                    'problem_description': r[4],
                    'request_status': r[5],
                    'client_name': r[6],
                    'client_phone': r[7],
                    'master_name': r[8]
                }
                for r in self.cursor.fetchall()
            ]

        except Error as e:
            print(f"❌ search_requests error: {e}")
            return []

    # ===================== STATISTICS =====================

    def get_statistics(self) -> Dict:
        try:
            stats = {}

            self.cursor.execute("SELECT COUNT(*) FROM requests")
            stats['total_requests'] = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT COUNT(*) FROM requests
                WHERE request_status = 'Готова к выдаче'
            """)
            stats['completed_requests'] = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT AVG(EXTRACT(DAY FROM (completion_date - start_date)))
                FROM requests
                WHERE completion_date IS NOT NULL
            """)
            avg_days = self.cursor.fetchone()[0]
            stats['avg_completion_time'] = round(avg_days, 1) if avg_days else 0

            self.cursor.execute("""
                SELECT climate_tech_type, COUNT(*)
                FROM requests
                GROUP BY climate_tech_type
                ORDER BY COUNT(*) DESC
            """)
            stats['by_tech_type'] = [
                {'type': r[0], 'count': r[1]}
                for r in self.cursor.fetchall()
            ]

            self.cursor.execute("""
                SELECT request_status, COUNT(*)
                FROM requests
                GROUP BY request_status
            """)
            stats['by_status'] = [
                {'status': r[0], 'count': r[1]}
                for r in self.cursor.fetchall()
            ]

            return stats

        except Error as e:
            print(f"❌ get_statistics error: {e}")
            return {}

    def close(self):
        self.cursor.close()
        self.connection.close()
        print("✅ Соединение с БД закрыто")
