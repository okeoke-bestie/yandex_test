import os
import time
import urllib.parse
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://cloud-api.yandex.net/v1/disk"
TOKEN = os.getenv("YANDEX_DISK_TOKEN")

@pytest.fixture(scope="session")
def api_client():
    """Фикстура для создания HTTP-сессии с авторизацией."""
    if not TOKEN:
        pytest.fail(
            "Не найден YANDEX_DISK_TOKEN. "
            "Установите его в переменной окружения или создайте файл .env на основе .env.example"
        )
    
    session = requests.Session()
    session.headers.update({
        "Authorization": f"OAuth {TOKEN}",
        "Content-Type": "application/json"
    })
    return session

@pytest.fixture
def test_folder_path():
    """Генерирует уникальный путь для тестовой папки на каждый тест."""
    timestamp = int(time.time() * 1000)
    return f"/autotest_folder_{timestamp}"

@pytest.fixture(autouse=True)
def cleanup_resources(api_client, test_folder_path):
    """Автоматическая очистка тестовых ресурсов после выполнения каждого теста."""
    yield
    # Удаление ресурсов в обратном порядке
    for path in [f"{test_folder_path}_copy", test_folder_path]:
        encoded_path = urllib.parse.quote(path, safe="")
        # Игнорирование ошибок
        api_client.delete(
            f"{BASE_URL}/resources",
            params={"path": encoded_path, "permanently": "true"}
        )
