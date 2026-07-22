import urllib.parse
import pytest
from conftest import BASE_URL

class TestYandexDiskAPI:
    """Набор тестов для проверки основных HTTP-методов API Яндекс.Диска."""

    def test_get_disk_info(self, api_client):
        """GET: Получение информации о диске пользователя."""
        response = api_client.get(f"{BASE_URL}/")
        
        assert response.status_code == 200, "Не удалось получить информацию о диске (проверьте токен)"
        data = response.json()
        
        assert "total_space" in data, "В ответе отсутствует поле total_space"
        assert "used_space" in data, "В ответе отсутствует поле used_space"
        assert data["total_space"] >= data["used_space"], "Использованное место превышает общее"

    def test_create_folder(self, api_client, test_folder_path):
        """PUT: Создание новой папки на диске."""
        encoded_path = urllib.parse.quote(test_folder_path, safe="")
        
        response = api_client.put(
            f"{BASE_URL}/resources",
            params={"path": encoded_path}
        )
        
        assert response.status_code == 201, f"Ожидался код 201 Created, получен {response.status_code}"
        data = response.json()
        
        assert "href" in data, "В ответе отсутствует ссылка на созданный ресурс"
        assert data["method"] == "GET", "Метод для проверки ресурса должен быть GET"

    def test_copy_resource(self, api_client, test_folder_path):
        """POST: Копирование файла или папки (метод POST используется для операции copy)."""
        # Гарантируем существование исходной папки для независимости теста
        encoded_path = urllib.parse.quote(test_folder_path, safe="")
        api_client.put(f"{BASE_URL}/resources", params={"path": encoded_path})
        
        encoded_from = urllib.parse.quote(test_folder_path, safe="")
        encoded_to = urllib.parse.quote(f"{test_folder_path}_copy", safe="")
        
        response = api_client.post(
            f"{BASE_URL}/resources/copy",
            params={
                "from": encoded_from,
                "path": encoded_to,
                "overwrite": "true"
            }
        )
        
        # API может вернуть 201 Created или 202 Accepted (для асинхронных операций)
        assert response.status_code in [201, 202], f"Ожидался код 201 или 202, получен {response.status_code}"

    def test_delete_resource(self, api_client, test_folder_path):
        """DELETE: Безвозвратное удаление файла или папки."""
        # Создаем ресурс специально для этого теста, чтобы он был полностью независимым
        encoded_path = urllib.parse.quote(test_folder_path, safe="")
        api_client.put(f"{BASE_URL}/resources", params={"path": encoded_path})
        
        response = api_client.delete(
            f"{BASE_URL}/resources",
            params={
                "path": encoded_path,
                "permanently": "true"
            }
        )
        
        # API возвращает 204 No Content (для файлов/пустых папок) или 202 Accepted (для непустых)
        assert response.status_code in [202, 204], f"Ожидался код 202 или 204, получен {response.status_code}"
        
        # Дополнительная проверка: убеждаемся, что ресурс действительно удален
        get_response = api_client.get(f"{BASE_URL}/resources", params={"path": encoded_path})
        assert get_response.status_code == 404, "Ресурс должен быть удален и возвращать статус 404 Not Found"