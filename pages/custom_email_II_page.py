# # pages/custom_email_II_page.py
# from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError
# from base.base_page import BasePage


# class CustomEmailPage(BasePage):
#     def __init__(self, page):
#         super().__init__(page)

#     def _debug_counts(self):
#         print("PAGE URL:", self.page.url)
#         print(
#             "counts: Email Status selector:",
#             self.page.locator(
#                 "div.slds-form-element:has(span.test-id__field-label:has-text('Email Status')) span.test-id__field-value"
#             ).count(),
#         )
#         print(
#             "counts: Custom Email Number label:",
#             self.page.locator(
#                 "span.test-id__field-label:has-text('Custom Email Number')"
#             ).count(),
#         )
#         print(
#             "counts: generic Status labels:",
#             self.page.locator("span.test-id__field-label:has-text('Status')").count(),
#         )

#     def get_status_value(self, timeout: int = 10_000) -> str:
#         """
#         Prefer to read the 'Status' value that's *inside the Custom Email record section*.
#         Strategy:
#          - find the 'Custom Email Number' label (unique element on this record)
#          - take its ancestor layout-row and search inside it for 'Status' value
#          - fallback to explicit 'Email Status'
#          - fallback to generic Status (last resort)
#         """

#         # 0) ensure we're on the custom email URL (best-effort)
#         try:
#             self.page.wait_for_url("**/lightning/r/Custom_Email_2__c/**", timeout=3000)
#         except Exception:
#             # ignore — we still try, but this helps ensure the test navigated properly
#             pass

#         # 1) Try the 'Custom Email Number' anchor -> ancestor -> find Status inside same block
#         try:
#             anchor = self.page.locator(
#                 "span.test-id__field-label:has-text('Custom Email Number')"
#             ).first
#             if anchor.count():
#                 # find a sensible ancestor container. Use XPath to go to a reasonable parent row
#                 # NOTE: playwright accepts xpath selectors as "xpath=..."
#                 ancestor = self.page.locator(
#                     "xpath=//span[text()='Custom Email Number']/ancestor::div[contains(@class,'records-record-layout-row') or contains(@class,'slds-grid')][1]"
#                 ).first
#                 if ancestor.count():
#                     # now look for Status value inside that same ancestor
#                     candidate = ancestor.locator(
#                         "div.slds-form-element:has(span.test-id__field-label:has-text('Status')) span.test-id__field-value"
#                     ).first
#                     if candidate.count():
#                         # scroll (harmless) and read
#                         try:
#                             candidate.scroll_into_view_if_needed(timeout=500)
#                         except Exception:
#                             pass
#                         txt = candidate.text_content(timeout=1500)
#                         if txt and txt.strip():
#                             return txt.strip()
#         except PlaywrightTimeoutError:
#             pass
#         except Exception:
#             # swallow and continue to other fallbacks
#             pass

#         # 2) Fallback: explicit 'Email Status' (if your org exposes it as a field)
#         try:
#             candidate = self.page.locator(
#                 "div.slds-form-element:has(span.test-id__field-label:has-text('Email Status')) span.test-id__field-value"
#             ).first
#             if candidate.count():
#                 try:
#                     candidate.scroll_into_view_if_needed(timeout=500)
#                 except Exception:
#                     pass
#                 txt = candidate.text_content(timeout=1500)
#                 if txt and txt.strip():
#                     return txt.strip()
#         except Exception:
#             pass

#         # 3) Last-resort: generic 'Status' (but prefer ones near the top of page)
#         try:
#             # pick the first visible value for Status
#             all_status_values = self.page.locator(
#                 "div.slds-form-element:has(span.test-id__field-label:has-text('Status')) span.test-id__field-value"
#             )
#             count = all_status_values.count()
#             for i in range(count):
#                 node = all_status_values.nth(i)
#                 try:
#                     # prefer visible nodes
#                     if not node.is_visible():
#                         # still attempt to read text_content (some orgs render inside shadow/slot)
#                         txt = node.text_content(timeout=300)
#                     else:
#                         txt = node.text_content(timeout=300)
#                 except Exception:
#                     txt = None
#                 if txt and txt.strip():
#                     # return the first meaningful text we find (best-effort)
#                     return txt.strip()
#         except Exception:
#             pass

#         # If nothing found -> print debug and raise
#         self._debug_counts()
#         # show short snippet of the page around any Status rows for debugging
#         try:
#             rows = self.page.locator(
#                 "div.slds-form-element:has(span.test-id__field-label:has-text('Status'))"
#             )
#             if rows.count():
#                 print("First status row snippet:", rows.first.inner_html()[:1000])
#         except Exception:
#             pass

#         raise AssertionError(
#             f"Row for 'Status' not visible / no text found (url={self.page.url})"
#         )

