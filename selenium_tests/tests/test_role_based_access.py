import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoAlertPresentException,
    TimeoutException
)


class TestRoleBasedAccess:
    @classmethod
    def setup_class(cls):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")  # or "--headless" for older Chrome
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # 👇 Disable password manager popup
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,  # block notifications
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_setting_values.media_stream": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        cls.driver = webdriver.Chrome(options=chrome_options)

        cls.driver.set_page_load_timeout(30)
        cls.wait = WebDriverWait(cls.driver, 20)

        cls.admin_username = "admin@gmail.com"
        cls.admin_password = "Admin@1234"
        cls.student_username = "student@gmail.com"
        cls.student_password = "Student@1234"
        cls.base_url = "https://drdointernshipapplicationproject.netlify.app"

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()

    def take_screenshot(self, name):
        self.driver.save_screenshot(f"screenshot_{name}.png")

    def dismiss_alerts(self):
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except NoAlertPresentException:
            pass

    def login(self, email, password):
        self.driver.get(f"{self.base_url}/login")
        self.dismiss_alerts()
        self.wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

        try:
            email_input = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
            )
            password_input = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
            )
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )

            email_input.clear()
            password_input.clear()
            email_input.send_keys(email)
            password_input.send_keys(password)
            login_button.click()

            time.sleep(1.5)  # Allow redirection
        except Exception:
            self.take_screenshot("login_failure")
            raise

    def login_as_admin(self):
        print("Attempting admin login...")
        self.login(self.admin_username, self.admin_password)
        print("Admin login submitted, now checking for /admin route")

        try:
            # Wait for the URL to contain "/admin"
            self.wait.until(EC.url_contains("/admin"))
            print("✅ URL contains '/admin', now checking for dashboard heading...")

            # Wait for the dashboard heading to appear
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-dashboard-title']"))
            )
            print("✅ Admin dashboard heading found.")
        except TimeoutException:
            print("❌ Timeout: Admin login failed or dashboard did not load in time.")
            self.take_screenshot("admin_login_failure")
            raise


    def login_as_student(self):
        self.login(self.student_username, self.student_password)
        try:
            self.wait.until(EC.url_contains("/student"))
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='student-dashboard-title']"))
            )
        except TimeoutException:
            self.take_screenshot("student_login_failure")
            raise

    def logout(self):
        try:
            self.dismiss_alerts()
            logout_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Logout')]/ancestor::button"))
            )
            try:
                logout_btn.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", logout_btn)

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
            )
        except Exception:
            self.take_screenshot("logout_failure")
            raise

    def test_student_cannot_access_admin_routes(self):
        self.login_as_student()
        admin_routes = ["/admin", "/admin/applications", "/admin/notifications", "/admin/profile"]

        for route in admin_routes:
            self.driver.get(f"{self.base_url}{route}")
            try:
                self.wait.until(EC.url_contains("/student"))
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='student-dashboard-title']"))
                )
                assert "/student" in self.driver.current_url, f"❌ Student was not redirected from {route}"
                print(f"✅ Student blocked from {route}")
            except Exception:
                self.take_screenshot(f"student_access_{route.replace('/', '_')}")
                raise

        self.logout()

    def test_admin_cannot_access_student_routes(self):
        self.login_as_admin()
        student_routes = [
            "/student", "/student/applications", "/student/apply",
            "/student/notifications", "/student/profile"
        ]

        for route in student_routes:
            self.driver.get(f"{self.base_url}{route}")
            try:
                self.wait.until(EC.url_contains("/admin"))
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-dashboard-title']"))
                )
                assert "/admin" in self.driver.current_url, f"❌ Admin was not redirected from {route}"
                print(f"✅ Admin blocked from {route}")
            except Exception:
                self.take_screenshot(f"admin_access_{route.replace('/', '_')}")
                raise

        self.logout()

    def test_unauthenticated_access_redirects_to_login(self):
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        time.sleep(1)

        protected_routes = [
            "/admin", "/admin/applications", "/admin/notifications", "/admin/profile",
            "/student", "/student/applications", "/student/apply", "/student/notifications", "/student/profile"
        ]

        for route in protected_routes:
            self.driver.get(f"{self.base_url}{route}")
            try:
                self.wait.until(EC.url_contains("/login"))
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
                )
                assert "/login" in self.driver.current_url, f"❌ Unauthorized access to {route} not redirected"
                print(f"✅ Unauthenticated access to {route} redirected to login")
            except Exception:
                self.take_screenshot(f"unauth_access_{route.replace('/', '_')}")
                raise

    def test_role_specific_redirect_after_login(self):
        self.login_as_admin()
        try:
            self.wait.until(EC.url_contains("/admin"))
            assert "/admin" in self.driver.current_url, "❌ Admin not redirected to admin dashboard"
            import logging
            logging.basicConfig(level=logging.INFO)
            logging.info("✅ Admin redirected to Admin Dashboard")

        except AssertionError:
            self.take_screenshot("admin_redirect_failure")
            raise
        finally:
            self.logout()

        self.login_as_student()
        try:
            self.wait.until(EC.url_contains("/student"))
            assert "/student" in self.driver.current_url, "❌ Student not redirected to student dashboard"
            print("✅ Student redirected to Student Dashboard")
        except AssertionError:
            self.take_screenshot("student_redirect_failure")
            raise
        finally:
            self.logout()


if __name__ == "__main__":
    test = TestRoleBasedAccess()
    test.setup_class()
    try:
        test.test_student_cannot_access_admin_routes()
        test.test_admin_cannot_access_student_routes()
        test.test_unauthenticated_access_redirects_to_login()
        test.test_role_specific_redirect_after_login()
    finally:
        test.teardown_class()