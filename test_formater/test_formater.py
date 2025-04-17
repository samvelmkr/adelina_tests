import os
import json
import csv
import argparse

from openpyxl import Workbook


HEADERS = [
    "id", "test_id", "interval_id", "number",
    "quiz", "image", "title_secondy", "type",
    "answers", "answer", "columns", "asnwer_checkes", "sort"
]

def to_unicode_escape(text):
    """Преобразует текст в Unicode-эскейпы."""
    return text.encode('unicode_escape').decode('utf-8')

def format_answers(answers, correct_answers):
    """Формирует JSON-ответы в нужном формате (с кодировкой)."""
    formatted = {}
    
    for i, answer in enumerate(answers, start=1):
        formatted[str(i)] = {
            "title": to_unicode_escape(answer),  # Кодируем в Unicode
            "status": "1" if answer in correct_answers else "0"
        }
    
    return json.dumps(formatted, ensure_ascii=False)  # JSON без двойного эскейпа

def append_to_file(entry, json_path, quiz_type: str):
    with open(json_path[:-5] + "-" + quiz_type + ".txt", "a") as extra_quiz_file:
        extra_quiz_file.write(str(entry) + "\n")

def process_json_file(json_path, start_id, test_id):
    """Читает NDJSON и формирует данные для Excel."""
    rows = []
   
    counter = 1
    with open(json_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                entry = json.loads(line.strip())
            except Exception as e:
                print(line)
                print(line.strip())
                print(str(e))
                continue

            quiz = entry.get("quiz", "")  # Вопрос
            answers = entry.get("answers", [])  # Варианты ответов
            correct_answers = entry.get("correct_answers", [])  # Правильные

            formatted_answers = format_answers(answers, correct_answers)

            # Определяем тип теста
            test_type = 1
            if entry.get("matching_answers"):
                test_type = 2  # Соответствия
                append_to_file(entry, json_path, "соответствия")
                #print(f" --> Соответствия: {entry}")
                continue

            if entry.get("image"):
                append_to_file(entry, json_path, "рисунки")
                #print(f" --> Рисунки: {entry}")
                continue


            if len(answers) == 0 and len(correct_answers) != 0:
                test_type = 5 # Развернутый
                formatted_answers = '{"1":{"title":"","status":"0"},"2":{"title":"","status":"0"},"3":{"title":"","status":"0"},"4":{"title":"","status":"0"},"5":{"title":"","status":"0"},"6":{"title":"","status":"0"},"7":{"title":"","status":"0"},"8":{"title":"","status":"0"}}'
            if test_type == 1:
                answer_field = "" 
            elif test_type == 2:
                answer_field = f'{", ".join(map(to_unicode_escape, entry.get("matching_answers")))}'
            else:
                answer_field = f'{", ".join(correct_answers)}'

            row = [
                counter + start_id, test_id, "", counter,  # id, test_id, interval_id, number (пустые)
                quiz, "", "", test_type,  # Вопрос, image(пусто), title_secondy(пусто), тип теста
                formatted_answers, answer_field, "", "", ""  # Ответы, правильный ответ, пустые столбцы
            ]
            rows.append(row)
            counter += 1
    
    return rows

def save_to_excel(filename, data):
    """Сохраняет данные в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)

    for row in data:
        ws.append(row)

    wb.save(filename)
    print(f"✅ Файл сохранен: {filename}")


def save_to_csv(filename, data):

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)
        writer.writerows(data)
    print(f"✅ Файл сохранен: {filename}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["xlsx", "csv"], default="csv", help="Выходной формат файла")
    parser.add_argument("--start-id", type=int, default=1, help="Начальный ID для вопросов")
    parser.add_argument("--start-test-id", type=int, default=1, help="Начальный test_id")
    args = parser.parse_args()

    """Обрабатывает все NDJSON-файлы в папке."""
    json_files = [f for f in os.listdir() if f.endswith(".json")]

    if not json_files:
        print("❌ Нет JSON-файлов в папке.")
        return

    test_id = args.start_test_id
    row_id = args.start_id
    for json_file in json_files:
        print(f"🔄 Обрабатываю: {json_file}")
        data = process_json_file(json_file, row_id, test_id)

        out_file_name = json_file.replace(".json", f".{args.format}")
        if args.format == "xlsx":
            save_to_excel(out_file_name, data)
        else:
            save_to_csv(out_file_name, data)

        test_id += 1

if __name__ == "__main__":
    main()

