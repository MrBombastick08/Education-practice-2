from database import Database
import csv

def import_users_from_csv(db: Database, filename: str):
    """Импорт пользователей из CSV файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # Читаем CSV с разделителем точка с запятой
            reader = csv.DictReader(file, delimiter=';')
            
            count = 0
            for row in reader:
                user_id = db.add_user(
                    fio=row['fio'],
                    phone=row['phone'],
                    login=row['login'],
                    password=row['password'],
                    user_type=row['type']
                )
                if user_id:
                    count += 1
                    print(f"✅ Импортирован пользователь: {row['fio']} ({row['type']})")
            
            print(f"\n✅ Всего импортировано пользователей: {count}")
            
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
    except Exception as e:
        print(f"❌ Ошибка при импорте пользователей: {e}")

def import_requests_from_csv(db: Database, filename: str):
    """Импорт заявок из CSV файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            count = 0
            for row in reader:
                # Добавляем заявку
                request_id = db.cursor.execute('''
                    INSERT INTO requests (
                        start_date, climate_tech_type, climate_tech_model,
                        problem_description, request_status, completion_date,
                        repair_parts, master_id, client_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING request_id
                ''', (
                    row['startDate'],
                    row['climateTechType'],
                    row['climateTechModel'],
                    row['problemDescryption'],  # Опечатка в исходных данных
                    row['requestStatus'],
                    row['completionDate'] if row['completionDate'] != 'null' else None,
                    row['repairParts'] if row['repairParts'] else None,
                    int(row['masterID']) if row['masterID'] != 'null' else None,
                    int(row['clientID'])
                ))
                
                request_id = db.cursor.fetchone()[0]
                db.connection.commit()
                
                if request_id:
                    count += 1
                    print(f"✅ Импортирована заявка #{request_id}: {row['climateTechType']} - {row['requestStatus']}")
            
            print(f"\n✅ Всего импортировано заявок: {count}")
            
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
    except Exception as e:
        print(f"❌ Ошибка при импорте заявок: {e}")

def import_comments_from_csv(db: Database, filename: str):
    """Импорт комментариев из CSV файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            count = 0
            for row in reader:
                success = db.add_comment(
                    message=row['message'],
                    master_id=int(row['masterID']),
                    request_id=int(row['requestID'])
                )
                if success:
                    count += 1
                    print(f"✅ Импортирован комментарий к заявке #{row['requestID']}")
            
            print(f"\n✅ Всего импортировано комментариев: {count}")
            
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
    except Exception as e:
        print(f"❌ Ошибка при импорте комментариев: {e}")

def main():
    """Главная функция для импорта всех данных"""
    print("="*60)
    print("🔄 ИМПОРТ ДАННЫХ В БАЗУ")
    print("="*60)
    
    # Подключение к БД
    # ВАЖНО: Измените параметры подключения на свои
    db = Database(
        host='localhost',
        database='climate_service',
        user='postgres',
        password='postgres',
        port=5432
    )
    
    try:
        # Импорт пользователей
        print("\n📥 Импорт пользователей...")
        import_users_from_csv(db, 'inputDataUsers.txt')
        
        # Импорт заявок
        print("\n📥 Импорт заявок...")
        import_requests_from_csv(db, 'inputDataRequests.txt')
        
        # Импорт комментариев
        print("\n📥 Импорт комментариев...")
        import_comments_from_csv(db, 'inputDataComments.txt')
        
        print("\n" + "="*60)
        print("✅ ИМПОРТ УСПЕШНО ЗАВЕРШЁН!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
