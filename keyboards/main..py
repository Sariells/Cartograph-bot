import json

keyboard_config = {
    "main": {
        "button1": "Помощь"
    },
    "inline": {
        "city1": "Город 1",
        "city2": "Город 2"
    }
}

# Сохраняем конфигурацию клавиатуры в файл
with open('keyboards/main_keyboard.json', 'w', encoding='utf-8') as f:
    json.dump(keyboard_config, f, ensure_ascii=False, indent=4)