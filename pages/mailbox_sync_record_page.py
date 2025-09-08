import json
from playwright.sync_api import Locator, TimeoutError, expect
import logging, allure
from base.base_page import BasePage

logger = logging.getLogger(__name__)


class MailboxSyncRecordPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self._by_label = (
            "div.slds-form-element:has(span.test-id__field-label:has-text('{label}'))"
        )

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
