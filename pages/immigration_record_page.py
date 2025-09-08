import allure
from playwright.sync_api import expect, Page
from utils.logger import logger
from base.base_page import BasePage
from data import test_data


class ImmigrationRecordPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.cap_nominee_field = (
            "div div div span[class='test-id__field-label']:has-text('CAP Nominee')"
        )
        self.initiation_period = "div[class='test-id__field-label-container slds-form-element__label']:has-text('Initiation Period (CI)')"

    @allure.step("Getting the cap nominee value")
    def get_cap_nominee_value(self, timeout: int = 30_000) -> str:
        container = self.page.locator(
            "[data-target-selection-name='sfdc:RecordField.WCT_Immigration__c.CAP_Nominee__c']"
        ).first
        expect(container).to_be_visible(timeout=timeout)

        value = container.locator(
            "lightning-formatted-text, .test-id__field-value, .slds-form-element__static"
        ).first
        return value.inner_text().strip()

    # @allure.step("Verify the CAP Nominee equals: `{expected_value}`")
    # def verify_cap_nominee_field(
    #     self, expected_value: str = test_data.immigration_cap_nominee_value
    # ):
    #     logger.info("verify the value present on the cap nominee field")
    #     actual_value = self.get_cap_nominee_value()
    #     assert (
    #         actual_value.lower() == expected_value.lower()
    #     ), f"Expected {expected_value!r},got {actual_value!r}"

    @allure.step("Getting the inititation period value")
    def get_initiation_period(self):
        self
