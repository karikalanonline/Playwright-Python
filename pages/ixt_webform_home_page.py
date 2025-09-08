from playwright.sync_api import Page, expect
from base.base_page import BasePage
from data import test_data
from utils.logger import logger
import re


class IxtWebFormHomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.dropdown = "button[role='combobox']"
        self.inquiry_textbox = "div[class*='slds-rich-text-area']"
        self.submit_button = (
            "button[class='slds-button slds-button_brand']:has-text('Submit')"
        )
        self.yes_button = (
            "button[class='slds-button slds-button_brand']:has-text('Yes')"
        )
        self.thankyou_message = "p[class='slds-p-left_small']"
        self.confirm_modal = "div.slds-modal__container"

    def name_batch(self, name: str):
        return self.page.locator(
            "h2.slds-card__header-title span.slds-truncate", has_text=name
        )

    def email_batch(self, email_id: str):
        return self.page.locator(
            "div.slds-var-p-horizontal_medium i a", has_text=email_id
        )

    def assert_name(self, expected_name: str):
        expect(self.name_batch(expected_name)).to_contain_text(expected_name)

    def assert_email(self, expected_email: str):
        expect(self.email_batch(expected_email)).to_contain_text(expected_email)

    # def click_dropdown(self):
    #     self.click_element(self.dropdown)

    def click_dropdown(self, aria_label: str):
        self.page.get_by_role("combobox", name=aria_label).click()

    def select_option(self, option: str):
        self.page.get_by_role("option", name=option).click()

    def enter_inquiry(self):
        text_box = self.page.locator(self.inquiry_textbox)
        text_box.scroll_into_view_if_needed()
        text_box.click()
        self.fill(self.inquiry_textbox, "Playwright Automation")

    def click_submit_button(self):
        submit_button = self.page.locator(self.submit_button)
        submit_button.scroll_into_view_if_needed()
        self.click_element(self.submit_button)

    def click_confirm_yes(self):
        logger.info("Attempt to click the confirm Yes button")
        expect(self.page.locator(self.confirm_modal)).to_be_visible(timeout=5000)
        self.click_element(self.yes_button)
        expect(self.page.locator(self.confirm_modal)).to_be_hidden(timeout=5000)

    def assert_success_message(self):
        expect(self.page.locator(self.thankyou_message)).to_be_visible()
        success_message = self.page.locator(self.thankyou_message).inner_text()
        print("Full sucess message:", success_message)
        assert "Thank you for your inquiry" in success_message
        match = re.search(r"\b(IXT-\d+)\b", success_message)
        assert match is not None, "Inquiry number not present in the success message"
        assert match.group(1).startswith("IXT-")
        self.inquiry_number = match.group(1)

    def get_inquiry_number(self):
        inquiry_number = self.inquiry_number
        print("The inquiry number is:", inquiry_number)
        return inquiry_number

    def go_back_to_salesforce_page(self):
        with self.page.expect_navigation():
            self.page.go_back()

    # def fill_form(self):
    #     self.assert_name(test_data.name)
    #     self.assert_email(test_data.email)
    #     self.click_dropdown("Requestor Type")
    #     self.select_option("Myself and/or dependent(s)")
    #     self.click_dropdown("Category")
    #     self.select_option("H-1B Cap Sponsorship")
    #     self.click_dropdown("Subcategory 1")
    #     self.select_option("Status of case")
    #     self.enter_inquiry()
    #     self.click_submit_button()
    #     self.click_confirm_yes()
    #     self.assert_success_message()
    #     return self.get_inquiry_number()

    def fill_form(self):
        self.assert_name(test_data.name)
        self.assert_email(test_data.email)
        self.click_dropdown("Requestor Type")
        self.select_option("Myself and/or dependent(s)")
        self.click_dropdown("Category")
        self.select_option("H-1B Cap Sponsorship")
        self.click_dropdown("Subcategory 1")
        self.select_option("Status of case")
        self.enter_inquiry()
        self.click_submit_button()
        self.click_confirm_yes()
        self.assert_success_message()
        inquiry_number = self.get_inquiry_number()
        return inquiry_number
