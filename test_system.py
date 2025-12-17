"""
Скрипт автоматического тестирования системы учёта заявок

Проверяет основные функции модуля database.py
"""

from database_module import Database
import sys

def test_connection():
    """Тест 1: Подключение к базе данных"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Подключение к базе данных")
    print("="*60)
    
    try:
        db = Database()
        print("✅ PASSED: Подключение к PostgreSQL успешно")
        return db, True
    except Exception as e:
        print(f"❌ FAILED: Ошибка подключения - {e}")
        return None, False

def test_add_user(db):
    """Тест 2: Добавление пользователя"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Добавление нового пользователя")
    print("="*60)
    
    try:
        user_id = db.add_user(
            fio="Тестовый Пользователь",
            phone="89991234567",
            login="test_user_001",
            password="test123",
            user_type="Заказчик"
        )
        
        if user_id:
            print(f"✅ PASSED: Пользователь создан с ID: {user_id}")
            return user_id, True
        else:
            print("❌ FAILED: Не удалось создать пользователя")
            return None, False
            
    except Exception as e:
        print(f"❌ FAILED: Ошибка при создании пользователя - {e}")
        return None, False

def test_authentication(db):
    """Тест 3: Аутентификация пользователя"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Аутентификация пользователя")
    print("="*60)
    
    try:
        # Тест с правильными данными
        user = db.authenticate_user("login1", "pass1")
        if user:
            print(f"✅ PASSED: Успешная аутентификация пользователя {user['fio']}")
            success1 = True
        else:
            print("❌ FAILED: Не удалось аутентифицировать пользователя")
            success1 = False
        
        # Тест с неправильными данными
        user_wrong = db.authenticate_user("wrong_login", "wrong_pass")
        if not user_wrong:
            print("✅ PASSED: Отказ в доступе с неверными данными")
            success2 = True
        else:
            print("❌ FAILED: Система пропустила неверные данные")
            success2 = False
        
        return success1 and success2
        
    except Exception as e:
        print(f"❌ FAILED: Ошибка при аутентификации - {e}")
        return False

def test_add_request(db, client_id):
    """Тест 4: Добавление заявки"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Добавление новой заявки")
    print("="*60)
    
    try:
        request_id = db.add_request(
            climate_tech_type="Кондиционер",
            climate_tech_model="Test Model AC-2000",
            problem_description="Тестовая заявка для проверки функционала",
            client_id=client_id
        )
        
        if request_id:
            print(f"✅ PASSED: Заявка создана с ID: {request_id}")
            return request_id, True
        else:
            print("❌ FAILED: Не удалось создать заявку")
            return None, False
            
    except Exception as e:
        print(f"❌ FAILED: Ошибка при создании заявки - {e}")
        return None, False

