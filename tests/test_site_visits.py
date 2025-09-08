import time


from playwright.sync_api import sync_playwright, Playwright, expect


def test_login(playwright: Playwright):
    browser = playwright.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Landing to Home page
    page.goto("https://deloitteimmigration--qa.sandbox.lightning.force.com/")
    page.get_by_label("username").fill("sushmn@deloitte.com.immg.qa")  # textbox
    page.fill("#password", "Deloitte@8660")
    page.get_by_role("button", name="Log In to Sandbox").click()
    time.sleep(3)
    # Navigate to CIP APP
    page.get_by_role("button", name="App Launcher").click()
    page.wait_for_selector("input[placeholder='Search apps and items...']").fill("CIP")
    page.get_by_role("option", name="CIP").nth(1).click()
    time.sleep(3)

    # Manual record creation for site visits
    page.get_by_role("button", name="More").click()
    time.sleep(2)
    page.get_by_role("menuitem", name="Site Visits").click()
    time.sleep(2)
    page.get_by_role("button", name="New", exact=True).click()
    page.get_by_role("checkbox", name="CIP")
    time.sleep(2)
    page.get_by_role("button", name="Next", exact=True).click()
    time.sleep(5)

    # Employee Name (autocomplete)
    employee_name = page.locator(
        "div input[class='slds-combobox__input slds-input']"
    ).first
    employee_name.click()
    time.sleep(5)
    employee_name.fill("Sushma")
    time.sleep(5)
    dropdown_options = page.locator(
        "li.slds-listbox__item lightning-base-combobox-formatted-text"
    )
    expect(dropdown_options.first).to_be_visible()
    dropdown_options.first.click()

    # Employee Manager (autocomplete)
    employee_manager = page.locator(
        "div input[class='slds-combobox__input slds-input']"
    ).nth(0)
    time.sleep(2)
    employee_manager.click()
    time.sleep(2)
    employee_manager.fill("Neha Kumari")
    picklist_options = page.locator(
        "li.slds-listbox__item lightning-base-combobox-formatted-text"
    )
    time.sleep(3)
    expect(picklist_options.first).to_be_visible()
    picklist_options.first.click()
