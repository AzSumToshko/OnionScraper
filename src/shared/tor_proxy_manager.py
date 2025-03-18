import subprocess
import time

import requests
from stem import Signal
from stem.control import Controller

from config import TOR_PATH, TOR_IP_CHECKER_URL, TOR_CONTROL_PORT, TOR_PROXIES, TOR_PORT
from src.shared.logger_service import LoggingService

logger = LoggingService().initialize_logger()


def get_current_tor_ip(proxies):
    try:
        response = requests.get(TOR_IP_CHECKER_URL, proxies=proxies, timeout=5)
        ip_address = response.json().get("IP", "Unknown")
        logger.info(f"🌍 Current Tor IP: {ip_address} 🌍")
        return ip_address
    except requests.exceptions.RequestException:
        logger.warning("⚠️ Unable to fetch current Tor IP. ⚠️")
        return "Unknown"

class TorManager:
    def __init__(self, tor_path=TOR_PATH, control_port=TOR_CONTROL_PORT, port=TOR_PORT, proxies=TOR_PROXIES):
        self.path = tor_path
        self.control_port = control_port
        self.port = port
        self.proxies = proxies
        self.process = None

    def __del__(self):
        if self.process:
            try:
                self.stop()
            except:
                pass

    def start(self):
        if self.process:
            logger.info("🟢 Tor service is already running. 🟢")
            return

        try:
            logger.info("🔄 Starting Tor service... 🔄")
            self.process = subprocess.Popen([self.path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
            logger.info("✅ Tor service started successfully! ✅")
        except Exception as e:
            logger.error(f"❌ Failed to start Tor: {e}")

    def stop(self):
        if self.process:
            try:
                logger.info("🛑 Stopping Tor service... 🛑")
                self.process.terminate()
                self.process = None
                logger.info("✅ Tor service stopped successfully! ✅")
            except Exception as e:
                logger.error(f"❌ Failed to stop Tor: {e}")

    def request_new_identity(self):
        """
        Requests a new Tor IP.
        WARNING: This affects all Tor-based parallel processes and may cause interruptions and even errors.
        """
        try:
            logger.info("🔄 Requesting new Tor IP... 🔄")
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
            time.sleep(5)  # Wait for Tor to apply changes
            logger.info("✅ New Tor identity acquired.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to request new Tor identity: {e}")

    def restart(self):
        logger.info("🔄 Restarting Tor service... 🔄")
        self.stop()
        self.start()
        logger.info("✅ Tor service restarted!")