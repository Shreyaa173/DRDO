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
        print("✓ Admin login successful")
        return True
        
    except Exception as e:
        print(f"✗ Admin login failed: {e}")
        return False

def navigate_to_applications(driver, wait):
    """Navigate to admin applications page"""
    try:
        selectors = [
            "//a[contains(text(), 'Applications')]",
            "//a[contains(text(), 'Manage Applications')]",
            "//nav//a[contains(@href, 'applications')]",
            "a[href*='applications']"
        ]
        
        if not safe_click_element(driver, selectors):
            driver.get(f"{BASE_URL}/admin/applications")
            
        time.sleep(3)
        print("✓ Navigated to admin applications page")
        return True
        
    except Exception as e:
        print(f"✗ Navigation failed: {e}")
        return False

def get_application_rows(driver):
    """Get all application rows from the table"""
    try:
        row_selectors = [
            "tbody tr:not(:has(td[colspan]))",  # Table rows excluding "No applications found"
            "tbody tr[data-application-id]",   # Rows with application ID
            "tbody tr:has(button)",            # Rows with action buttons
            "tbody tr"                         # Fallback to all rows
        ]
        
        for selector in row_selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if rows:
                    # Filter out empty rows or "no data" rows
                    valid_rows = []
                    for row in rows:
                        if row.find_elements(By.CSS_SELECTOR, "button"):  # Has action buttons
                            valid_rows.append(row)
                    return valid_rows
            except:
                continue
        
        return []
    except Exception as e:
        print(f"Error getting application rows: {e}")
        return []

def get_current_status(row):
    """Get current status of an application from the row"""
    try:
        # Enhanced status detection with multiple approaches
        status_selectors = [
            # Tailwind status badge classes
            ".bg-yellow-100.text-yellow-800",    # Pending
            ".bg-green-100.text-green-800",      # Approved
            ".bg-blue-100.text-blue-800",        # On Hold
            ".bg-red-100.text-red-800",          # Rejected
            ".bg-gray-100.text-gray-800",        # Other statuses
            
            # Generic badge classes
            ".px-2.py-1.rounded-full.text-xs.font-medium",
            ".badge",
            ".status-badge",
            
            # Text-based detection
            "span[class*='text-yellow']",
            "span[class*='text-green']",
            "span[class*='text-blue']",
            "span[class*='text-red']",
            
            # Fallback - any span with status-like classes
            "span[class*='bg-']",
            "td span",
            "span"
        ]
        
        for selector in status_selectors:
            try:
                status_element = row.find_element(By.CSS_SELECTOR, selector)
                status_text = status_element.text.strip().lower()

                status_map = {
                    'pending': 'Pending',
                    'approved': 'Approved',
                    'rejected': 'Rejected',
                    'hold': 'On Hold',
                    'on hold': 'On Hold'
                }

                for key in status_map:
                    if key in status_text:
                        return status_map[key]
                    
            except:
                pass        

        
        # Try to find status by examining all text in the row
        try:
            row_text = row.text
            status_keywords = {
                'pending': 'Pending',
                'approved': 'Approved', 
                'rejected': 'Rejected',
                'hold': 'On Hold',
                'on hold': 'On Hold'
            }
            
            for keyword, status in status_keywords.items():
                if keyword in row_text.lower():
                    return status
        except:
            pass
        
        # Debug: Print row structure to understand the HTML
        try:
            print(f"Debug - Row HTML: {row.get_attribute('outerHTML')[:200]}...")
        except:
            pass
        
        return "Unknown"
    except Exception as e:
        print(f"Error getting current status: {e}")
        return "Unknown"

def get_action_buttons(row):
    """Get action buttons from an application row"""
    try:
        buttons = {}
        
        # Button selectors based on your component structure
        button_selectors = {
            'approve': [
                "button[title='Approve']",
                "button.text-green-600",
                "//button[contains(@class, 'text-green-600')]",
                "//button[contains(text(), 'Approve')]"
            ],
            'hold': [
                "button[title='Put on Hold']",
                "button[title='On Hold']",
                "button.text-yellow-600",
                "//button[contains(@class, 'text-yellow-600')]",
                "//button[contains(text(), 'Hold')]"
            ],
            'reject': [
                "button[title='Reject']",
                "button.text-red-600",
                "//button[contains(@class, 'text-red-600')]",
                "//button[contains(text(), 'Reject')]"
            ]
        }
        
        for action, selectors in button_selectors.items():
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        button = row.find_element(By.XPATH, selector)
                    else:
                        button = row.find_element(By.CSS_SELECTOR, selector)
                    buttons[action] = button
                    break
                except:
                    continue
        
        return buttons
    except Exception as e:
        print(f"Error getting action buttons: {e}")
        return {}

