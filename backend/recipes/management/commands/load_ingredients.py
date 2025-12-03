import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON файла'

    def handle(self, *args, **options):
        # Путь к файлу. Предполагается, что папка data лежит в корне backend
        file_path = os.path.join(settings.BASE_DIR, 'ingredients.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return

        self.stdout.write(f'Загрузка ингредиентов из {file_path}...')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ingredients_to_create = []
            for item in data:
                # Создаем объект, но пока не сохраняем в БД
                ingredient = Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                ingredients_to_create.append(ingredient)

            # bulk_create вставляет список объектов одним запросом (это очень быстро)
            # ignore_conflicts=True пропускает дубликаты, если они уже есть в БД
            Ingredient.objects.bulk_create(ingredients_to_create, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(f'Успешно загружено {len(ingredients_to_create)} ингредиентов'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при загрузке: {e}'))