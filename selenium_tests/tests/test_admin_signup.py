from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import random

BASE_URL = "https://drdointernshipapplicationproject.netlify.app"

def generate_unique_email():
    return f"admin{random.randint(1000, 9999)}@test.com"

def get_chromedriver_path():
    # Go up one level from tests/ to selenium_tests/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "chromedriver.exe")

def test_admin_signup():
    chromedriver_path = get_chromedriver_path()
    print(f"[DEBUG] Chromedriver path: {chromedriver_path}")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(f"{BASE_URL}/signup")
        print("[STEP] Filling admin signup form...")

        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Full Name']").send_keys("Admin Tester")
        email = generate_unique_email()
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("adminpassword123")
        driver.find_element(By.CSS_SELECTOR, "select").send_keys("admin")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("[STEP] Submitted form, waiting for redirect...")

        WebDriverWait(driver, 10).until(EC.url_contains("admin"))

        current_url = driver.current_url
        print("[INFO] Current URL after signup:", current_url)

        assert "admin" in current_url, "[FAIL] Redirect to admin panel failed"
        print("[SUCCESS] Admin signup successful:", email)

    except Exception as e:
        print("[ERROR] during admin signup test:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_admin_signup()
