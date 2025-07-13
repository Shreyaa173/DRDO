from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# === Configuration ===
BASE_URL = "http://localhost:5173"
TEST_EMAIL = "anshikafb1506@gmail.com"
TEST_PASSWORD = "12345"
RESUME_PATH = "C:\\Users\\sachi\\Documents\\assignment bee.pdf"  # ✅ Ensure this is correct
CHROMEDRIVER_PATH = "C:\\Users\\sachi\\DRDO\\DRDO_Project\\selenium_tests\\chromedriver.exe"

def test_application_form():
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    try:
        # Check if the file exists before proceeding
        if not os.path.isfile(RESUME_PATH):
            print("Test Failed: Resume file not found at:", RESUME_PATH)
            driver.quit()
            return

        # 1. Login
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(TEST_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/student"))
        print("Logged in successfully")
        print("Current URL after login:", driver.current_url)

        # 2. Wait for sidebar menu and click "Apply Now"
        print("Waiting for 'Apply Now' menu item...")
        apply_now_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Apply Now')]"))
        )
        time.sleep(1)
        apply_now_button.click()
        print("Clicked 'Apply Now'")

        # 3. Wait for form modal to appear
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        time.sleep(1)

        # 4. Fill the form
        selects = driver.find_elements(By.TAG_NAME, "select")
        Select(selects[0]).select_by_visible_text("Solid State Physics Laboratory (SSPL) - Delhi")
        Select(selects[1]).select_by_visible_text("Summer Research Intern")
        Select(selects[2]).select_by_visible_text("Computer Science & AI")
        Select(selects[3]).select_by_visible_text("6-8 weeks (Industrial Training)")

        # 5. Expected start date
        driver.find_element(By.CSS_SELECTOR, "input[type='date']").send_keys("2025-08-01")

        # 6. Cover letter
        driver.find_element(By.TAG_NAME, "textarea").send_keys(
            "I am enthusiastic about contributing to national defence through research at DRDO."
        )

        # 7. Upload Resume
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(RESUME_PATH)
        print("Resume uploaded:", RESUME_PATH)

        time.sleep(1)

        # 8. Submit the form
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Application')]")
        submit_button.click()
        print("Submitted application")

        # 9. Handle alert (optional)
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print("Submission Alert:", alert.text)
            alert.accept()
        except:
            print("No alert appeared — assuming inline confirmation")

        print("Application Form Submitted Successfully")

    except Exception as e:
        print("Test Failed:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_application_form()
