#!/bin/bash
# Скрипт для быстрого запуска тестов

set -e

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Todo Service Test Runner ===${NC}\n"

# Проверка окружения
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry не установлен. Установите Poetry сначала.${NC}"
    exit 1
fi

# Функция для запуска тестов
run_tests() {
    local test_type=$1
    local test_path=$2
    
    echo -e "${BLUE}Запуск ${test_type} тестов...${NC}"
    poetry run pytest ${test_path} -v
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${test_type} тесты пройдены${NC}\n"
    else
        echo -e "${RED}✗ ${test_type} тесты провалены${NC}\n"
        exit 1
    fi
}

# Парсинг аргументов
case "${1:-all}" in
    unit)
        run_tests "Unit" "tests/unit/"
        ;;
    integration)
        echo -e "${BLUE}Проверка PostgreSQL...${NC}"
        if ! docker ps | grep -q todo_postgres; then
            echo -e "${RED}PostgreSQL не запущен. Запустите: docker-compose up -d${NC}"
            exit 1
        fi
        run_tests "Integration" "tests/integration/"
        ;;
    e2e)
        echo -e "${BLUE}Проверка PostgreSQL...${NC}"
        if ! docker ps | grep -q todo_postgres; then
            echo -e "${RED}PostgreSQL не запущен. Запустите: docker-compose up -d${NC}"
            exit 1
        fi
        run_tests "E2E" "tests/e2e/"
        ;;
    cov)
        echo -e "${BLUE}Запуск тестов с покрытием кода...${NC}"
        poetry run pytest --cov=app --cov-report=html --cov-report=term-missing
        echo -e "${GREEN}✓ Отчёт о покрытии создан в htmlcov/index.html${NC}"
        ;;
    all)
        run_tests "Unit" "tests/unit/"
        
        echo -e "${BLUE}Проверка PostgreSQL для integration/e2e тестов...${NC}"
        if docker ps | grep -q todo_postgres; then
            run_tests "Integration" "tests/integration/"
            run_tests "E2E" "tests/e2e/"
        else
            echo -e "${RED}PostgreSQL не запущен. Пропускаем integration и e2e тесты.${NC}"
            echo -e "${BLUE}Для запуска всех тестов: docker-compose up -d${NC}\n"
        fi
        
        echo -e "${GREEN}=== Все доступные тесты пройдены! ===${NC}"
        ;;
    watch)
        echo -e "${BLUE}Запуск тестов в режиме watch...${NC}"
        poetry run ptw --runner "pytest -v"
        ;;
    *)
        echo "Использование: ./run_tests.sh [unit|integration|e2e|cov|all|watch]"
        echo ""
        echo "  unit         - Только unit тесты (быстро, без БД)"
        echo "  integration  - Только integration тесты (с БД)"
        echo "  e2e          - Только e2e тесты (полный API)"
        echo "  cov          - Все тесты с покрытием кода"
        echo "  all          - Все тесты (по умолчанию)"
        echo "  watch        - Автозапуск при изменениях"
        exit 1
        ;;
esac
