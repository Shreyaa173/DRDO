import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configuration
BASE_URL = "https://drdointernshipapplicationproject.netlify.app"  # Frontend base URL
ADMIN_USERNAME = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@1234"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "test_downloads")

class TestResumeDownload:
    @classmethod
    def setup_class(cls):
        chrome_options = Options()
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 15)

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
        # Optional cleanup
        for file in os.listdir(DOWNLOAD_DIR):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, file))
            except Exception as e:
                print(f"Error deleting file: {e}")

    def wait_for_pdf_download(self, timeout=15):
        for _ in range(timeout):
            files = os.listdir(DOWNLOAD_DIR)
            if any(file.endswith(".pdf") for file in files):
                return True
            time.sleep(1)
        return False

    def login_as_admin(self):
        self.driver.get(f"{BASE_URL}/login")

        email_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[text()='Email']/following-sibling::input"))
        )
        email_input.send_keys(ADMIN_USERNAME)

        password_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[text()='Password']/following-sibling::div/input"))
        )
        password_input.send_keys(ADMIN_PASSWORD)

        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(text(), 'Admin Dashboard')]"))
        )

    def test_resume_download(self):
        self.login_as_admin()

        # Navigate to Applications
        applications_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Applications']/ancestor::button"))
        )
        applications_btn.click()

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(text(), 'Applications Management')]"))
        )

        # Find all Download Resume links
        download_links = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'Download Resume')]"))
        )

        assert download_links, "❌ No 'Download Resume' links found."

        # Click the first one
        first_link = download_links[0]
        app_row = first_link.find_element(By.XPATH, "./ancestor::tr")
        student_name = app_row.find_element(By.XPATH, ".//td[1]//div[1]").text
        position = app_row.find_element(By.XPATH, ".//td[2]").text

        print(f"🔍 Downloading resume for {student_name} - {position}")
        first_link.click()

        # ✅ Wait for download to complete
        assert self.wait_for_pdf_download(), "❌ Resume PDF was not downloaded."

        downloaded_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".pdf")]
        assert downloaded_files, "❌ No PDF found after clicking download."

        downloaded_file = downloaded_files[0]
        file_path = os.path.join(DOWNLOAD_DIR, downloaded_file)
        assert os.path.getsize(file_path) > 0, "❌ Downloaded file is empty."

        print(f"✅ Resume downloaded successfully: {downloaded_file}")

if __name__ == "__main__":
    test = TestResumeDownload()
    test.setup_class()
    try:
        test.test_resume_download()
    finally:
        test.teardown_class()

