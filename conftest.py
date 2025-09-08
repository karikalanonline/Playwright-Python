import pytest, re, os
import allure
import json
from playwright.sync_api import Playwright, Page, expect
from pages.login_page import LoginPage
from utils import config
from pages.salesforce_home_page import SalesforceHomePage
from pages.immi_home_page import ImmigrationHomePage
from data import test_data
from pages.ixt_webform_home_page import IxtWebFormHomePage
from pages.salesforce_admin_page import SalesforceAdminPage
from pages.mailbox_sync_record_page import MailboxSyncRecordPage


# The below snippet will take the screenshot on failure
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Run all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # We only care about failed tests
    if report.failed and report.when in ("setup", "call", "teardown"):
        try:
            page = item.funcargs["page"]  # get Playwright page
            screenshot = page.screenshot()

            allure.attach(  # failure on screenshot
                screenshot,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

            allure.attach(  # current URL at failure
                page.url,
                name="URL at failure",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as e:
            print(f"Could not take screenshot: {e}")


@pytest.fixture
def context(playwright: Playwright):
    # Launch browser with viewport disabled. By default, Chromium will still launch with a small window.
    # to overcome this, args=["--start-maximized"]
    browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(no_viewport=True)  # disables forced viewport
    yield context  # gives the context to tests
    context.close()  # teardown after test
    browser.close()


@pytest.fixture
def page(context):
    # Creates a fresh page (tab) from the context
    page = context.new_page()
    yield page  # gives the page to tests
    page.close()  # teardown after test


# 1) Enable video recording for every test context
@pytest.fixture(scope="session")
def brower_context_args(browser_context_args):
    os.makedirs("Videos", exist_ok=True)
    return {
        **browser_context_args,
        "record_video_dir": "videos",
        "record_video_size": {"width": 1280, "height": 720},
    }


# 2) Capture the call-phase report so fixtures can read .rep_call
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    outcome = yield
    item.rep_call = outcome.get_result()


# 3) Start trace before the test; on failure, save trace + video to Allure
@pytest.fixture(autouse=True)
def _video_trace(page: Page, request):
    # Enable trace/video per test; keep only for failures
    # Start tracing at test start
    page.context.tracing.start(
        title=request.node.name, screenshots=True, snapshots=True, sources=True
    )
    yield
    failed = (
        request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    )
    if failed:
        # CHANGE 1: make sure folder exists
        os.makedirs("reports", exist_ok=True)
        # use the test name, not request.node (which prints empty)
        trace_path = f"reports/trace-{request.node}.zip"
        page.context.tracing.stop(path=trace_path)
        allure.attach.file(
            trace_path,
            name="Playwright Trace",
            attachment_type=allure.attachment_type.ZIP,
        )

        try:
            page.close()
        except Exception:
            pass

        # attach video as WEBM (Chromium/WebKit default)
        for v in page.video.values():
            try:
                p = v.path()
                allure.attach.file(
                    p,
                    name="Video (failure)",
                    attachment_type=allure.attachment_type.MP4,
                )
            except Exception:
                pass

    else:
        page.context.tracing.stop()


@pytest.fixture
def sf_home_page(page: Page) -> SalesforceHomePage:
    with allure.step("preconditon: Login and switch to lightning"):
        login_Page = LoginPage(page)
        login_Page.navigate_to(config.BASE_URL)
        sf_home_page = login_Page.login(config.USERNAME, config.PASSWORD)
        sf_home_page.switch_to_lightning()
        expect(page.locator(sf_home_page.home_tab)).to_be_visible()
        return sf_home_page


@pytest.fixture
def ixt_webform_nominee(sf_home_page: SalesforceHomePage) -> IxtWebFormHomePage:
    sf_home_page.click_app_launcher()
    ixt_mailbox = sf_home_page.search_and_select_ixt_mailbox_app()
    ixt_webform = ixt_mailbox.search_and_select_ixt_webform()
    return ixt_webform


# @pytest.fixture
# def ixt_webform_business(proxy_business_user: SalesforceHomePage) -> IxtWebFormHomePage:
#     proxy_business_user.click_app_launcher()
#     ixt_mailbox = proxy_business_user.search_and_select_ixt_mailbox_app()
#     ixt_webform = ixt_mailbox.search_and_select_ixt_webform()
#     return ixt_webform


@pytest.fixture
def ixt_mailbox_business(
    proxy_business_user: SalesforceHomePage, inquiry_number
) -> MailboxSyncRecordPage:
    proxy_business_user.click_app_launcher()
    ixt_mailbox = proxy_business_user.search_and_select_ixt_mailbox_app()
    ixt_mailbox_sync_home = ixt_mailbox.click_mailbox_sync_tab()
    mailbox_sync_record_page = ixt_mailbox_sync_home.open_ixt_record_business(
        inquiry_number
    )
    # mailbox_sync_record_page.assert_case_details()
    return mailbox_sync_record_page


@pytest.fixture()
def sf_admin_page(sf_home_page: SalesforceHomePage) -> SalesforceAdminPage:
    with allure.step("Goto the admin page to do a proxy login"):
        return sf_home_page.go_to_admin_page()


@pytest.fixture
def proxy_business_user(sf_admin_page: SalesforceAdminPage, common_data):
    username = common_data["Business_user_name_1"]
    sf_proxy_home_page = sf_admin_page.proxy_login(username)
    return sf_proxy_home_page


@pytest.fixture(scope="function")
def inquiry_number(request) -> str:
    file = os.path.join("data", "inquiry.json")
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file) as f:
            try:
                return json.load(f)["inquiry"]
            except json.JSONDecodeError:
                pass

    ixt_webform_nominee = request.getfixturevalue("ixt_webform_nominee")
    inquiry = ixt_webform_nominee.fill_form()

    with open(file, "w") as f:
        json.dump({"inquiry": inquiry}, f)

    return inquiry


@pytest.fixture
def immigration_home(sf_home_page: SalesforceHomePage) -> ImmigrationHomePage:
    with allure.step("Precondition: Open Immigration app"):
        sf_home_page.click_app_launcher()
        sf_home_page.search_immigration()
        immigration_home_page = sf_home_page.click_immigration()
        expect(immigration_home_page.page).to_have_url(
            re.compile(rf"^{re.escape(test_data.immigration_home_url)}")
        )
    return immigration_home_page


@pytest.fixture(scope="session")
def common_data():
    file = os.path.join("data", "common_data.json")
    with open(file) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def immigration_record_data():
    with open("data/immigration_record_data.json") as f:
        return json.load(f)  # return dict
