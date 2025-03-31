import time
import requests
from bs4 import BeautifulSoup
# import pandas as pd

LOGIN_URL = "https://www.adelina.space/login.aspx"
EMULATOR_URL = "https://www.adelina.space/emulator.aspx"
username = "Альберт"
password = "gustax-guvrof-Zipru8"


session = requests.Session()

def main():    
    login_payload = {
        "username": username,
        "password": password
    }
    response = session.post(LOGIN_URL, data=login_payload)
    if response.status_code == 200:
        print("Successfully logined.")
    else:
        print("LOgin failed")
        exit()

    # Some delay
    time.sleep(2)

    # Переход на страницу эмулятора
    response = session.get(EMULATOR_URL)
    if response.status_code == 200:
        print("Successfully selected emulator.")
    else:
        print("emulator failed")
        exit()

    soup = BeautifulSoup(response.text, 'html.parser')


    # Нажатие на кнопку "Поехали"
    start_test_button = soup.find("a", href="emulator.aspx")
    if start_test_button:
        test_url = "https://www.adelina.space/" + start_test_button['href']
        response = session.get(test_url)
#     
#         # Здесь нужно изучить запросы и ответы на действия пользователя
#         # Выбор вариантов ответов, переход к следующему вопросу
#         # Это можно сделать с помощью браузера и доработать код ниже.
#     
#         # Пример структуры данных
#         questions_data = []
#     
#         # Пример записи вопроса
#         question = {
#             "number": 1,
#             "quiz": "Пример текста вопроса",
#             "type": 1,
#             "answers": '{"1": {"title": "ответ 1", "status": "0"}, "2": {"title": "ответ 2", "status": "1"}}'
#         }
#         questions_data.append(question)
#     
#         # Экспорт в Excel
#         df = pd.DataFrame(questions_data)
#         df.to_excel("questions.xlsx", index=False)
#         print("Данные сохранены в файл questions.xlsx")
#     else:
#         print("Кнопка 'Поехали' не найдена.")
    

if __name__ == '__main__':
    main()
