import subprocess
import time

from config import NYM_CLIENT_PATH, NYM_CLIENT_ID, NYM_USE_REPLY_SUBS, NYM_CLIENT_PORT, NYM_CLIENT_PROVIDER
from src.shared.logger_service import LoggingService

logger = LoggingService().initialize_logger()

class NymProxyManager:

    # https://nym.com/docs/developers/clients/socks5/setup
    # https://github.com/nymtech/nym
    # https://explorer.nymtech.net/
    # https://harbourmaster.nymtech.net/

    def __init__(self):
        self.process = None
        self.proxy_address = "socks5://127.0.0.1:1083"
        self.nym_executable = NYM_CLIENT_PATH

    def __del__(self):
        if self.process:
            try:
                self.stop()
            except:
                pass

    def init_client_id(self,
                       client_id = NYM_CLIENT_ID,
                       use_reply_subs = NYM_USE_REPLY_SUBS,
                       port = NYM_CLIENT_PORT,
                       provider = NYM_CLIENT_PROVIDER):
        try:
            command = [
                self.nym_executable, "init",
                "--id", client_id,                      # Client name
                "--use-reply-surbs", use_reply_subs,    # Sets weather the user will be anonymous or not
                "--provider", provider,                 # Specifies to which provider to send the requests
                "--port", str(port),                    # Specifies the port on which the client listens
                "--latency-based-selection"             # Finds the network with the lowest latency and chooses it
            ]

            logger.info(f"🚀 Initializing Nym client '{client_id}'... 🚀")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                logger.info("✅ Nym client initialized successfully! ✅")
            else:
                logger.warn(f"❌ Nym initialization failed:\n{result.stderr} ❌")

        except Exception as e:
            logger.warn(f"⚠️ Error initializing Nym client: {e}")

    def start(self, client_id=NYM_CLIENT_ID):
        """Starts the Nym SOCKS5 client"""
        if self.process is None:
            print("🚀 Starting Nym SOCKS5 Proxy... 🚀")
            self.process = subprocess.Popen(
                [self.nym_executable, "run", "--id", client_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(5)  # Wait for Nym to initialize
            logger.info("✅ Nym Proxy Started Successfully! ✅")

    def stop(self):
        if self.process:
            logger.info("🛑 Stopping Nym Proxy... 🛑")
            self.process.terminate()
            self.process = None
            logger.info("✅ Nym Proxy Stopped ✅")

    def get_proxy(self):
        # return {
        #     "http": self.proxy_address,
        #     "https": self.proxy_address
        # }
        return self.proxy_address