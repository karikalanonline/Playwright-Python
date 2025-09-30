import pytest, re, os, allure, json, time
from playwright.sync_api import Playwright, Page, expect
from pages.login_page import LoginPage
from utils import config
from utils.date_utils import date_from_value
from pathlib import Path
from playwright.sync_api import expect as pw_expect, Page
from data import test_data
from pages.salesforce_home_page import SalesforceHomePage
from pages.immi_home_page import ImmigrationHomePage
from pages.ixt_mailbox_home_page import IxtMailboxApp
from pages.mailbox_sync_home_page import MailboxSyncHomePage
from pages.ixt_webform_home_page import IxtWebFormHomePage
from pages.salesforce_admin_page import SalesforceAdminPage
from pages.mailbox_sync_record_page import MailboxSyncRecordPage
from pages.custom_email_II_page import CustomEmailPage
from playwright.sync_api import TimeoutError as PWTimeoutError

INQUIRY_FILE = Path(__file__).parent / "data" / "inquiry.json"

BASE = Path(
    __file__
).parent.parent  # adjust if conftest is at project root under tests/
COMMON_PATH = BASE / "data" / "common_data.json"
TESTDATA_PATH = Path(__file__).resolve().parent / "data" / "web_form_values.json"
print("DEBUG: Looking for web_form_values.json at:", TESTDATA_PATH)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pytest_addoption(parser):
    """
    Add a command-line option '--tc' to pass a single test-case id or
    multiple comma-separated ids: --tc=TC-100 or --tc=TC-100,TC-200
    """
    parser.addoption(
        "--tc",
        action="store",
        default="",
        help="Run only the test data record(s) matching the TC id(s), comma separated.",
    )


def _normalize_key(k: str) -> str:
    # convert "Upcoming Travel Start Date" -> "upcoming_travel_start"
    s = k.strip()
    s = s.replace("-", " ").replace("/", " ")
    s = re.sub(r"\s+", "_", s)  # spaces -> _
    s = re.sub(r"[^0-9a-zA-Z_]", "", s)  # drop other punctuation
    return s.lower()


def pytest_generate_tests(metafunc):
    # only parametrize tests that request 'data'
    if "data" not in metafunc.fixturenames:
        return

    common = load_json(COMMON_PATH) if COMMON_PATH.exists() else {}
    all_data = load_json(TESTDATA_PATH)

    tc_option = metafunc.config.option.tc.strip()
    if tc_option:
        wanted = {s.strip() for s in tc_option.split(",") if s.strip()}
        filtered = [d for d in all_data if d.get("tc_id") in wanted]
        if not filtered:
            raise pytest.UsageError(
                f"No test data found for tc id(s): {', '.join(wanted)}"
            )
        param_list = filtered
    else:
        param_list = all_data

    prepared = []
    ids = []
    for d in param_list:
        # create merged copy: start with common, update with per-test
        merged = dict(common)  # shallow copy of common
        merged.update(d)  # per-test overrides common
        # normalize keys if you used mixed-case in JSON (optional)
        # convert date offsets (if present)
        if merged.get("upcoming_travel_start"):
            merged["upcoming_travel_start_formatted"] = date_from_value(
                merged["upcoming_travel_start"], "%m/%d/%Y"
            )
        if merged.get("upcoming_travel_end"):
            merged["upcoming_travel_end_formatted"] = date_from_value(
                merged["upcoming_travel_end"], "%m/%d/%Y"
            )

        prepared.append(merged)
        ids.append(merged.get("tc_id", "no-id"))

    metafunc.parametrize("data", prepared, ids=ids)


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


def get_sf_credentials_from_env():
    return [
        {
            "user": os.getenv("sf1_user", config.USERNAME),
            "password": os.getenv("sf1_password", config.PASSWORD),
        },
        {
            "user": os.getenv("sf2_user", config.USERNAME),
            "password": os.getenv("sf2_password", config.PASSWORD),
        },
    ]


@pytest.fixture(scope="session")
def common_data():
    file = os.path.join("data", "common_data.json")
    with open(file) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def users():
    file = os.path.join("data", "users.json")
    with open(file) as f:
        return json.load(f)


