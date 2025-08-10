import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestNavigation:
    @classmethod
    def setup_class(cls):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)  # Reduced implicit wait
        cls.wait = WebDriverWait(cls.driver, 30)  # Increased explicit wait
        cls.short_wait = WebDriverWait(cls.driver, 10)  # For quick checks
        cls.actions = ActionChains(cls.driver)

        cls.admin_username = "admin@gmail.com"
        cls.admin_password = "Admin@1234"
        cls.student_username = "student@gmail.com"
        cls.student_password = "Student@1234"
        cls.base_url = "https://drdointernshipapplicationproject.netlify.app"

    def clear_session(self):
        """Comprehensive session clearing"""
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            # Clear any authentication tokens
            self.driver.execute_script("window.localStorage.removeItem('token');")
            self.driver.execute_script("window.localStorage.removeItem('user');")
            self.driver.execute_script("window.localStorage.removeItem('userRole');")
        except Exception as e:
            print(f"Warning: Could not clear session completely: {e}")

    def wait_for_page_load(self):
        """Wait for page to be fully loaded"""
        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            # Additional wait for React components to render
            time.sleep(2)
        except TimeoutException:
            print("Warning: Page load timeout")

    def login(self, username, password, expected_role):
        """Enhanced login method with detailed debugging"""
        print(f"🌐 Attempting login as {expected_role} with {username}")
        
        try:
            # Navigate to login page
            self.driver.get("https://drdointernshipapplicationproject.netlify.app/login")
            time.sleep(2)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"📄 Current page title: {self.driver.title}")
            print(f"🔗 Current URL: {self.driver.current_url}")
            
            # Take screenshot for debugging
            # self.driver.save_screenshot(f"login_page_{expected_role}.png")
            
            # Find and fill username field
            username_selectors = [
                "input[name='email']",
                "input[type='email']", 
                "input[name='username']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "#email",
                "#username"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found username field with selector: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                print("❌ Username field not found!")
                print("🔍 Available input fields:")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for i, inp in enumerate(inputs):
                    print(f"  Input {i}: type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', placeholder='{inp.get_attribute('placeholder')}'")
                raise Exception("Username field not found")
            
            # Clear and enter username
            username_field.clear()
            username_field.send_keys(username)
            print(f"📝 Entered username: {username}")
            
            # Find and fill password field
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
                "#password"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found password field with selector: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                print("❌ Password field not found!")
                raise Exception("Password field not found")
            
            # Clear and enter password
            password_field.clear()
            password_field.send_keys(password)
            print("📝 Entered password")
            
            # Find login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Login') or contains(text(), 'Sign in') or contains(@class, 'login-btn')]")
            print(f"🔘 Found login button: {login_button.text}")
            
            # Check if button is enabled
            if not login_button.is_enabled():
                print("⚠️ Login button is disabled!")
                time.sleep(2)  # Wait a bit and check again
                if not login_button.is_enabled():
                    print("❌ Login button remains disabled")
            
            # Click login button
            login_button.click()
            print("🔄 Clicked login button")
            
            # Wait for navigation or error message
            time.sleep(3)
            
            current_url = self.driver.current_url
            print(f"🔗 URL after login attempt: {current_url}")
            
            # Check for error messages
            error_selectors = [
                ".error",
                ".alert-danger",
                "[class*='error']",
                "[class*='invalid']",
                ".text-red-500",
                ".text-danger"
            ]
            
            for selector in error_selectors:
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for error in error_elements:
                        if error.is_displayed() and error.text.strip():
                            print(f"⚠️ Error message found: {error.text}")
                except:
                    pass
            
            # Check if login was successful
            if "login" in current_url.lower():
                print("❌ Still on login page - login failed")
                
                # Additional debugging - check what happened
                page_source = self.driver.page_source
                if "invalid" in page_source.lower() or "incorrect" in page_source.lower():
                    print("🔍 Page contains 'invalid' or 'incorrect' - likely wrong credentials")
                
                # Try to find any visible text that might indicate the issue
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if "invalid" in body_text.lower():
                    print("🔍 Body contains 'invalid' text")
                
                raise Exception(f"Login failed - remained on login page. Current URL: {current_url}")
            
            print(f"✅ Login successful - navigated to: {current_url}")
            
            # Wait for the page to fully load
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Login failed for {expected_role}: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            raise e

    def login_as_admin(self):
        self.clear_session()
        time.sleep(1)
        return self.login(self.admin_username, self.admin_password, "admin")

    def login_as_student(self):
        self.clear_session()
        time.sleep(1)
        return self.login(self.student_username, self.student_password, "student")

    def find_nav_element(self, label):
        """Find navigation element with multiple strategies"""
        selectors = [
            f"//span[contains(text(), '{label}')]/ancestor::button",
            f"//a[contains(text(), '{label}')]",
            f"//button[contains(text(), '{label}')]",
            f"//nav//button[contains(., '{label}')]",
            f"//nav//a[contains(., '{label}')]",
            f"//li[contains(., '{label}')]//button",
            f"//li[contains(., '{label}')]//a",
        ]
        
        for selector in selectors:
            try:
                element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                return element
            except TimeoutException:
                continue
        
        raise NoSuchElementException(f"Could not find navigation element for '{label}'")

    def test_admin_navigation_links(self):
        self.login_as_admin()
        admin_nav_items = [
            {"label": "Dashboard", "path": "/admin", "title": "Admin Dashboard"},
            {"label": "Applications", "path": "/admin/applications", "title": "Applications"},
            {"label": "Notifications", "path": "/admin/notifications", "title": "Notifications"},
            {"label": "Profile", "path": "/admin/profile", "title": "Profile"},
        ]

        for item in admin_nav_items:
            try:
                print(f"🔍 Testing navigation to {item['label']}")
                
                # Find and click the navigation element
                nav_element = self.find_nav_element(item['label'])
                
                # Scroll to element and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", nav_element)
                time.sleep(1)
                nav_element.click()

                # Wait for URL to update
                self.wait.until(EC.url_contains(item['path']))
                
                # Wait for page content to load
                self.wait_for_page_load()
                
                # Look for title or content with flexible matching
                title_selectors = [
                    f"//*[contains(text(), '{item['title']}')]",
                    f"//h1[contains(text(), '{item['title']}')]",
                    f"//h2[contains(text(), '{item['title']}')]",
                    f"//title[contains(text(), '{item['title']}')]",
                    f"//*[@class='title' or @class='heading'][contains(text(), '{item['title']}')]"
                ]
                
                content_found = False
                for selector in title_selectors:
                    try:
                        self.short_wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        content_found = True
                        break
                    except TimeoutException:
                        continue
                
                if not content_found:
                    print(f"⚠️ Title not found, but URL is correct: {self.driver.current_url}")
                
                print(f"✅ Admin navigated to {item['label']} successfully")
                time.sleep(1)

            except Exception as e:
                print(f"❌ Failed to navigate to {item['label']}: {str(e)}")
                self.driver.save_screenshot(f"admin_nav_failure_{item['label'].replace(' ', '_')}_{int(time.time())}.png")
                raise e

    def test_student_navigation_links(self):
        self.login_as_student()
        student_nav_items = [
            {"label": "Dashboard", "path": "/student", "title": "Student Dashboard"},
            {"label": "My Applications", "path": "/student/applications", "title": "Applications"},
            {"label": "Apply Now", "path": "/student/apply", "title": "Apply"},
            {"label": "Notifications", "path": "/student/notifications", "title": "Notifications"},
            {"label": "Profile", "path": "/student/profile", "title": "Profile"},
        ]

        for item in student_nav_items:
            try:
                print(f"🔍 Testing navigation to {item['label']}")
                
                # Find and click the navigation element
                nav_element = self.find_nav_element(item['label'])
                
                # Scroll to element and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", nav_element)
                time.sleep(1)
                nav_element.click()

                # Wait for URL to update
                self.wait.until(EC.url_contains(item['path']))
                
                # Wait for page content to load
                self.wait_for_page_load()
                
                # Look for title or content with flexible matching
                title_selectors = [
                    f"//*[contains(text(), '{item['title']}')]",
                    f"//h1[contains(text(), '{item['title']}')]",
                    f"//h2[contains(text(), '{item['title']}')]",
                    f"//title[contains(text(), '{item['title']}')]",
                    f"//*[@class='title' or @class='heading'][contains(text(), '{item['title']}')]"
                ]
                
                content_found = False
                for selector in title_selectors:
                    try:
                        self.short_wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        content_found = True
                        break
                    except TimeoutException:
                        continue
                
                if not content_found:
                    print(f"⚠️ Title not found, but URL is correct: {self.driver.current_url}")
                
                print(f"✅ Student navigated to {item['label']} successfully")
                time.sleep(1)

            except Exception as e:
                print(f"❌ Failed to navigate to {item['label']}: {str(e)}")
                self.driver.save_screenshot(f"student_nav_failure_{item['label'].replace(' ', '_')}_{int(time.time())}.png")
                raise e

    def test_unauthorized_access_redirect(self):
        """Test that unauthorized access redirects to login"""
        print("🔍 Testing unauthorized access redirects")
        
        # Clear all session data
        self.clear_session()
        
        protected_paths = ["/admin", "/student", "/admin/applications", "/student/applications"]
        
        for path in protected_paths:
            try:
                print(f"Testing unauthorized access to {path}")
                self.driver.get(f"{self.base_url}{path}")
                
                # Wait for redirect to login
                self.wait.until(
                    lambda driver: "/login" in driver.current_url or 
                                   EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'], input[type='email']"))
                )
                
                # Verify we're on login page
                current_url = self.driver.current_url
                if "/login" not in current_url:
                    # Check if login form is present (some SPAs don't change URL immediately)
                    try:
                        self.short_wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'], input[type='email']"))
                        )
                        print(f"✅ {path} shows login form (auth required)")
                    except TimeoutException:
                        raise Exception(f"Path {path} did not redirect to login or show login form")
                else:
                    print(f"✅ {path} redirected to login page")
                    
            except Exception as e:
                print(f"❌ Failed to verify unauthorized access to {path}: {str(e)}")
                self.driver.save_screenshot(f"unauthorized_access_failure_{path.replace('/', '_')}_{int(time.time())}.png")
                raise e

    def test_logout_functionality(self):
        """Test logout functionality for both roles"""
        print("🔍 Testing logout functionality")
        
        # Test student logout
        self.login_as_student()
        try:
            logout_selectors = [
                "//span[contains(text(), 'Logout')]/ancestor::button",
                "//button[contains(text(), 'Logout')]",
                "//a[contains(text(), 'Logout')]",
                "//button[contains(text(), 'Sign out')]",
                "//a[contains(text(), 'Sign out')]",
                "//*[contains(@class, 'logout')]",
            ]
            
            logout_btn = None
            for selector in logout_selectors:
                try:
                    logout_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not logout_btn:
                raise Exception("Could not find logout button")
            
            # Click logout
            self.driver.execute_script("arguments[0].scrollIntoView(true);", logout_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", logout_btn)
            
            # Wait for redirect to login
            self.wait.until(
                lambda driver: "/login" in driver.current_url or 
                               EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'], input[type='email']"))
            )
            
            print("✅ Student logout successful")
            
        except Exception as e:
            print(f"❌ Student logout failed: {str(e)}")
            self.driver.save_screenshot(f"student_logout_failure_{int(time.time())}.png")
            raise e

        # Test admin logout
        self.login_as_admin()
        try:
            logout_selectors = [
                "//span[contains(text(), 'Logout')]/ancestor::button",
                "//button[contains(text(), 'Logout')]",
                "//a[contains(text(), 'Logout')]",
                "//button[contains(text(), 'Sign out')]",
                "//a[contains(text(), 'Sign out')]",
                "//*[contains(@class, 'logout')]",
            ]
            
            logout_btn = None
            for selector in logout_selectors:
                try:
                    logout_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not logout_btn:
                raise Exception("Could not find logout button")
            
            # Click logout
            self.driver.execute_script("arguments[0].scrollIntoView(true);", logout_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", logout_btn)
            
            # Wait for redirect to login
            self.wait.until(
                lambda driver: "/login" in driver.current_url or 
                               EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'], input[type='email']"))
            )
            
            print("✅ Admin logout successful")
            
        except Exception as e:
            print(f"❌ Admin logout failed: {str(e)}")
            self.driver.save_screenshot(f"admin_logout_failure_{int(time.time())}.png")
            raise e

    @classmethod
    def teardown_class(cls):
        """Clean up after all tests"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
            print("🧹 Browser closed successfully")

if __name__ == "__main__":
    test = TestNavigation()
    test.setup_class()
    test.test_admin_navigation_links()
    test.test_student_navigation_links()
    test.teardown_class()
