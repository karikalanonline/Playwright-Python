import time
from playwright.sync_api import Page, expect, Playwright
from pytest_playwright.pytest_playwright import browser


def test_logintochromium(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(
        "https://deloitteimmigration--qa.sandbox.my.salesforce.com/?ec=302&startURL=%2F500%2Fo"
    )
    page.get_by_label("username").fill("nehakumari27@deloitte.com.immg.qa")
    page.get_by_label("Password").fill("Sunshine@73623")
    page.locator("#rememberUn").check()
    page.get_by_role("button", name="Log In to Sandbox").click()
    time.sleep(5)
    page.locator("xpath=//a[@class='switch-to-lightning']").click()
    time.sleep(5)
    page.get_by_role("button", name="App Launcher").click()
    time.sleep(5)
    page.get_by_role("combobox", name="Search apps and items...").click()
    page.get_by_role("combobox", name="Search apps and items...").fill("CIP")
    time.sleep(5)
    page.get_by_role("option", name="CIP").nth(1).click()
    time.sleep(5)
    page.get_by_role("link", name="I-9 Process").click()
    page.get_by_role("button", name="Select a List View: I-9").click()
    page.get_by_text("Reverification - New").click()
    page.get_by_role("link", name="I9-00000166").click()
    page.get_by_role("button", name="Send Email").click()
    page.get_by_role("button", name="Clear").first.click()
    time.sleep(3)
    page.get_by_role("button", name="Lookup Contact").first.click()
    time.sleep(3)
    page.get_by_role("textbox", name="Search").fill("nehakumari27@deloitte.com")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("row", name="Neha Kumari Employee 123459").get_by_role(
        "checkbox"
    ).check()
    page.get_by_role("button", name="Add Contact").click()
    page.locator("#wrapper-body section").get_by_role(
        "button", name="Select Template"
    ).click()
    page.get_by_role("combobox", name="Email Template", exact=True).click()
    page.get_by_text("I-9 Reverification Completed").click()
    page.get_by_role("button", name="Select", exact=True).click()
    page.locator("#wrapper-body section").get_by_role("button", name="Send").click()
    expect(
        page.get_by_text("Success notification.SuccessEmail sent successfully")
    ).to_be_visible()
    time.sleep(5)
    page.set_input_files(
        ".slds-file-selector__dropzone input[type='file']", "D:\E330_Windows"
    )
    page.wait_for_timeout(4000)  # just to see what scripts do
