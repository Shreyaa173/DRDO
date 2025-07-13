from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://localhost:5173"
CHROMEDRIVER_PATH = r"C:\Users\sachi\DRDO\DRDO_project\selenium_tests\chromedriver.exe"
TEST_EMAIL = "student9203@test.com"
TEST_PASSWORD = "studentpassword123"

def test_profile_creation():
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("[STEP 1] Logging in...")
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        print("[STEP 2] Opening profile page...")
        driver.get(f"{BASE_URL}/student/profile")
        time.sleep(2)

        print("[STEP 3] Clicking Edit Profile...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Edit Profile']]"))
        ).click()
        time.sleep(1)

        print("[STEP 4] Filling profile fields...")
        driver.find_element(By.XPATH, "//input[@placeholder='e.g. IGDTUW']").clear()
        driver.find_element(By.XPATH, "//input[@placeholder='e.g. IGDTUW']").send_keys("IGDTUW")

        driver.find_element(By.XPATH, "//input[@placeholder='e.g. Computer Science']").clear()
        driver.find_element(By.XPATH, "//input[@placeholder='e.g. Computer Science']").send_keys("CSE")

        Select(driver.find_element(By.XPATH, "//select")).select_by_visible_text("3rd Year")

        print("[STEP 5] Saving profile...")
        driver.find_element(By.XPATH, "//button[span[text()='Save']]").click()
        time.sleep(2)

        print("[SUCCESS] Profile updated successfully.")

    except Exception as e:
        print("[ERROR]", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_profile_creation()
