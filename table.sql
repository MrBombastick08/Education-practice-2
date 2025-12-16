-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    fio VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    -- Добавлена роль 'Администратор' в CHECK constraint
    user_type VARCHAR(30) NOT NULL 
        CHECK(user_type IN ('Менеджер', 'Специалист', 'Оператор', 'Заказчик', 'Менеджер по качеству', 'Администратор')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица заявок
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
    client_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица комментариев
CREATE TABLE IF NOT EXISTS comments (
    comment_id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    master_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    request_id INTEGER NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(request_status);
CREATE INDEX IF NOT EXISTS idx_requests_master ON requests(master_id);
CREATE INDEX IF NOT EXISTS idx_requests_client ON requests(client_id);
CREATE INDEX IF NOT EXISTS idx_requests_date ON requests(start_date);
CREATE INDEX IF NOT EXISTS idx_comments_request ON comments(request_id);
CREATE INDEX IF NOT EXISTS idx_users_login ON users(login);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_requests_updated_at 
    BEFORE UPDATE ON requests 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблицам
COMMENT ON TABLE users IS 'Таблица пользователей системы';
COMMENT ON TABLE requests IS 'Таблица заявок на ремонт';
COMMENT ON TABLE comments IS 'Таблица комментариев к заявкам';

-- Вывод информации
SELECT 'База данных climate_service успешно создана!' AS message;