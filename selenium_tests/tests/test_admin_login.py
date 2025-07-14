from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Configuration ===
BASE_URL = "http://localhost:5173"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@1234"

def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print("[ERROR] Failed to initialize ChromeDriver:", e)
        return None

def login_admin(driver, wait):
    """Login as admin"""
    try:
        driver.get(f"{BASE_URL}/login")

        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.clear()
        email_field.send_keys(ADMIN_EMAIL)

        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(ADMIN_PASSWORD)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        wait.until(EC.url_contains("/admin"))
        print("[PASS] Admin login successful")
        return True

    except Exception as e:
        print("[FAIL] Admin login failed:", e)
        return False

def test_admin_login():
    """Run the admin login test"""
    print("[INFO] Starting Admin Login Test...")
    driver = setup_driver()
    if not driver:
        return

    wait = WebDriverWait(driver, 20)

    try:
        result = login_admin(driver, wait)
        if result:
            print("[INFO] Admin login test passed")
        else:
            print("[INFO] Admin login test failed")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_admin_login()
