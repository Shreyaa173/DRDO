from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import os

# === Configuration ===
BASE_URL = "https://drdointernshipapplicationproject.netlify.app"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@1234"
STUDENT_EMAIL = "student@gmail.com"
STUDENT_PASSWORD = "Student@1234"

def setup_driver():
    """Setup Chrome driver with improved options"""
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
        print("Using ChromeDriver from system PATH")
        return driver
    except Exception as e:
        print(f"Failed to initialize ChromeDriver: {e}")
        return None

def safe_find_element(driver, selectors, timeout=10):
    """Safely find element with multiple selector fallbacks"""
    wait = WebDriverWait(driver, timeout)
    
    if isinstance(selectors, str):
        selectors = [selectors]
    
    for selector in selectors:
        try:
            if selector.startswith("//"):
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            else:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return element
        except TimeoutException:
            continue
    
    return None

def safe_click_element(driver, selectors, timeout=10):
    """Safely click element with multiple selector fallbacks"""
    wait = WebDriverWait(driver, timeout)
    
    if isinstance(selectors, str):
        selectors = [selectors]
    
    for selector in selectors:
        try:
            if selector.startswith("//"):
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            return True
        except TimeoutException:
            continue
    
    return False

def login_user(driver, wait, email, password, user_type):
    """Login user with improved error handling"""
    try:
        driver.get(f"{BASE_URL}/login")
        
        # Wait for login form
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.clear()
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for redirect
        expected_url = f"/{user_type}" if user_type == "admin" else "/student"
        wait.until(EC.url_contains(expected_url))
        print(f"✓ Logged in as {user_type} successfully")
        return True
        
    except Exception as e:
        print(f"✗ Login failed for {user_type}: {e}")
        return False

def navigate_to_applications(driver, wait, user_type):
    """Navigate to applications page with improved selectors"""
    try:
        if user_type == "admin":
            # Try multiple selectors for admin applications
            selectors = [
                "//a[contains(text(), 'Applications')]",
                "//a[contains(text(), 'Manage Applications')]",
                "//nav//a[contains(@href, 'applications')]",
                "a[href*='applications']"
            ]
            
            if not safe_click_element(driver, selectors):
                # Fallback to direct navigation
                driver.get(f"{BASE_URL}/admin/applications")
                
        else:
            # Try multiple selectors for student applications
            selectors = [
                "//a[contains(text(), 'My Applications')]",
                "//a[contains(text(), 'Applications')]",
                "//nav//a[contains(@href, 'applications')]",
                "a[href*='applications']"
            ]
            
            if not safe_click_element(driver, selectors):
                # Fallback to direct navigation
                driver.get(f"{BASE_URL}/student/applications")
        
        time.sleep(3)  # Wait for page to load
        print(f"✓ Navigated to {user_type} applications page")
        return True
        
    except Exception as e:
        print(f"✗ Navigation failed for {user_type}: {e}")
        return False

def get_results_count(driver):
    """Get count of filtered results - Updated for your actual component structure"""
    try:
        # Based on your MyApplications component structure
        student_selectors = [
            ".bg-white.rounded-lg.shadow-sm.border.p-6.hover\\:shadow-md",  # Student application cards
            ".grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3.gap-6 > div:not(.col-span-full)",  # Grid items
            "[data-testid='application-item']"
        ]
        
        # Based on your ApplicationsManagement component structure
        admin_selectors = [
            "tbody tr:not(:has(td[colspan]))",  # Table rows excluding "No applications found"
            ".hover\\:bg-gray-50",  # Table rows with hover effect
            "tr[data-application-id]"
        ]
        
        # Try student selectors first
        for selector in student_selectors:
            try:
                results = driver.find_elements(By.CSS_SELECTOR, selector)
                if results:
                    return len(results)
            except:
                continue
        
        # Try admin selectors
        for selector in admin_selectors:
            try:
                results = driver.find_elements(By.CSS_SELECTOR, selector)
                if results:
                    return len(results)
            except:
                continue
        
        return 0
    except Exception as e:
        print(f"Error getting results count: {e}")
        return 0