@pytest.fixture
def sf_home_page(request, page: Page) -> SalesforceHomePage:
    # if used normally (no param), it logs with config.USERNAME/config.PASSWORD
    # if used with indirect param, request.param must be dict: {"user":..., "password"..}
    if hasattr(request, "param") and isinstance(request.param, dict):
        creds = request.param
    else:
        creds = {
            "user": os.getenv("sf_user", getattr(config, "USERNAME")),
            "password": os.getenv("sf_password", getattr(config, "PASSWORD")),
        }
    with allure.step(f"preconditon: Login as {creds['user']} and switch to lightning"):
        login_Page = LoginPage(page)
        login_Page.navigate_to(config.BASE_URL)
        sf_home_page = login_Page.login(creds["user"], creds["password"])
        sf_home_page.switch_to_lightning()
        expect(page.locator(sf_home_page.home_tab)).to_be_visible()
        return sf_home_page


@pytest.fixture
def ixt_webform_nominee(sf_home_page: SalesforceHomePage) -> IxtWebFormHomePage:
    sf_home_page.click_app_launcher()
    ixt_mailbox = sf_home_page.search_and_select_ixt_mailbox_app()
    ixt_webform = ixt_mailbox.search_and_select_ixt_webform()
    return ixt_webform


@pytest.fixture
def custom_email_page(
    mailbox_record_page_business: MailboxSyncRecordPage,
) -> CustomEmailPage:
    custom_email_page = mailbox_record_page_business.click_email_link()
    return custom_email_page


@pytest.fixture()
def sf_admin_page(sf_home_page: SalesforceHomePage) -> SalesforceAdminPage:
    with allure.step("Goto the admin page to do a proxy login"):
        return sf_home_page.go_to_admin_page()


@pytest.fixture
def proxy_user_login(sf_admin_page: SalesforceAdminPage, users, request):
    mapping = users.get("users", {})
    key_or_value = getattr(request, "param", None)
    user_name = mapping.get("Business_user_name_1")
    if key_or_value:
        user_name = mapping.get(key_or_value, key_or_value)
    if not user_name:
        raise ValueError(f"Proxy user not found for key/value: {key_or_value}")
    sf_proxy_home_page = sf_admin_page.proxy_login(user_name)
    return sf_proxy_home_page


@pytest.fixture
def mailbox_record_page_business(
    proxy_user_login: SalesforceHomePage,
) -> MailboxSyncRecordPage:
    file = os.path.join("data", "inquiry.json")
    inquiry_id = None
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            with open(file, "r", encoding="utf-8") as f:
                inquiry_id = json.load(f).get("inquiry")
        except Exception:
            pass

    if not inquiry_id:
        raise RuntimeError("No inquiry id found in data/inquiry.json")
    proxy_user_login.switch_to_lightning()
    proxy_user_login.click_app_launcher()
    # proxy_user_login.search_and_select_ixt_mailbox_app()
    ixt_mailbox_sync_home = proxy_user_login.click_mailbox_sync_tab()
    # ixt_mailbox = proxy_user_login.search_and_select_ixt_mailbox_app()
    # ixt_mailbox_sync_home = ixt_mailbox.click_mailbox_sync_tab()
    mailbox_sync_record_page = ixt_mailbox_sync_home.open_ixt_record_business(
        inquiry_id
    )
    # mailbox_sync_record_page.assert_case_details()
    return mailbox_sync_record_page


@pytest.fixture
def select_list_view(proxy_mailbox_sync_home_page, common_data, request):
    mapping = common_data.get("list_view_name", {})
    key = getattr(request, "param", None) or "All"
    list_view_name = mapping.get(key, key)
    if not list_view_name:
        raise ValueError(f"List view not found for {key!r}")

    proxy_mailbox_sync_home_page.go_to_list_view(list_view_name)
    # mailbox_sync_home_page.assert_list_view_loaded(list_view_name)
    return proxy_mailbox_sync_home_page


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
def immigration_record_data():
    with open("data/immigration_record_data.json") as f:
        return json.load(f)  # return dict


@pytest.fixture
def ixt_mailbox_app_home_page(
    sf_home_page: SalesforceHomePage,
) -> IxtMailboxApp:
    sf_home_page.switch_to_lightning()
    sf_home_page.click_app_launcher()
    mailbox_app_home_page = sf_home_page.search_and_select_ixt_mailbox_app()
    return mailbox_app_home_page


@pytest.fixture
def mailbox_sync_home_page(
    ixt_mailbox_app_home_page: IxtMailboxApp,
) -> MailboxSyncHomePage:
    mailbox_sync_home_page = ixt_mailbox_app_home_page.click_mailbox_sync_tab()
    return mailbox_sync_home_page