def test_get_requests(db):
    """Тест 5: Получение списка заявок"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Получение списка заявок")
    print("="*60)
    
    try:
        # Получение всех заявок
        all_requests = db.get_all_requests()
        print(f"✅ PASSED: Получено всего заявок: {len(all_requests)}")
        
        # Получение заявок по статусу
        new_requests = db.get_all_requests(status="Новая заявка")
        print(f"✅ PASSED: Новых заявок: {len(new_requests)}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Ошибка при получении заявок - {e}")
        return False

def test_assign_master(db, request_id):
    """Тест 6: Назначение мастера"""
    print("\n" + "="*60)
    print("ТЕСТ 6: Назначение мастера на заявку")
    print("="*60)
    
    try:
        # Получаем список мастеров
        masters = db.get_masters()
        
        if not masters:
            print("⚠️  WARNING: Нет доступных мастеров в системе")
            return False
        
        master_id = masters[0]['user_id']
        success = db.assign_master(request_id, master_id)
        
        if success:
            print(f"✅ PASSED: Мастер ID:{master_id} назначен на заявку ID:{request_id}")
            return True
        else:
            print("❌ FAILED: Не удалось назначить мастера")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Ошибка при назначении мастера - {e}")
        return False

def test_add_comment(db, request_id, master_id):
    """Тест 7: Добавление комментария"""
    print("\n" + "="*60)
    print("ТЕСТ 7: Добавление комментария к заявке")
    print("="*60)
    
    try:
        success = db.add_comment(
            message="Тестовый комментарий - проверка функционала",
            master_id=master_id,
            request_id=request_id
        )
        
        if success:
            print(f"✅ PASSED: Комментарий добавлен к заявке ID:{request_id}")
            
            # Проверяем получение комментариев
            comments = db.get_comments_by_request(request_id)
            print(f"✅ PASSED: Получено комментариев: {len(comments)}")
            return True
        else:
            print("❌ FAILED: Не удалось добавить комментарий")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Ошибка при добавлении комментария - {e}")
        return False

def test_update_status(db, request_id):
    """Тест 8: Изменение статуса заявки"""
    print("\n" + "="*60)
    print("ТЕСТ 8: Изменение статуса заявки")
    print("="*60)
    
    try:
        success = db.update_request_status(request_id, "Готова к выдаче")
        
        if success:
            print(f"✅ PASSED: Статус заявки ID:{request_id} изменён на 'Готова к выдаче'")
            return True
        else:
            print("❌ FAILED: Не удалось изменить статус")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Ошибка при изменении статуса - {e}")
        return False

def test_search(db):
    """Тест 9: Поиск заявок"""
    print("\n" + "="*60)
    print("ТЕСТ 9: Поиск заявок")
    print("="*60)
    
    try:
        # Поиск по типу оборудования
        results = db.search_requests("Кондиционер")
        print(f"✅ PASSED: Найдено заявок по запросу 'Кондиционер': {len(results)}")
        
        # Поиск по несуществующему запросу
        no_results = db.search_requests("НЕСУЩЕСТВУЮЩИЙ_ЗАПРОС_12345")
        if len(no_results) == 0:
            print(f"✅ PASSED: Корректная обработка пустых результатов поиска")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Ошибка при поиске - {e}")
        return False

def test_statistics(db):
    """Тест 10: Расчёт статистики"""
    print("\n" + "="*60)
    print("ТЕСТ 10: Расчёт статистики")
    print("="*60)
    
    try:
        stats = db.get_statistics()
        
        print(f"  • Всего заявок: {stats.get('total_requests', 0)}")
        print(f"  • Завершённых заявок: {stats.get('completed_requests', 0)}")
        print(f"  • Среднее время выполнения: {stats.get('avg_completion_time', 0):.2f} дней")
        
        print(f"\n  Статистика по типам оборудования:")
        for item in stats.get('by_tech_type', []):
            print(f"    - {item['type']}: {item['count']} заявок")
        
        print(f"\n  Статистика по статусам:")
        for item in stats.get('by_status', []):
            print(f"    - {item['status']}: {item['count']} заявок")
        
        print("\n✅ PASSED: Статистика успешно рассчитана")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Ошибка при расчёте статистики - {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "🔬"*30)
    print("   АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("🔬"*30)
    
    results = []
    
    # Тест 1: Подключение
    db, success = test_connection()
    results.append(("Подключение к БД", success))
    
    if not db:
        print("\n❌ КРИТИЧЕСКАЯ ОШИБКА: Невозможно продолжить тестирование без подключения к БД")
        return
    
    try:
        # Тест 2: Добавление пользователя
        test_user_id, success = test_add_user(db)
        results.append(("Добавление пользователя", success))
        
        # Тест 3: Аутентификация
        success = test_authentication(db)
        results.append(("Аутентификация", success))
        
        # Тест 4: Добавление заявки
        if test_user_id:
            test_request_id, success = test_add_request(db, test_user_id)
            results.append(("Добавление заявки", success))
        else:
            # Используем существующего пользователя
            test_request_id, success = test_add_request(db, 7)  # client_id из тестовых данных
            results.append(("Добавление заявки", success))
        
        # Тест 5: Получение заявок
        success = test_get_requests(db)
        results.append(("Получение списка заявок", success))
        
        # Тест 6: Назначение мастера
        if test_request_id:
            success = test_assign_master(db, test_request_id)
            results.append(("Назначение мастера", success))
        
        # Тест 7: Добавление комментария
        if test_request_id:
            success = test_add_comment(db, test_request_id, 2)  # master_id=2 из тестовых данных
            results.append(("Добавление комментария", success))
        
        # Тест 8: Изменение статуса
        if test_request_id:
            success = test_update_status(db, test_request_id)
            results.append(("Изменение статуса", success))
        
        # Тест 9: Поиск
        success = test_search(db)
        results.append(("Поиск заявок", success))
        
        # Тест 10: Статистика
        success = test_statistics(db)
        results.append(("Расчёт статистики", success))
        
    finally:
        db.close()
    
    # Итоговый отчёт
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*60)
    print(f"Пройдено тестов: {passed}/{total} ({passed/total*100:.1f}%)")
    print("-"*60)
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"\n⚠️  ВНИМАНИЕ: {total - passed} тест(ов) не пройдено!")

if __name__ == '__main__':
    run_all_tests()
