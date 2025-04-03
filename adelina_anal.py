from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
import time
import random
import json
import os
import requests

root_dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(root_dir, 'resources')
os.makedirs(resources_dir, exist_ok=True)

# Drivers path
driver_path = os.path.join(root_dir, "geckodriver")
service = Service(executable_path=driver_path)
driver = webdriver.Firefox(service=service)

username = "логин"
password = "пароль"

wait = WebDriverWait(driver, 15)

def login():
    driver.get("https://www.adelina.space/login.aspx")

    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Вход')]"))
    )
    login_button.click()

    wait.until(EC.presence_of_element_located((By.ID, "Login1_UserName")))

    username_field = driver.find_element(By.ID, "Login1_UserName")
    password_field = driver.find_element(By.ID, "Login1_Password")

    username_field.send_keys(username)
    password_field.send_keys(password)

    submit_button = driver.find_element(By.ID, "Login1_LoginButton")
    submit_button.click()

    print("Login attempt completed!")

def navigate_to_emulator():
    # Navigate to "Эмулятор"
    emulator_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-tooltip='Эмулятор']"))
    )
    emulator_button.click()

    input("Press enter to continue...")

    # Start the test
    start_button = wait.until(
        EC.element_to_be_clickable((By.ID, "button1"))
    )
    start_button.click()

def append_to_json_file(filename, data):
    with open(filename, "a", encoding="utf-8") as json_file:
        for entry in data:
            json_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_unique_filename(directory, filename):
    """
    Generates a unique filename if the file already exists in the given directory.
    """
    base_name, ext = os.path.splitext(filename)
    unique_name = filename
    counter = 1
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{base_name}_{counter}{ext}"
        counter += 1
    return unique_name

def save_image(image_url, save_path):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"Failed to download image: {image_url}")

def process_question_with_image_answers():
    # Извлекаем текст вопроса
    quiz_text = driver.find_element(By.ID, "q").text.strip()
    
    # Нажимаем "Ответить", чтобы появились картинки
    # answer_button = driver.find_element(By.ID, "ButtonSub2")  # Подставь реальный ID кнопки
    # answer_button.click()
    # time.sleep(2)  # Даем время подгрузить элементы
    
    # Ищем все варианты ответа (изображения)
    answer_elements = driver.find_elements(By.CSS_SELECTOR, "div.col img")
    
    answers = []
    correct_answers = []

    for img in answer_elements:
        image_src = img.get_attribute("src")
        img_class = img.get_attribute("class")

        if not image_src:
            raise ValueError("Not found image src")

        # Ensure unique filename
        image_filename = os.path.basename(image_src)
        downloaded_filename = get_unique_filename(resources_dir, image_filename)
        save_path = os.path.join(resources_dir, downloaded_filename)
        save_image(image_src, save_path)

        answers.append(downloaded_filename)

        if "text-success" in img_class:
            correct_answers.append(downloaded_filename)

    return {
        "quiz": quiz_text,
        "answers": answers,
        "correct_answers": correct_answers,
        "image": "answers"
    }