@pytest.fixture
def proxy_mailbox_sync_home_page(
    proxy_user_login: SalesforceHomePage,
) -> MailboxSyncHomePage:
    proxy_user_login.switch_to_lightning()
    proxy_user_login.click_app_launcher()
    proxy_mailbox_sync_home_page = proxy_user_login.click_mailbox_sync_tab()
    return proxy_mailbox_sync_home_page


@pytest.fixture(scope="function")
def clear_inquiry_key():
    """Remove the legacy 'inquiry' (and optional '_latest') keys but keep other mapping data."""
    file = Path(__file__).parent / "data" / "inquiry.json"
    if file.exists() and file.stat().st_size > 0:
        try:
            data = json.loads(file.read_text(encoding="utf-8")) or {}
            removed = False
            for k in ("inquiry", "_latest"):
                if k in data:
                    data.pop(k, None)
                    removed = True
            if removed:
                file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                print("DEBUG: removed 'inquiry'/_latest from inquiry.json")
        except Exception as e:
            print("DEBUG: clear_inquiry_key fallback - removing file due to error:", e)
            try:
                file.unlink()
            except Exception:
                pass
    yield


@pytest.fixture(scope="function")
def get_inquiry_number(request, data) -> str:
    file = os.path.join("data", "inquiry.json")
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            with open(file, "r", encoding="utf-8") as f:
                val = json.load(f).get("inquiry")
                if val:
                    return val
        except json.JSONDecodeError:
            pass

    # ixt_webform_nominee is already a fixture param (page object)
    ixt_webform_nominee = request.getfixturevalue("ixt_webform_nominee")
    inquiry = ixt_webform_nominee.fill_form(data)  # pass the data dict

    with open(file, "w", encoding="utf-8") as f:
        json.dump({"inquiry": inquiry}, f)
    return inquiry


# @pytest.fixture
# def select_list_view_factory(mailbox_sync_home_page: MailboxSyncHomePage, common_data):
#     mapping = common_data.get("list_view_name", {})

#     def _select(key_or_label: str):
#         list_view_name = mapping.get(key_or_label, key_or_label)
#         if not list_view_name:
#             raise ValueError("List view 'All' not fount")
#         mailbox_sync_home_page.go_to_list_view(list_view_name)
#         mailbox_sync_home_page.assert_list_view_loaded(list_view_name)
#         return mailbox_sync_home_page

#     return _select

# @pytest.fixture
# def proxy_business_user(sf_admin_page: SalesforceAdminPage, common_data):
#     username = common_data["Business_user_name_1"]
#     sf_proxy_home_page = sf_admin_page.proxy_login(username)
#     return sf_proxy_home_page

# @pytest.fixture
# def mailbox_record_page_business(
#     proxy_business_user: SalesforceHomePage,
# ) -> MailboxSyncRecordPage:
#     file = os.path.join("data", "inquiry.json")
#     inquiry_id = None
#     if os.path.exists(file) and os.path.getsize(file) > 0:
#         try:
#             with open(file, "r", encoding="utf-8") as f:
#                 inquiry_id = json.load(f).get("inquiry")
#         except Exception:
#             pass

#     if not inquiry_id:
#         raise RuntimeError("No inquiry id found in data/inquiry.json")
#     proxy_business_user.click_app_launcher()
#     ixt_mailbox = proxy_business_user.search_and_select_ixt_mailbox_app()
#     ixt_mailbox_sync_home = ixt_mailbox.click_mailbox_sync_tab()
#     mailbox_sync_record_page = ixt_mailbox_sync_home.open_ixt_record_business(
#         inquiry_id
#     )
#     # mailbox_sync_record_page.assert_case_details()
#     return mailbox_sync_record_page

# INQUIRY_FILE = Path(__file__).parent / "data" / "inquiry.json"


# def _read_inquiry_mapping():
#     if not INQUIRY_FILE.exists() or INQUIRY_FILE.stat().st_size == 0:
#         return {}
#     try:
#         return json.loads(INQUIRY_FILE.read_text(encoding="utf-8")) or {}
#     except Exception:
#         return {}


# def _write_inquiry_mapping(mapping: dict):
#     tmp = INQUIRY_FILE.with_suffix(".tmp")
#     INQUIRY_FILE.parent.mkdir(parents=True, exist_ok=True)
#     with tmp.open("w", encoding="utf-8") as f:
#         json.dump(mapping, f, indent=2)
#         f.flush()
#         os.fsync(f.fileno())
#     tmp.replace(INQUIRY_FILE)


