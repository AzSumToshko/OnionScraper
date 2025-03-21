import os

# General
NUM_WORKERS = 8  # Number of parallel processes (based on your CPU threads)
BATCH_SIZE = 100
DEFAULT_RETRIES = 3
CHROME_DEBUG_PORT = 9222
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
BASE_URL = "https://www.mobile.bg/obiavi/avtomobili-dzhipove/namira-se-v-balgariya"
DB_TIMEOUT=5

# Paths
SCREENSHOTS_FOLDER = "debug/screenshots"
MOBILE_BG_OUTPUT_FOLDER="output/mobilebg"

# Extensions
PNG_EXTENSION = ".png"
JPEG_EXTENSION = ".jpeg"

# JS Scripts
JS_SCROLL_TO_BOTTOM_SCRIPT = "window.scrollTo(0, document.body.scrollHeight);"
JS_SCROLL_TO_TOP_SCRIPT = "window.scrollTo(0, 0);"

# Tor Settings
NUM_TOR_INSTANCES = 10 # NOT IMPLEMENTED (Also it may be not necessary since single instance is working fine with 8 parallel processes)
TOR_PORT = 9050
TOR_HOST = "127.0.0.1"
TOR_CONTROL_PORT = 9051
TOR_PATH = r"C:\\tor-14.0.7\\tor\\tor.exe"
TOR_PROXY = f"socks5://{TOR_HOST}:{TOR_PORT}"
TOR_IP_CHECKER_URL = "https://check.torproject.org/api/ip"
TOR_PROXIES = {  "http": TOR_PROXY,  "https": TOR_PROXY  }

# NYM settings
NYM_CLIENT_PORT = 1081
NYM_USE_REPLY_SUBS = "true"
NYM_CLIENT_ID = "mobilebg_client_1"
NYM_CLIENT_PATH = os.path.join(os.getcwd(), "src", "nym-socks5-client.exe")
NYM_CLIENT_PROVIDER = "Entztfv6Uaz2hpYHQJ6JKoaCTpDL5dja18SuQWVJAmmx.Cvhn9rBJw5Ay9wgHcbgCnVg89MPSV5s2muPV2YF1BXYu@Fo4f4SQLdoyoGkFae5TpVhRVoXCF8UiypLVGtGjujVPf"

# SeleniumBase Driver settings
SELENIUMBASE_UC_MODE = True
SELENIUMBASE_INCOGNITO_MODE = True
SELENIUMBASE_HEADLESS_MODE = True
SELENIUMBASE_DISABLE_CSR_MODE = True
SELENIUMBASE_DISPLAY_WIDTH = 1920
SELENIUMBASE_DISPLAY_HEIGHT = 1080