def start_scrapping():
    quiz_data = []
    counter = 0

    while True:
        if len(quiz_data) % 50 == 0 and len(quiz_data) > 0:
            append_to_json_file("quiz_data.json", quiz_data)
            quiz_data = []

        try:
            counter += 1
            # Wait for the quiz container to load
            wait.until(EC.presence_of_element_located((By.ID, "qqq")))
            time.sleep(2)  # 1 Safety wait

            # Extract the quiz text
            quiz_text = driver.find_element(By.ID, "q").text

            # Check for an image in the quiz
            try:
                image_element = driver.find_element(By.XPATH, "//img[contains(@class, 'materialboxed')]")
                image_src = image_element.get_attribute("src")
                if image_src:
                    # Ensure unique filename
                    image_filename = os.path.basename(image_src)
                    unique_filename = get_unique_filename(resources_dir, image_filename)
                    save_path = os.path.join(resources_dir, unique_filename)
                    save_image(image_src, save_path)
                    image_src = unique_filename
            except Exception:
                image_src = None

            if image_src:
                print("Image_src FOUNDED !! (((")

            # Extract answers
            answers = []
            answer_elements = driver.find_elements(By.XPATH, "//label[contains(@id, 'ca')]")
            for answer in answer_elements:
                answers.append(answer.text)

            # Handle empty sequence exception
            if not answers:
                # Click "Ответить"
                submit_button = driver.find_element(By.ID, "ButtonSub2")
                time.sleep(0.5)
                submit_button.click()

                # Check if it's a "matching" test
                try:
                    # Find all matching answer elements
                    matching_answers = []
                    matching_elements = driver.find_elements(By.XPATH, "//label[contains(@id, 'da')]")
                    for match in matching_elements:
                        matching_answers.append(match.text)

                    if matching_answers:
                        # Save the question data
                        if image_src is None:
                            quiz_data.append({
                                "quiz": quiz_text,
                                "matching_answers": matching_answers,
                            })
                        else:
                            quiz_data.append({
                                "quiz": quiz_text,
                                "matching_answers": matching_answers,
                                "image": image_src
                            })

                        # Skip to the next question
                        next_button = driver.find_element(By.XPATH,
                                                          "//input[@value='ВЕРНО! »>' or @value='НЕВЕРНО! »>']")
                        next_button.click()
                        continue
                except Exception as match_error:
                    print(f"Failed to process matching test: {match_error}")
                    append_to_json_file("quiz_data.json", quiz_data)
                    break

                # Otherwise, handle single answer scenario
                try:
                    time.sleep(1.5)
                    # Extract the correct answer
                    correct_answer = driver.find_element(By.ID, "universalans").text


                    # Save the question data
                    if image_src is None:
                        quiz_data.append({
                            "quiz": quiz_text,
                            "answers": [],
                            "correct_answers": [correct_answer],
                        })
                    else:
                        quiz_data.append({
                            "quiz": quiz_text,
                            "answers": [],
                            "correct_answers": [correct_answer],
                            "image": image_src
                        })

                    # Confirm the answer
                    confirm_button = driver.find_element(By.XPATH, "//input[@value='Подтвердить »>']")
                    time.sleep(1)
                    confirm_button.click()
                    continue
                except Exception as confirm_error:
                    print(f"Failed to handle single answer scenario: {confirm_error}")
                    try:
                        print("Try to find image answers")
                        data = process_question_with_image_answers()
                        quiz_data.append(data)

                        confirm_button = driver.find_element(By.ID, "ButtonSub2")
                        time.sleep(0.5)
                        confirm_button.click()
                        continue
                    except Exception as e:
                        print(f"Failed to find image answers: {e}")
                        append_to_json_file("quiz_data.json", quiz_data)
                        break

            # Select a random answer
            random_choice = random.choice(range(1, len(answers) + 1))

            label_to_click = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, f"ca{random_choice}"))
            )
            
            # Wait for any overlays to disappear
            try:
                WebDriverWait(driver, 5).until(
                    EC.invisibility_of_element((By.ID, "a_processing"))
                )
                # time.sleep(0.1)  # Safety wait after overlay disappears
            except Exception:
                print("No blocking overlay found or timeout waiting for invisibility.")

            # Scroll the label into view and click
            driver.execute_script("arguments[0].scrollIntoView();", label_to_click)
            time.sleep(.5)  # Safety wait
            label_to_click.click()

            # Submit the answer
            submit_button = driver.find_element(By.ID, "ButtonSub2")
            time.sleep(.5)  # Safety wait
            submit_button.click()

            # Wait for the result
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "text-success"))
            )
            time.sleep(0.5)  # Safety wait

            # Extract correct answers
            correct_answers = []
            correct_elements = driver.find_elements(By.CLASS_NAME, "text-success")
            for correct in correct_elements:
                correct_answers.append(correct.text)

            # Save the quiz data
            if image_src is None:
                quiz_data.append({
                    "quiz": quiz_text,
                    "answers": answers,
                    "correct_answers": correct_answers,
                })
            else:
                quiz_data.append({
                    "quiz": quiz_text,
                    "answers": answers,
                    "correct_answers": correct_answers,
                    "image": image_src
                })

            # Go to the next question
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@value='ВЕРНО! »>' or @value='НЕВЕРНО! »>']")
                )
            )
            time.sleep(0.5)  # Safety wait
            next_button.click()

        except Exception as e:
            try:
                print(f">> Test finish? Exception occurred: {e}")
                # Check if "Завершить тест" button is present
                finish_button = driver.find_element(By.ID, "ButtonEnd1")
                if finish_button.is_displayed() and finish_button.get_attribute("value") == "Завершить тест":
                    print("End of test reached. Saving data and finishing.")
                    append_to_json_file("quiz_data.json", quiz_data)
                    break
            except Exception as finish_error:
                print(f"Skipping question due to error: {finish_error} \nTest number: {counter}")
                try:
                    append_to_json_file("quiz_data.json", quiz_data)
                    quiz_data = []

                    # Refresh the references for the buttons
                    submit_button = driver.find_element(By.ID, "ButtonSub2")
                    time.sleep(0.5)  # Safety wait
                    submit_button.click()
                    skip_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//input[@value='НЕВЕРНО! »>' or @value='ВЕРНО! »>']")
                        )
                    )
                    time.sleep(0.5)  # Safety wait
                    skip_button.click()
                except Exception as skip_error:
                    print(f"Failed to skip question: {skip_error} \nTest number: {counter}")
                    break


def main():
    login()
    navigate_to_emulator()
    start_scrapping()
    driver.quit()


if __name__ == "__main__":
    main()