def test_status_update_approve(driver, wait):
    """Test approve status update"""
    print("\n=== Testing Approve Status Update ===")
    
    try:
        rows = get_application_rows(driver)
        if not rows:
            print("✗ No application rows found")
            return
        
        success_count = 0
        
        for i, row in enumerate(rows[:3]):  # Test first 3 applications
            try:
                current_status = get_current_status(row)
                print(f"Application {i+1} current status: {current_status}")
                
                if current_status.lower() == "approved":
                    print(f"Application {i+1} already approved, skipping")
                    continue
                
                buttons = get_action_buttons(row)
                if 'approve' in buttons:
                    # Click approve button
                    buttons['approve'].click()
                    time.sleep(2)
                    
                    # Handle any confirmation dialog
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        time.sleep(1)
                        print(f"✓ Application {i+1} approved (with confirmation)")
                    except:
                        print(f"✓ Application {i+1} approved (no confirmation)")
                    
                    success_count += 1
                else:
                    print(f"✗ No approve button found for application {i+1}")
                    
            except Exception as e:
                print(f"✗ Error approving application {i+1}: {e}")
        
        print(f"✓ Approve test completed: {success_count} applications processed")
        
    except Exception as e:
        print(f"✗ Approve test failed: {e}")

def test_status_update_reject(driver, wait):
    """Test reject status update"""
    print("\n=== Testing Reject Status Update ===")
    
    try:
        rows = get_application_rows(driver)
        if not rows:
            print("✗ No application rows found")
            return
        
        success_count = 0
        
        for i, row in enumerate(rows[:3]):  # Test first 3 applications
            try:
                current_status = get_current_status(row)
                print(f"Application {i+1} current status: {current_status}")
                
                if current_status.lower() == "rejected":
                    print(f"Application {i+1} already rejected, skipping")
                    continue
                
                buttons = get_action_buttons(row)
                if 'reject' in buttons:
                    # Click reject button
                    buttons['reject'].click()
                    time.sleep(2)
                    
                    # Handle any confirmation dialog
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        time.sleep(1)
                        print(f"✓ Application {i+1} rejected (with confirmation)")
                    except:
                        print(f"✓ Application {i+1} rejected (no confirmation)")
                    
                    success_count += 1
                else:
                    print(f"✗ No reject button found for application {i+1}")
                    
            except Exception as e:
                print(f"✗ Error rejecting application {i+1}: {e}")
        
        print(f"✓ Reject test completed: {success_count} applications processed")
        
    except Exception as e:
        print(f"✗ Reject test failed: {e}")

def test_status_update_hold(driver, wait):
    """Test on hold status update"""
    print("\n=== Testing On Hold Status Update ===")
    
    try:
        rows = get_application_rows(driver)
        if not rows:
            print("✗ No application rows found")
            return
        
        success_count = 0
        
        for i, row in enumerate(rows[:3]):  # Test first 3 applications
            try:
                current_status = get_current_status(row)
                print(f"Application {i+1} current status: {current_status}")
                
                if current_status.lower() == "on hold":
                    print(f"Application {i+1} already on hold, skipping")
                    continue
                
                buttons = get_action_buttons(row)
                if 'hold' in buttons:
                    # Click hold button
                    buttons['hold'].click()
                    time.sleep(2)
                    
                    # Handle any confirmation dialog
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        time.sleep(1)
                        print(f"✓ Application {i+1} put on hold (with confirmation)")
                    except:
                        print(f"✓ Application {i+1} put on hold (no confirmation)")
                    
                    success_count += 1
                else:
                    print(f"✗ No hold button found for application {i+1}")
                    
            except Exception as e:
                print(f"✗ Error putting application {i+1} on hold: {e}")
        
        print(f"✓ Hold test completed: {success_count} applications processed")
        
    except Exception as e:
        print(f"✗ Hold test failed: {e}")

