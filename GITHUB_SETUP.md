# GitHub Setup для AutoCLI

Агент теперь может пушить в ваш репозиторий: https://github.com/ncreasor/CLIAgent

## Настройка авторизации

### Вариант 1: Personal Access Token (рекомендуется)

1. Перейдите: https://github.com/settings/tokens
2. Нажмите "Generate new token" → "Generate new token (classic)"
3. Выберите права:
   - ✅ `repo` (полный доступ к репозиториям)
4. Скопируйте токен

5. Настройте git для использования токена:
```bash
cd autocli
git remote set-url origin https://YOUR_TOKEN@github.com/ncreasor/CLIAgent.git
```

### Вариант 2: SSH ключ

1. Создайте SSH ключ (если нет):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Добавьте ключ в GitHub:
   - Скопируйте содержимое `~/.ssh/id_ed25519.pub`
   - Перейдите: https://github.com/settings/keys
   - Нажмите "New SSH key"
   - Вставьте ключ

3. Измените URL на SSH:
```bash
cd autocli
git remote set-url origin git@github.com:ncreasor/CLIAgent.git
```

## Проверка

После настройки агент сможет выполнять:

```bash
git push origin main
```

## Для агента

Когда будешь готов пушить изменения:

```python
# Используй git tool
git add .
git commit -m "feat: your improvement description"
git push origin main
```

Или через bash tool:
```bash
cd /path/to/autocli
git add .
git commit -m "feat: improvement"
git push origin main
```

## Текущий статус
- ✅ Git инициализирован
- ✅ Remote добавлен: https://github.com/ncreasor/CLIAgent.git
- ✅ Ветка: main
- ⏳ Требуется: настройка авторизации (токен или SSH)
