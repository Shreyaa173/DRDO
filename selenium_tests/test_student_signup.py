from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import random

BASE_URL = "http://localhost:5173"  # Change if needed

def generate_unique_email():
    return f"student{random.randint(1000, 9999)}@test.com"

def test_student_signup():
    service = Service(r"C:\Users\sachi\DRDO\DRDO_project\selenium_tests\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(f"{BASE_URL}/signup")
        time.sleep(1)

        print("Filling form...")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Full Name']").send_keys("Student Tester")
        email = generate_unique_email()
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("studentpassword123")
        driver.find_element(By.CSS_SELECTOR, "select").send_keys("student")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Submitted form, waiting for redirect...")
        time.sleep(5)

        current_url = driver.current_url
        print("Current URL after signup:", current_url)

        assert "overview" in current_url or "student" in current_url, "Redirect after signup failed"
        print("Student signup successful:", email)

    except Exception as e:
        print("Error during signup test:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_student_signup()