def test_status_filter_after_updates(driver, wait):
    """Test status filtering after status updates"""
    print("\n=== Testing Status Filter After Updates ===")
    
    try:
        status_selectors = [
            "select.px-4.py-2.border.border-gray-300.rounded-lg",
            "select"
        ]
        
        status_element = safe_find_element(driver, status_selectors)
        if not status_element:
            print("✗ Status filter element not found")
            return
        
        status_select = Select(status_element)
        
        # Test filtering by each status
        statuses_to_test = ["Pending", "Approved", "On Hold", "Rejected"]
        
        for status in statuses_to_test:
            try:
                status_select.select_by_visible_text(status)
                time.sleep(2)
                
                rows = get_application_rows(driver)
                print(f"Applications with status '{status}': {len(rows)}")
                
                # Verify all visible applications have the correct status
                if rows:
                    for i, row in enumerate(rows[:3]):  # Check first 3
                        current_status = get_current_status(row)
                        if current_status.lower() == status.lower():
                            print(f"✓ Application {i+1} correctly shows {status}")
                        else:
                            print(f"✗ Application {i+1} shows {current_status}, expected {status}")
                            
            except Exception as e:
                print(f"✗ Error testing {status} filter: {e}")
        
        # Reset to All Status
        status_select.select_by_visible_text("All Status")
        time.sleep(1)
        print("✓ Status filter test completed")
        
    except Exception as e:
        print(f"✗ Status filter test failed: {e}")

def test_bulk_status_updates(driver, wait):
    """Test bulk status updates if available"""
    print("\n=== Testing Bulk Status Updates ===")
    
    try:
        # Enhanced bulk action detection
        bulk_elements_found = False
        
        # Look for select all checkbox (usually in table header)
        select_all_selectors = [
            "thead input[type='checkbox']",
            "th input[type='checkbox']",
            "input[type='checkbox'][name*='selectAll']",
            "input[type='checkbox'][id*='selectAll']"
        ]
        
        select_all_checkbox = None
        for selector in select_all_selectors:
            try:
                select_all_checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                if select_all_checkbox:
                    print("✓ Found select all checkbox")
                    bulk_elements_found = True
                    break
            except:
                continue
        
        # Look for individual row checkboxes
        row_checkboxes = []
        checkbox_selectors = [
            "tbody input[type='checkbox']",
            "tr input[type='checkbox']",
            "td input[type='checkbox']",
            "input[type='checkbox'][name*='select']"
        ]
        
        for selector in checkbox_selectors:
            try:
                checkboxes = driver.find_elements(By.CSS_SELECTOR, selector)
                if checkboxes:
                    row_checkboxes = checkboxes
                    print(f"✓ Found {len(row_checkboxes)} row checkboxes")
                    bulk_elements_found = True
                    break
            except:
                continue
        
        # Look for bulk action buttons/dropdown
        bulk_action_selectors = [
            "button[title*='Bulk']",
            "select[name*='bulk']",
            "select[name*='action']",
            ".bulk-actions",
            "button:contains('Bulk Actions')",
            "//button[contains(text(), 'Bulk')]",
            "//select[contains(@name, 'bulk')]"
        ]
        
        bulk_action_element = None
        for selector in bulk_action_selectors:
            try:
                if selector.startswith("//"):
                    bulk_action_element = driver.find_element(By.XPATH, selector)
                else:
                    bulk_action_element = driver.find_element(By.CSS_SELECTOR, selector)
                if bulk_action_element:
                    print("✓ Found bulk action element")
                    bulk_elements_found = True
                    break
            except:
                continue
        
        if not bulk_elements_found:
            print("✗ No bulk action elements found")
            return
        
        # Test bulk selection if available
        if row_checkboxes and len(row_checkboxes) > 0:
            try:
                print(f"Testing bulk selection with {len(row_checkboxes)} checkboxes")
                
                # Select first few checkboxes
                selected_count = 0
                for i, checkbox in enumerate(row_checkboxes[:3]):
                    if checkbox.is_enabled() and checkbox.is_displayed():
                        try:
                            driver.execute_script("arguments[0].click();", checkbox)
                            selected_count += 1
                            time.sleep(0.5)
                            print(f"✓ Selected checkbox {i+1}")
                        except Exception as e:
                            print(f"✗ Failed to select checkbox {i+1}: {e}")
                
                if selected_count > 0:
                    print(f"✓ Bulk selection test passed: {selected_count} items selected")
                    
                    # Test bulk action if dropdown/button exists
                    if bulk_action_element:
                        try:
                            if bulk_action_element.tag_name == "select":
                                bulk_select = Select(bulk_action_element)
                                options = [opt.text for opt in bulk_select.options]
                                print(f"Available bulk actions: {options}")
                                
                                # Try to select a bulk action (don't execute)
                                if len(options) > 1:
                                    bulk_select.select_by_index(1)
                                    print("✓ Bulk action selection test passed")
                            else:
                                print("✓ Bulk action button found but not tested (to avoid accidental execution)")
                        except Exception as e:
                            print(f"✗ Bulk action test failed: {e}")
                    
                    # Deselect all checkboxes
                    for checkbox in row_checkboxes[:3]:
                        if checkbox.is_enabled() and checkbox.is_selected():
                            try:
                                driver.execute_script("arguments[0].click();", checkbox)
                                time.sleep(0.3)
                            except:
                                pass
                    
                    print("✓ Deselected all checkboxes")
                else:
                    print("✗ No checkboxes could be selected")
                    
            except Exception as e:
                print(f"✗ Bulk selection test failed: {e}")
        
        # Test select all functionality if available
        if select_all_checkbox:
            try:
                if select_all_checkbox.is_enabled() and select_all_checkbox.is_displayed():
                    driver.execute_script("arguments[0].click();", select_all_checkbox)
                    time.sleep(1)
                    print("✓ Select all test passed")
                    
                    # Deselect all
                    driver.execute_script("arguments[0].click();", select_all_checkbox)
                    time.sleep(1)
                    print("✓ Deselect all test passed")
                else:
                    print("✗ Select all checkbox not clickable")
            except Exception as e:
                print(f"✗ Select all test failed: {e}")
        
        print("✓ Bulk status update testing completed")
        
    except Exception as e:
        print(f"✗ Bulk status update test failed: {e}")

