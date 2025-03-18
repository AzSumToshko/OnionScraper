import time
from seleniumbase import Driver

from config import *
from src.shared.logger_service import LoggingService
from src.shared.tor_proxy_manager import get_current_tor_ip

logger = LoggingService().initialize_logger()

class RequestService:
    def __init__(self, proxy):
        self.driver = None
        self.proxy = proxy
        self.full_proxy = {  "http": self.proxy,  "https": self.proxy  }

    def __del__(self):
        self.__close_driver()

    def __close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🛑 WebDriver closed cleanly! 🛑")
            except Exception as e:
                logger.warning(f"⚠️ WebDriver quit failed: {e}")
        self.driver = None

    def __resolve_captcha(self):
        try:
            logger.info("🔍 Checking for captcha... 🔍")

            if self.driver.is_element_present("iframe[title*='challenge']"):

                self.driver.uc_gui_handle_captcha()
                logger.info("✅ Captcha resolved! ✅")

            else:
                logger.info("✅ No Captcha tests appeared! ✅")

        except Exception as e:
            logger.warning(f"⚠️ No captcha detected or failed to solve: {e}")

    def __handle_cookie_popup(self):
        try:
            logger.info("🔍 Checking for cookie popup in SeleniumBase... 🔍")

            if self.driver.is_element_visible("#cookiescript_reject"):

                self.driver.click("#cookiescript_reject")
                logger.info("✅ Cookie popup dismissed! ✅")

            else:
                logger.info("✅ No Cookie PopUp appeared! ✅")

        except:
            logger.warning(f"⚠️ No cookie popup detected or failed to dismiss it. ⚠️")

    def __scroll_page(self):
        try:
            logger.info("🔄 Scrolling to trigger Lazy Loading... 🔄")

            self.driver.execute_script(JS_SCROLL_TO_BOTTOM_SCRIPT)
            time.sleep(2)
            self.driver.execute_script(JS_SCROLL_TO_TOP_SCRIPT)

            logger.info("✅ Scrolling completed! ✅")

        except Exception as e:
            logger.warning(f"⚠️ Scrolling failed: {e}")

    def __take_screenshot(self, filename="screenshot"):
        try:
            screenshot_path = os.path.join(SCREENSHOTS_FOLDER, filename + PNG_EXTENSION)
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

            self.driver.save_screenshot(screenshot_path)

            logger.info(f"📸 Screenshot saved: {screenshot_path} 📸")

        except Exception as e:
            logger.warning(f"⚠️ Failed to take screenshot: {e}")

    def fetch_page_seleniumbase(self, url, max_retries=DEFAULT_RETRIES):
        for attempt in range(max_retries):
            try:
                logger.info(f"🚀 Fetching page with SeleniumBase: {url} using: {self.proxy} 🚀")

                self.driver = Driver(
                    uc              =       SELENIUMBASE_UC_MODE,
                    incognito       =       SELENIUMBASE_INCOGNITO_MODE,
                    headless        =       SELENIUMBASE_HEADLESS_MODE,
                    disable_csp     =       SELENIUMBASE_DISABLE_CSR_MODE,
                    d_width         =       SELENIUMBASE_DISPLAY_WIDTH,
                    d_height        =       SELENIUMBASE_DISPLAY_HEIGHT,
                    proxy           =       self.proxy,
                )

                logger.info(f"🌍 Using Tor | Attempt: {attempt + 1} | IP: {get_current_tor_ip(self.full_proxy)} | Agent: {self.driver.get_user_agent()} 🌍")

                self.driver.uc_open_with_reconnect(url)

                self.__resolve_captcha()

                self.__handle_cookie_popup()

                self.__resolve_captcha()

                self.__scroll_page()

                html = self.driver.get_page_source()

                logger.info(f"✅ Page {url} successfully retrieved with SeleniumBase! ✅")
                return html

            except Exception as e:
                logger.error(f"❌ SeleniumBase failed to fetch page: {url}.\n Trying again... \nReason: {str(e)}❌")

                self.__close_driver()

            finally:
                self.__close_driver()

        logger.error(f"🚨 All retries failed! Unable to fetch page: {url} 🚨")
        return None