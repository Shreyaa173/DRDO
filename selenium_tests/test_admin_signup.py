from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time
import random
import os

BASE_URL = "http://localhost:5173"  # change if needed

def generate_unique_email():
    return f"admin{random.randint(1000, 9999)}@test.com"

def test_admin_signup():
    # ✅ General path assuming chromedriver is in the same folder as this script
    CHROMEDRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(f"{BASE_URL}/signup")
        time.sleep(1)

        print("[STEP] Filling admin signup form...")
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='Full Name']").send_keys("Admin Tester")
        email = generate_unique_email()
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("adminpassword123")
        driver.find_element(By.CSS_SELECTOR, "select").send_keys("admin")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("[STEP] Submitted form, waiting for redirect...")

        # ✅ Wait for redirect to 'admin' route
        WebDriverWait(driver, 10).until(
            EC.url_contains("admin")
        )

        current_url = driver.current_url
        print("[INFO] Current URL after signup:", current_url)

        assert "admin" in current_url, "[FAIL] Redirect to admin panel failed"
        print("[SUCCESS] Admin signup successful:", email)

    except Exception as e:
        print("[ERROR] during admin signup test:", str(e))

    finally:
        print("[INFO] Closing browser...")
        driver.quit()

if __name__ == "__main__":
    test_admin_signup()
