def dump_status_debug(self):
    self._debug_counts()
    try:
        print("PAGE URL:", self.page.url)
        labels = self.page.locator("span.test-id__field-label").all_inner_texts()
        print("All labels (sample):", labels[:40])
    except Exception as e:
        print("dump_status_debug error:", e)


# dump_status_debug() (the counts and sample labels).
# Those outputs will show exactly which nodes exist and which the code is seeing.


def debug_counts(self):
    print("PAGE URL:", self.page.url)
    print(
        "counts: Email Status selector:",
        self.page.locator(
            "div.slds-form-element:has(span.test-id__field-label:has-text('Email Status')) span.test-id__field-value"
        ).count(),
    )
    print(
        "counts: Custom Email Number label:",
        self.page.locator(
            "span.test-id__field-label:has-text('Custom Email Number')"
        ).count(),
    )
    print(
        "counts: generic Status labels:",
        self.page.locator("span.test-id__field-label:has-text('Status')").count(),
    )


def dump_status_nodes(self):
    # helpful debug output when things go wrong
    try:
        email_status_nodes = self.page.locator(
            "div.slds-form-element:has(span.test-id__field-label:has-text('Email Status')) span.test-id__field-value"
        )
        print("Email Status count:", email_status_nodes.count())
        for i in range(email_status_nodes.count()):
            node = email_status_nodes.nth(i)
            print(
                f"EmailStatus[{i}] visible={node.is_visible()} text={repr(node.text_content(timeout=200).strip() if node.count() else '')}"
            )
    except Exception as e:
        print("dump email_status error:", e)

    try:
        generic_status_nodes = self.page.locator(
            "div.slds-form-element:has(span.test-id__field-label:has-text('Status')) span.test-id__field-value"
        )
        print("Generic Status count:", generic_status_nodes.count())
        for i in range(generic_status_nodes.count()):
            node = generic_status_nodes.nth(i)
            print(
                f"Status[{i}] visible={node.is_visible()} text={repr(node.text_content(timeout=200).strip() if node.count() else '')}"
            )
    except Exception as e:
        print("dump generic status error:", e)