# @pytest.fixture(scope="function", name="inquiry_number")
# def inquiry_number_always_submit(data, ixt_webform_nominee) -> str:
#     """
#     ALWAYS submit the webform for the given test data 'data' (function-scoped).
#     After submission persist mapping:
#        { "<tc_id>": "<IXT-...>", "_latest": "<IXT-...>" }
#     Return the created inquiry id (the created/current one).
#     """
#     tc = data.get("tc_id")
#     if not tc:
#         raise RuntimeError("test data must include 'tc_id'")

#     # 1) Submit the form (always)
#     new_inquiry = ixt_webform_nominee.fill_form(data)
#     if not new_inquiry:
#         raise RuntimeError("fill_form did not return an inquiry id")

#     # 2) Persist mapping: per-tc and also update special "_latest"
#     mapping = _read_inquiry_mapping()
#     mapping[tc] = new_inquiry
#     mapping["_latest"] = new_inquiry
#     _write_inquiry_mapping(mapping)

#     # (optional) navigate back so the same tab returns to SF UI (helps proxy logic)
#     try:
#         # ixt_webform_nominee.go_back_to_salesforce_page() should exist on your page object
#         ixt_webform_nominee.go_back_to_salesforce_page()
#         ixt_webform_nominee.page.wait_for_load_state("domcontentloaded", timeout=10000)
#     except Exception:
#         # best-effort, not fatal
#         pass

#     return new_inquiry


# @pytest.fixture(scope="session", name="latest_inquiry_id")
# def latest_inquiry_id_fixture():
#     """
#     Return the latest stored inquiry id from data/inquiry.json (session-scoped).
#     If file missing or key missing, returns None.
#     """
#     mapping = _read_inquiry_mapping()
#     return mapping.get("_latest")


# # helper to get mapping within tests/fixtures
# @pytest.fixture(scope="session", name="inquiry_mapping")
# def inquiry_mapping_fixture():
#     return _read_inquiry_mapping()


# @pytest.fixture
# def proxy_business_user(sf_admin_page: SalesforceAdminPage, common_data):
#     username = common_data["Business_user_name_1"]
#     # call proxy_login which probably triggered a new tab
#     sf_admin_page.proxy_login(
#         username
#     )  # keep if it performs click; may not return the new page

#     # get the newest page in the same context
#     pages = sf_admin_page.page.context.pages
#     new_page = pages[-1]  # usually the last page is the newly opened one
#     sf_proxy_home_page = SalesforceHomePage(new_page)
#     sf_proxy_home_page.switch_to_lightning()
#     return sf_proxy_home_page


# @pytest.fixture
# def proxy_business_user(sf_admin_page: "SalesforceAdminPage", common_data):
#     username = common_data["Business_user_name_1"]

#     # call proxy_login which performs actions and returns SalesforceHomePage(self.page)
#     # we call it for its side-effect (login as the proxy user)
#     sf_admin_page.proxy_login(username)

#     # pick the candidate page from context (pages[-1] as you prefer)
#     pages = sf_admin_page.page.context.pages
#     # prefer a page that looks like Lightning home, else fallback to last page
#     proxy_page = None
#     for p in reversed(pages):
#         try:
#             u = p.url
#         except Exception:
#             continue
#         if "lightning" in u and "/home" in u:
#             proxy_page = p
#             break
#     if proxy_page is None:
#         proxy_page = pages[-1]

#     # ensure Playwright focuses the proxy page/tab
#     try:
#         proxy_page.bring_to_front()
#     except Exception:
#         pass

#     sf_proxy_home_page = SalesforceHomePage(proxy_page)
#     try:
#         pw_expect(proxy_page.locator(sf_proxy_home_page.home_tab)).to_be_visible(
#             timeout=15000
#         )
#     except Exception:
#         # best-effort debug print
#         print(
#             "DEBUG: proxy_business_user: home_tab not visible after proxy_login. pages:",
#             [p.url for p in pages],
#         )

#     return sf_proxy_home_page

# def _read_inquiry_mapping():
#     if not INQUIRY_FILE.exists() or INQUIRY_FILE.stat().st_size == 0:
#         return {}
#     try:
#         return json.loads(INQUIRY_FILE.read_text(encoding="utf-8")) or {}
#     except Exception:
#         return {}
