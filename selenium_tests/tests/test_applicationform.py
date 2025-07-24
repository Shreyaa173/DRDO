from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# === Configuration ===
BASE_URL = "https://drdointernshipapplicationproject.netlify.app"
TEST_EMAIL = "student@gmail.com"
TEST_PASSWORD = "Student@1234"

# Dynamically resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # one level above /tests
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
RESUME_PATH = os.path.join(BASE_DIR, "resume", "PROJECT FILE.pdf")

def test_application_form():
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    try:
        if not os.path.isfile(RESUME_PATH):
            print("Test Failed: Resume file not found at:", RESUME_PATH)
            return

        # Step 1: Login
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(TEST_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/student"))
        print("Logged in successfully")

        # Step 2: Click 'Apply Now'
        apply_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Apply Now')]")))
        apply_now.click()

        # Step 3: Fill form
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        selects = driver.find_elements(By.TAG_NAME, "select")
        Select(selects[0]).select_by_visible_text("Solid State Physics Laboratory (SSPL) - Delhi")
        Select(selects[1]).select_by_visible_text("Summer Research Intern")
        Select(selects[2]).select_by_visible_text("Computer Science & AI")
        Select(selects[3]).select_by_visible_text("6-8 weeks (Industrial Training)")

        driver.find_element(By.CSS_SELECTOR, "input[type='date']").send_keys("2025-08-01")
        driver.find_element(By.TAG_NAME, "textarea").send_keys(
            "I am enthusiastic about contributing to national defence through research at DRDO."
        )

        # Step 4: Upload resume
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(RESUME_PATH)

        # Step 5: Submit
        driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Application')]").click()

        # Step 6: Handle alert (if present)
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print("Alert:", alert.text)
            alert.accept()
        except:
            print("No alert appeared")

        print("Application Form Submitted Successfully")

    except Exception as e:
        print("Test Failed:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_application_form()
