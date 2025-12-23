# debug_profile_test.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Удаляем старых пользователей если есть
User.objects.filter(username__in=['testuser', 'anotheruser']).delete()

# Создаем тестовых пользователей
user = User.objects.create_user(username='testuser', password='testpass123')
another_user = User.objects.create_user(username='anotheruser', password='testpass123')

# Создаем клиенты
user_client = Client()
user_client.login(username='testuser', password='testpass123')

another_user_client = Client()
another_user_client.login(username='anotheruser', password='testpass123')

unlogged_client = Client()

# Получаем страницы
user_url = f'/profile/{user.username}/'
print(f"Getting URL: {user_url}")

# Получаем ответы
user_response = user_client.get(user_url)
another_response = another_user_client.get(user_url)
unlogged_response = unlogged_client.get(user_url)

# Сохраняем HTML
with open('user_own_profile.html', 'w') as f:
    f.write(user_response.content.decode())

with open('another_user_profile.html', 'w') as f:
    f.write(another_response.content.decode())

with open('unlogged_profile.html', 'w') as f:
    f.write(unlogged_response.content.decode())

print(f"\n=== USER viewing OWN profile ===")
print(f"Status: {user_response.status_code}")
html_user = user_response.content.decode()

print(f"\n=== ANOTHER USER viewing profile ===")
print(f"Status: {another_response.status_code}")
html_another = another_response.content.decode()

print(f"\n=== UNLOGGED viewing profile ===")
print(f"Status: {unlogged_response.status_code}")
html_unlogged = unlogged_response.content.decode()

# Проверяем ключевые элементы
print("\n=== АНАЛИЗ ССЫЛОК ===")

# Ищем ссылки в HTML пользователя
import re

# Ищем все ссылки
links_user = re.findall(r'href=[\'"]?([^\'" >]+)', html_user)
links_another = re.findall(r'href=[\'"]?([^\'" >]+)', html_another)

print(f"\nСсылки на странице владельца ({len(links_user)}):")
for link in sorted(set(links_user)):
    print(f"  {link}")

print(f"\nСсылки на странице другого пользователя ({len(links_another)}):")
for link in sorted(set(links_another)):
    print(f"  {link}")

# Ищем конкретные ссылки
print("\n=== ПОИСК КОНКРЕТНЫХ ССЫЛОК ===")

# Ищем ссылку на редактирование профиля
edit_profile_patterns = ['edit_profile', 'Редактировать профиль']
for pattern in edit_profile_patterns:
    if pattern in html_user.lower():
        print(f"✓ Нашел '{pattern}' на странице владельца")
    if pattern in html_another.lower():
        print(f"✗ Нашел '{pattern}' на странице другого пользователя (не должно быть!)")

# Ищем ссылку на изменение пароля
password_patterns = ['password_change', 'Изменить пароль']
for pattern in password_patterns:
    if pattern in html_user.lower():
        print(f"✓ Нашел '{pattern}' на странице владельца")
    if pattern in html_another.lower():
        print(f"✗ Нашел '{pattern}' на странице другого пользователя (не должно быть!)")

print("\n=== РАЗНИЦА МЕЖДУ СТРАНИЦАМИ ===")
diff_links = set(links_user) - set(links_another)
if diff_links:
    print(f"Найдено {len(diff_links)} уникальных ссылок на странице владельца:")
    for link in diff_links:
        print(f"  {link}")
else:
    print("Нет уникальных ссылок на странице владельца!")

print("\nФайлы сохранены: user_own_profile.html, another_user_profile.html, unlogged_profile.html")