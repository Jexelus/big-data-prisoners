from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta
import uuid

class PrisonerAPITest(HttpUser):
    wait_time = between(1, 2)  # Время ожидания между запросами (в секундах)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_prisoners = []  # Список для хранения UUID созданных заключенных

    @task(3)  # Создание заключенного (вес = 3)
    def create_prisoner(self):
        prisoner_data = {
            "id": str(uuid.uuid4()),
            "name": f"Prisoner_{random.randint(1000, 9999)}",
            "sentence_start": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "sentence_end": (datetime.now() + timedelta(days=random.randint(365, 1000))).isoformat(),
            "guard_name": f"Guard_{random.randint(100, 999)}"
        }
        response = self.client.post("/", json=prisoner_data)
        if response.status_code == 200:
            prisoner_id = response.json().get("id")  # Получаем UUID созданного заключенного
            if prisoner_id:
                self.created_prisoners.append(prisoner_id)  # Сохраняем UUID

    @task(4)  # Получение списка заключенных (вес = 4)
    def get_prisoners(self):
        self.client.get("/")

    @task(2)  # Получение конкретного заключенного (вес = 2)
    def get_prisoner(self):
        if self.created_prisoners:  # Проверяем, есть ли созданные заключенные
            prisoner_id = random.choice(self.created_prisoners)
            self.client.get(f"/{prisoner_id}", name="/[uuid]")

    @task(1)  # Обновление заключенного (вес = 1)
    def update_prisoner(self):
        if self.created_prisoners:  # Проверяем, есть ли созданные заключенные
            prisoner_id = random.choice(self.created_prisoners)
            update_data = {
                "name": f"UpdatedPrisoner_{random.randint(1000, 9999)}",
                "sentence_end": (datetime.now() + timedelta(days=random.randint(365, 1000))).isoformat(),
                "guard_name": f"UpdatedGuard_{random.randint(100, 999)}"
            }
            self.client.put(f"/{prisoner_id}", json=update_data, name="/[uuid]")

    @task(1)  # Удаление заключенного (вес = 1)
    def delete_prisoner(self):
        if self.created_prisoners:  # Проверяем, есть ли созданные заключенные
            prisoner_id = random.choice(self.created_prisoners)
            response = self.client.delete(f"/{prisoner_id}", name="/[uuid]")
            if response.status_code == 200:
                self.created_prisoners.remove(prisoner_id)  # Удаляем UUID из списка

    @task(1)  # Генерация отчета (вес = 1)
    def generate_report(self):
        self.client.get("/reports/file", name="/reports/file")

    @task(1)  # Проксирование отчетов (вес = 1)
    def proxy_reports(self):
        path_data = {
            "path": "rep"
        }
        self.client.post("/reports_by_path/", json=path_data)