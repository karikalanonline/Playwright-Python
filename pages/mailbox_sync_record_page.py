import json, re
from playwright.sync_api import Locator, TimeoutError, expect
import logging, allure
from base.base_page import BasePage

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from pages.custom_email_II_page import CustomEmailPage

logger = logging.getLogger(__name__)


class MailboxSyncRecordPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self._by_label = (
            "div.slds-form-element:has(span.test-id__field-label:has-text('{label}'))"
        )
        self.email_link = "h3.slds-tile__title >> a"

    def _value_node(self, label: str) -> Locator:
        selector = self._by_label.format(label=label)

        # wait for the container to appear (short timeout) — helps when navigation is still settling
        try:
            # This waits up to 8s for the container to exist.
            self.page.wait_for_selector(selector, timeout=8000)
        except TimeoutError:
            # helpful debug output so you can inspect what's actually on the page
            logger.error(
                "Timeout waiting for label container '%s' at URL %s",
                label,
                self.page.url,
            )
            # show some nearby HTML to inspect
            try:
                sample = self.page.locator("div.slds-form-element").first.inner_html()[
                    :2000
                ]
            except Exception:
                sample = "<could-not-read-sample>"
            raise RuntimeError(
                f"Could not find label container for '{label}'. URL: {self.page.url}\n"
                f"Sample nearby HTML: {sample}"
            )

        container = self.page.locator(selector)
        if container.count() == 0:
            # super-safety: maybe label slightly different
            found_labels = self.page.locator(
                "span.test-id__field-label"
            ).all_inner_texts()
            raise RuntimeError(
                f"Label container matched zero nodes for selector {selector!r}.\n"
                f"Labels found on page: {found_labels}\n"
                f"URL: {self.page.url}"
            )

        # candidate child selectors (relative to the container)
        candidates = [
            "slot >> span",
            "span.owner-name",
            ".slds-form-element__control span.test-id__field-value",
            ".slds-form-element__control lightning-formatted-text",
            ".slds-form-element__control .slds-form-element__static",
        ]

        for sel in candidates:
            loc = container.locator(sel)
            count = loc.count()
            if count == 0:
                continue

            for i in range(count):
                node = loc.nth(i)
                try:
                    text = node.inner_text(timeout=500).strip()
                except Exception:
                    text = ""

                if not text:
                    continue
                if text.lower().startswith("change"):
                    continue
                return node

        raise RuntimeError(
            f"Could not find value node for field label '{label}'. Container HTML: {container.first.inner_html()[:2000]}"
        )

    def assert_case_details(self, expected: dict):
        # Assert case details dynamically from a dic of expected values
        actual = {}

        # collect actual values for all expected fields, Iterate Keys only
        for field in expected:
            try:
                node = self._value_node(field)
                actual_value = node.inner_text().strip()
            except Exception as e:
                actual_value = f"<not-found: {e}>"
            actual[field] = actual_value

        # Always attach to allure, pass or fail
        try:
            payload = json.dumps(
                {"expected": expected, "actual": actual}, indent=2, ensure_ascii=False
            )
            allure.attach(
                payload,
                name="case details - expected vs actual",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            pass  # don’t break test if attach fails

        for field, expected_value in expected.items():
            node = self._value_node(field)
            expect(node).to_have_text(expected_value)

    def click_email_link(self, timeout: int = 20_000) -> CustomEmailPage:
        # Click the EMAIL tile link
        self.page.locator(self.email_link, has_text="EMAIL").click()

        # Try waiting for URL pattern (SPA-safe). Ignore if it doesn't happen.
        pattern = re.compile(r".*/lightning/r/Custom_Email_2__c/.*")
        try:
            self.page.wait_for_url(pattern, timeout=8_000)
        except Exception:
            pass

        # Wait for a unique email-page label to be attached.
        # Prefer 'Custom Email Number' (likely unique). If not present, wait for 'Email Status'.
        unique_selectors = [
            "span.test-id__field-label:has-text('Custom Email Number')",
            "span.test-id__field-label:has-text('Email Status')",
            # last-resort: any 'Email' section header
            "h1:has-text('Email'), h1:has-text('Custom Email')",
        ]

        for sel in unique_selectors:
            try:
                # use .first to avoid strict mode errors
                self.page.locator(sel).first.wait_for(state="attached", timeout=4000)
                # once found, break out
                break
            except Exception:
                continue

        # final stabilization
        try:
            self.page.wait_for_load_state("networkidle", timeout=3_000)
        except Exception:
            pass

        return CustomEmailPage(self.page)

    # def click_email_link(self, timeout: int = 15_000):
    #     # click the email tile link
    #     self.page.locator(self.email_link, has_text="EMAIL").click()
    #     # wait for the URL to match the email record pattern (SPA friendly)
    #     pattern = re.compile(r".*/lightning/r/Custom_Email_2__c/.*")
    #     self.page.wait_for_url(pattern, timeout=timeout)
    #     # optionally wait for network idle or a unique element
    #     self.page.wait_for_load_state("networkidle", timeout=7_000)
    #     from pages.custom_email_II_page import CustomEmailPage

    #     return CustomEmailPage(self.page)

    # # def click_email_link(self) -> CustomEmailPage:
    # #     # click and wait for navigation; adapt if your page uses a pushState update
    # #     with self.page.expect_navigation():
    # #         self.page.locator(self.email_link, has_text="EMAIL").click()
    # #     return CustomEmailPage(self.page)