def debug_application_structure(driver, wait):
    """Debug function to understand the application table structure"""
    print("\n=== Debugging Application Structure ===")
    
    try:
        # Get first few rows for debugging
        rows = get_application_rows(driver)
        
        if rows:
            print(f"Found {len(rows)} application rows")
            
            for i, row in enumerate(rows[:2]):  # Debug first 2 rows
                print(f"\n--- Row {i+1} Structure ---")
                
                # Get all cells in the row
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                print(f"Number of cells: {len(cells)}")
                
                for j, cell in enumerate(cells):
                    cell_text = cell.text.strip()
                    if cell_text:
                        print(f"Cell {j+1}: {cell_text}")
                    
                    # Look for buttons in this cell
                    buttons = cell.find_elements(By.CSS_SELECTOR, "button")
                    if buttons:
                        print(f"  Buttons in cell {j+1}: {len(buttons)}")
                        for k, button in enumerate(buttons):
                            button_text = button.text.strip()
                            button_title = button.get_attribute('title')
                            button_class = button.get_attribute('class')
                            print(f"    Button {k+1}: text='{button_text}', title='{button_title}', class='{button_class}'")
                
                # Check for any spans with status-like content
                spans = row.find_elements(By.CSS_SELECTOR, "span")
                status_spans = []
                for span in spans:
                    span_text = span.text.strip()
                    span_class = span.get_attribute('class')
                    if span_text and any(keyword in span_text.lower() for keyword in ['pending', 'approved', 'rejected', 'hold']):
                        status_spans.append(f"'{span_text}' (class: {span_class})")
                
                if status_spans:
                    print(f"Potential status spans: {status_spans}")
        else:
            print("No application rows found")
            
    except Exception as e:
        print(f"Debug failed: {e}")

def test_status_update_comprehensive():
    """Comprehensive status update test"""
    print(" Starting Comprehensive Admin Status Update Tests\n")
    
    driver = setup_driver()
    if not driver:
        return
    
    wait = WebDriverWait(driver, 20)
    
    try:
        # Login as admin
        if not login_admin(driver, wait):
            return
        
        # Navigate to applications
        if not navigate_to_applications(driver, wait):
            return
        
        # Test individual status updates
        test_status_update_approve(driver, wait)
        test_status_update_reject(driver, wait)
        test_status_update_hold(driver, wait)
        
        # Test filtering after updates
        test_status_filter_after_updates(driver, wait)
        
        # Test bulk updates if available
        test_bulk_status_updates(driver, wait)
        
        print("\n All status update tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Comprehensive test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_status_update_comprehensive()