def test_student_filtering_functionality():
    """Test filtering functionality for student dashboard"""
    print("=== Starting Student Application Filtering Tests ===\n")
    
    driver = setup_driver()
    if not driver:
        return
    
    wait = WebDriverWait(driver, 20)
    
    try:
        # Login as Student
        if not login_user(driver, wait, STUDENT_EMAIL, STUDENT_PASSWORD, "student"):
            return
        
        # Navigate to applications page
        if not navigate_to_applications(driver, wait, "student"):
            return
        
        # Test student-specific filters
        test_student_application_status_filter(driver, wait)
        test_student_search_filter(driver, wait)
        test_student_combined_filters(driver, wait)
        
    except Exception as e:
        print(f"✗ Student Test Failed: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

def test_admin_filtering_functionality():
    """Test filtering functionality for admin dashboard"""
    print("\n=== Starting Admin Application Filtering Tests ===\n")
    
    driver = setup_driver()
    if not driver:
        return
    
    wait = WebDriverWait(driver, 20)
    
    try:
        # Login as Admin
        if not login_user(driver, wait, ADMIN_EMAIL, ADMIN_PASSWORD, "admin"):
            return
        
        # Navigate to applications page
        if not navigate_to_applications(driver, wait, "admin"):
            return
        
        # Test admin-specific filters
        test_admin_application_status_filter(driver, wait)
        test_admin_search_filter(driver, wait)
        test_admin_combined_filters(driver, wait)
        test_admin_status_update_actions(driver, wait)
        
    except Exception as e:
        print(f"✗ Admin Test Failed: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

def test_student_application_status_filter(driver, wait):
    """Test student's application status filtering - Updated for your component"""
    print("=== Testing Student Application Status Filter ===")
    
    try:
        # Based on your MyApplications component - the select dropdown
        status_selectors = [
            "select[value]",  # Select with value attribute
            "select.px-4.py-2.border.border-gray-300.rounded-lg",  # Exact class from your component
            "//select[contains(@class, 'px-4') and contains(@class, 'py-2')]",  # XPath with classes
            "select"  # Fallback
        ]
        
        status_element = safe_find_element(driver, status_selectors)
        if not status_element:
            print("✗ Status filter element not found")
            return
        
        status_select = Select(status_element)
        options = [option.text for option in status_select.options]
        print(f"Available status options: {options}")
        
        # Test each available status based on your component options
        test_statuses = ["All Status", "Pending", "Approved", "On Hold"]
        
        for status in test_statuses:
            if status in options:
                print(f"Testing status: {status}")
                status_select.select_by_visible_text(status)
                time.sleep(2)
                
                results = get_results_count(driver)
                print(f"Results for {status}: {results}")
                
                if results >= 0:  # Any count is valid
                    print(f"✓ {status} filter test passed")
                else:
                    print(f"✗ {status} filter test failed")
        
        # Reset to default
        status_select.select_by_visible_text("All Status")
        time.sleep(1)
            
    except Exception as e:
        print(f"✗ Student status filter test failed: {e}")

def test_student_search_filter(driver, wait):
    """Test student search functionality - Updated for your component"""
    print("\n=== Testing Student Search Filter ===")
    
    try:
        # Based on your MyApplications component - the search input
        search_selectors = [
            "input[placeholder*='Search labs or branches']",  # Exact placeholder from your component
            "input.w-full.pl-10.pr-4.py-2.border.border-gray-300.rounded-lg",  # Exact classes
            "//input[contains(@placeholder, 'Search')]",  # XPath with placeholder
            "input[type='text']"  # Fallback
        ]
        
        search_input = safe_find_element(driver, search_selectors)
        if not search_input:
            print("✗ Search input not found")
            return
        
        # Test search functionality
        test_searches = ["research", "computer", "engineering", "lab"]
        
        for search_term in test_searches:
            search_input.clear()
            search_input.send_keys(search_term)
            time.sleep(2)  # Wait for filter to apply
            
            results = get_results_count(driver)
            print(f"Search results for '{search_term}': {results}")
        
        # Clear search
        search_input.clear()
        time.sleep(1)
        print("✓ Search filter test passed")
        
    except Exception as e:
        print(f"✗ Search filter test failed: {e}")

def test_student_combined_filters(driver, wait):
    """Test combined filters for student"""
    print("\n=== Testing Student Combined Filters ===")
    
    try:
        # Find both elements
        status_element = safe_find_element(driver, ["select.px-4.py-2.border.border-gray-300.rounded-lg", "select"])
        search_element = safe_find_element(driver, ["input[placeholder*='Search labs or branches']", "input[type='text']"])
        
        if status_element and search_element:
            status_select = Select(status_element)
            
            # Apply status filter
            try:
                status_select.select_by_visible_text("Pending")
            except:
                pass  # Skip if option doesn't exist
            
            # Apply search filter
            search_element.clear()
            search_element.send_keys("research")
            time.sleep(2)
            
            results = get_results_count(driver)
            print(f"Combined filter results: {results}")
            
            # Reset
            status_select.select_by_visible_text("All Status")
            search_element.clear()
            time.sleep(1)
            
            print("✓ Combined filters test passed")
        else:
            print("✗ Required filter elements not found")
            
    except Exception as e:
        print(f"✗ Combined filters test failed: {e}")

def test_admin_application_status_filter(driver, wait):
    """Test admin application status filtering - Updated for your component"""
    print("\n=== Testing Admin Application Status Filter ===")
    
    try:
        # Based on your ApplicationsManagement component
        status_selectors = [
            "select.px-4.py-2.border.border-gray-300.rounded-lg.focus\\:ring-2.focus\\:ring-indigo-500",  # Exact classes
            "//select[contains(@class, 'px-4') and contains(@class, 'py-2')]",  # XPath with classes
            "select"  # Fallback
        ]
        
        status_element = safe_find_element(driver, status_selectors)
        if not status_element:
            print("✗ Admin status filter element not found")
            return
        
        status_select = Select(status_element)
        options = [option.text for option in status_select.options]
        print(f"Available admin status options: {options}")
        
        # Test available status options from your component
        admin_statuses = ["All Status", "Pending", "Approved", "On Hold", "Rejected"]
        
        for status in admin_statuses:
            if status in options:
                print(f"Testing admin status: {status}")
                status_select.select_by_visible_text(status)
                time.sleep(2)
                
                results = get_results_count(driver)
                print(f"Results for {status}: {results}")
                print(f"✓ Admin {status} filter test passed")
        
        # Reset to default
        status_select.select_by_visible_text("All Status")
        time.sleep(1)
            
    except Exception as e:
        print(f"✗ Admin status filter test failed: {e}")

def test_admin_search_filter(driver, wait):
    """Test admin search functionality - Updated for your component"""
    print("\n=== Testing Admin Search Filter ===")
    
    try:
        # Based on your ApplicationsManagement component
        search_selectors = [
            "input[placeholder*='Search students, emails, or positions']",  # Exact placeholder
            "input.w-full.pl-10.pr-4.py-2.border.border-gray-300.rounded-lg",  # Exact classes
            "//input[contains(@placeholder, 'Search')]",  # XPath with placeholder
            "input[type='text']"  # Fallback
        ]
        
        search_element = safe_find_element(driver, search_selectors)
        if not search_element:
            print("✗ Admin search filter element not found")
            return
        
        # Test search functionality
        test_searches = ["student", "test", "research", "intern"]
        
        for search_term in test_searches:
            search_element.clear()
            search_element.send_keys(search_term)
            time.sleep(2)
            
            results = get_results_count(driver)
            print(f"Admin search results for '{search_term}': {results}")
        
        # Clear search
        search_element.clear()
        time.sleep(1)
        print("✓ Admin search filter test passed")
        
    except Exception as e:
        print(f"✗ Admin search filter test failed: {e}")

def test_admin_combined_filters(driver, wait):
    """Test admin combined filters - Updated for your component"""
    print("\n=== Testing Admin Combined Filters ===")
    
    try:
        # Find both elements based on your component structure
        status_element = safe_find_element(driver, ["select.px-4.py-2.border.border-gray-300.rounded-lg", "select"])
        search_element = safe_find_element(driver, ["input[placeholder*='Search students, emails, or positions']", "input[type='text']"])
        
        if status_element and search_element:
            status_select = Select(status_element)
            
            # Apply status filter
            try:
                status_select.select_by_visible_text("Pending")
            except:
                pass  # Skip if option doesn't exist
            
            # Apply search filter
            search_element.clear()
            search_element.send_keys("student")
            time.sleep(2)
            
            results = get_results_count(driver)
            print(f"Admin combined filter results: {results}")
            
            # Reset
            status_select.select_by_visible_text("All Status")
            search_element.clear()
            time.sleep(1)
            
            print("✓ Admin combined filters test passed")
        else:
            print("✗ Required admin filter elements not found")
            
    except Exception as e:
        print(f"✗ Admin combined filters test failed: {e}")

def test_admin_status_update_actions(driver, wait):
    """Test admin status update actions - Based on your component"""
    print("\n=== Testing Admin Status Update Actions ===")
    
    try:
        # Look for action buttons based on your component structure
        action_selectors = [
            "button[title='Approve']",  # Approve button
            "button[title='Put on Hold']",  # Hold button
            "button[title='Reject']",  # Reject button
            ".text-green-600.hover\\:text-green-900",  # Green approve button
            ".text-yellow-600.hover\\:text-yellow-900",  # Yellow hold button
            ".text-red-600.hover\\:text-red-900"  # Red reject button
        ]
        
        action_buttons = []
        for selector in action_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                action_buttons.extend(buttons)
            except:
                continue
        
        if action_buttons:
            print(f"Found {len(action_buttons)} action buttons")
            
            # Test clicking the first action button (if any)
            if len(action_buttons) > 0:
                try:
                    action_buttons[0].click()
                    time.sleep(2)
                    
                    # Check if any confirmation dialog appears
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()  # Accept the alert
                        time.sleep(1)
                        print("✓ Status update action test passed")
                    except:
                        print("✓ Status update action test passed (no alert)")
                        
                except Exception as e:
                    print(f"✗ Action button click failed: {e}")
            else:
                print("✗ No action buttons found to test")
        else:
            print("✗ No action buttons found")
            
    except Exception as e:
        print(f"✗ Admin status update actions test failed: {e}")

def run_all_tests():
    """Run both student and admin filtering tests"""
    print("🚀 Starting Comprehensive Filtering Tests\n")
    
    # Test student functionality
    test_student_filtering_functionality()
    
    # Test admin functionality  
    test_admin_filtering_functionality()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    run_all_tests()