#     def assert_email_status(self, expected: str = "Sent"):
#         actual = self.get_status_value()
#         assert (
#             actual == expected
#         ), f"Email status expected '{expected}' but got '{actual}'"

#     # convenience debug helper you can call from test:
#     def dump_status_debug(self):
#         self._debug_counts()
#         try:
#             print("PAGE URL:", self.page.url)
#             labels = self.page.locator("span.test-id__field-label").all_inner_texts()
#             print("All labels (sample):", labels[:40])
#         except Exception as e:
#             print("dump_status_debug error:", e)
# pages/custom_email_II_page.py
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from base.base_page import BasePage
import time, allure


class CustomEmailPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.page = page

    def _debug_nodes(self, selector):
        """Print some debug info for nodes matching selector."""
        nodes = self.page.locator(selector)
        count = nodes.count()
        print(f"DEBUG: selector={selector!r} count={count}")
        for i in range(count):
            n = nodes.nth(i)
            try:
                vis = n.is_visible()
            except Exception:
                vis = "<is_visible-error>"
            try:
                text = n.inner_text(timeout=300).strip()
            except Exception:
                text = "<inner_text-error>"
            print(f"  [{i}] visible={vis} text={repr(text)}")
        return count

    def get_status_value(self, timeout: int = 10_000) -> str:
        """
        Return the 'Email Status' (preferred) or the 'Status' inside the Custom Email area.
        Picks the first *visible* and non-empty node.
        """
        # 1) ensure the view switched to the Custom Email record (URL and anchor label)
        # Wait for the URL or the unique 'Custom Email Number' label to appear.
        try:
            # Wait for the URL pattern -- your click_email_link already calls wait_for_url.
            # Additionally wait for 'Custom Email Number' label to be visible so we know the
            # custom email record is actually displayed.
            self.page.wait_for_selector(
                "span.test-id__field-label:has-text('Custom Email Number')",
                timeout=timeout,
            )
        except PlaywrightTimeoutError:
            # fallback small sleep+debug so tests don't immediately fail intermittently
            time.sleep(1)
            # continue to try; we'll dump nodes if we fail later

        # candidate selectors (most specific first)
        candidates = [
            # explicit Email Status label (preferred)
            "div.slds-form-element:has(span.test-id__field-label:has-text('Email Status')) span.test-id__field-value",
            # explicit Email Status but look inside lightning-formatted-text slot (sometimes used)
            "div.slds-form-element:has(span.test-id__field-label:has-text('Email Status')) slot[name='outputField'] lightning-formatted-text",
            # fallback: within the Custom Email block look for 'Status' value
            "xpath=//span[text()='Custom Email Number']/ancestor::div[contains(@class,'records-record-layout-row') or contains(@class,'slds-grid')][1]//div[contains(@class,'slds-form-element') and .//span[contains(@class,'test-id__field-label') and normalize-space(text())='Status']]//span[contains(@class,'test-id__field-value')]",
            # generic Status (last resort) - but we will only take visible nodes
            "div.slds-form-element:has(span.test-id__field-label:has-text('Status')) span.test-id__field-value",
            # generic value inside slot
            "div.slds-form-element:has(span.test-id__field-label:has-text('Status')) slot[name='outputField'] lightning-formatted-text",
        ]

        # try each candidate selector and return the first visible non-empty inner_text()
        for sel in candidates:
            try:
                nodes = self.page.locator(sel)
                count = nodes.count()
            except Exception:
                count = 0

            if count == 0:
                continue

            for i in range(count):
                node = nodes.nth(i)
                try:
                    if not node.is_visible():
                        # skip hidden nodes (they may be from the earlier page)
                        continue
                except Exception:
                    # if `is_visible` errors, still try to read inner_text but prefer visible
                    pass

                # use inner_text() to get what user sees
                try:
                    txt = node.inner_text(timeout=500).strip()
                except Exception:
                    try:
                        txt = node.text_content(timeout=500) or ""
                        txt = txt.strip()
                    except Exception:
                        txt = ""

                if txt and not txt.lower().startswith("change"):  # skip edit hints
                    return txt

        # nothing found: dump debug info so you can see what's on the page
        print(
            "--- get_status_value: couldn't find visible Status; dumping candidates ---"
        )
        for sel in candidates:
            self._debug_nodes(sel)
        raise AssertionError(
            f"Row for 'Status' not visible within {timeout}ms (url={self.page.url})"
        )

    def assert_email_status(self, expected: str = "Sent"):
        actual = self.get_status_value()
        allure.attach(
            f"Expected: {expected}\nActual: {actual}",
            name="Email Status Verification",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert (
            actual == expected
        ), f"Email status expected '{expected}' but got '{actual}'"
