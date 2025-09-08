import allure
from playwright.sync_api import Page


def attach_text(name: str, message: str):
    allure.attach(message, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_screenshot(page: Page, name: str = "Screenshot"):
    allure.attach(
        page.screenshot(full_page=False),
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )
