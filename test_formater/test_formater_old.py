import os
import json
from openpyxl import Workbook

# Заголовки в Excel
HEADERS = [
    "id", "test_id", "interval_id", "number", 
    "quiz", "title_secondy", "type", 
    "answers", "answer", "columns", "asnwer_checkes"
]

def format_answers(answers, correct_answers):
    """Преобразует список ответов в нужный JSON-формат для Excel."""
    formatted = {}
    
    for i, answer in enumerate(answers, start=1):
        formatted[str(i)] = {
            "title": answer,  # Сам ответ
            "status": "1" if answer in correct_answers else "0"  # Отмечаем правильный
        }
    
    return json.dumps(formatted, ensure_ascii=False)  # Без Unicode-эскейпов

def process_json_file(json_path):
    """Читает NDJSON-файл и формирует данные для Excel."""
    rows = []
    
    with open(json_path, "r", encoding="utf-8") as file:
        for line in file:
            entry = json.loads(line.strip())  # Читаем как JSON-объект
            
            quiz = entry.get("quiz", "")  # Вопрос
            answers = entry.get("answers", [])  # Варианты ответов
            correct_answers = entry.get("correct_answers", [])  # Правильные
            
            formatted_answers = format_answers(answers, correct_answers)

            # Определяем тип теста (в большинстве случаев это 1)
            test_type = 1
            if entry.get("matching_answers"):
                test_type = 2  # Если есть matching_answers, значит соответствия
            
            row = [
                "", "", "", "",  # id, test_id, interval_id, number (можно заполнить вручную)
                quiz, "", test_type,  # Вопрос, пустой столбец, тип теста
                formatted_answers, ", ".join(correct_answers), "", ""  # Ответы, правильный ответ, пустые столбцы
            ]
            rows.append(row)
    
    return rows

def save_to_excel(filename, data):
    """Сохраняет данные в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)  # Заголовки

    for row in data:
        ws.append(row)

    wb.save(filename)
    print(f"✅ Файл сохранен: {filename}")

def main():
    """Обрабатывает все NDJSON-файлы в текущей папке."""
    json_files = [f for f in os.listdir() if f.endswith(".json")]
    
    if not json_files:
        print("❌ Нет JSON-файлов в текущей папке.")
        return

    for json_file in json_files:
        print(f"🔄 Обрабатываю: {json_file}")
        excel_filename = json_file.replace(".json", ".xlsx")
        data = process_json_file(json_file)
        save_to_excel(excel_filename, data)
        break

if __name__ == "__main__":
    main()

