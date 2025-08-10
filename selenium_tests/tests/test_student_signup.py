from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import random

BASE_URL = "https://drdointernshipapplicationproject.netlify.app"

def generate_unique_email():
    return f"student{random.randint(1000, 9999)}@test.com"

def test_student_signup():
    # Use portable path to chromedriver
    CHROMEDRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chromedriver.exe")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    try:
        print("[STEP] Opening signup page...")
        driver.get(f"{BASE_URL}/signup")

        print("[STEP] Filling signup form...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Full Name']"))).send_keys("Student Tester")
        email = generate_unique_email()
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("studentpassword123")
        driver.find_element(By.CSS_SELECTOR, "select").send_keys("student")

        print("[STEP] Submitting form...")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait until redirected to student dashboard or overview
        wait.until(EC.url_contains("student"))
        print("[SUCCESS] Student signup successful.")
        print("Registered email:", email)
        print("Current URL:", driver.current_url)

    except Exception as e:
        print("[ERROR] Signup test failed:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_student_signup()
