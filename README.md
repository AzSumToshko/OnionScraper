# 🚀 Onion Scraper

## 📚 Description

The **Onion Scraper** is an advanced web scraper designed to extract **car listings** from [Mobile.bg](https://www.mobile.bg/) and lots of other websites while ensuring **anonymity** using **Tor and Nym proxy networks**. It supports **parallel processing**, **Selenium-based JavaScript rendering**, and **data persistence in JSON & CSV formats**.

---

## 🛠️ Prerequisites

Before running the scraper, ensure you have the following installed:

### ✅ **System Requirements**
- Python **3.10+**
- Windows / Linux / macOS
- **Tor Expert Bundle**
- **Google Chrome**
- **ChromeDriver** (compatible with your Chrome version)

---

### ✅ **Tor Installation**
The scraper uses **Tor** for anonymous requests.

1️⃣ **Download & Install Tor Expert Bundle**:
   - Go to [Tor Project](https://www.torproject.org/download/tor/) and download the **Tor Expert Bundle**.
   - Extract the archive to a directory (e.g., `C:\tor` on Windows or `/usr/local/bin/tor` on Linux).
   - Add the extracted folder to your system **PATH**.

2️⃣ **Configure `torrc`**:
   - Navigate to the Tor directory and locate the `torrc` file.
   - Modify it to include the following settings:
     ```ini
     ControlPort 9051
     CookieAuthentication 1
     MaxCircuitDirtiness 10
     ```

3️⃣ **Start Tor**:
   - Run Tor **before starting the scraper** to bootstrap connections faster.
   - On Windows:
     ```sh
     C:\tor\tor.exe
     ```
   - On Linux/Mac:
     ```sh
     tor
     ```

---

## 🔧 Installation

```sh
pip install -r requirements.txt
```

---

## 📅 Configuration

Modify **config.py** to adjust parameters such as:
- **Parallel Processing:** `NUM_WORKERS`
- **Tor Proxy Settings:** `TOR_PATH`, `TOR_PORT`, `TOR_CONTROL_PORT`
- **Data Output Paths:** `MOBILE_BG_OUTPUT_FOLDER`
- **Selenium Options:** `SELENIUMBASE_HEADLESS_MODE`, `SELENIUMBASE_DISPLAY_WIDTH`, `SELENIUMBASE_DISPLAY_HEIGHT`

Example:
```python
NUM_WORKERS = 8  # Number of parallel scraping processes
TOR_PATH = "C:\\tor\\tor.exe"  # Path to Tor binary
MOBILE_BG_OUTPUT_FOLDER = "output/mobilebg"  # Output storage
```

---

## 🚶️ Usage

### 💡 **Start Full Scraping Process**
```sh
python run.py
```

### 📃 **Scrape Only Phase Two (Models & Listings)**
```sh
python -c "from src.mobile_bg.scraper_service import scrape_mobile_bg_phase_two_only; scrape_mobile_bg_phase_two_only('your_output_folder_name')"
```

---

## 🌐 Folder Structure

```
├── output/                 # Output storage for scraped data
│   ├── mobilebg/           # Main output folder
│   │   ├── YYYY-MM-DD/     # Date-stamped scraping session
│   │   │   ├── models/     # Brand models JSON & CSV
│   │   │   ├── listings/   # Listings JSON & CSV
│   │   │   ├── listings_data/  # Extracted post details
├── src/                    # Main source code
│   ├── mobile_bg/          # Scraper logic
│   │   ├── parser_service.py   # HTML parsing functions
│   │   ├── scraper_service.py  # Main scraping execution
│   ├── shared/             # Shared utilities
│   │   ├── data_service.py      # Handles JSON & CSV storage
│   │   ├── logger_service.py    # Logging setup
│   │   ├── request_service.py   # Handles HTTP & Selenium requests
│   │   ├── tor_proxy_manager.py # Tor proxy management
│   │   ├── nym_proxy_manager.py # Nym proxy management
├── config.py               # Configuration file
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point for running the scraper
```

---

## 📁 Shared Classes

### ✅ **Logger Service (`logger_service.py`)**
Centralized logging service to standardize logs across modules.
```python
logger = LoggingService().initialize_logger()
logger.info("Scraper started!")
```

### ✅ **Request Service (`request_service.py`)**
Handles Selenium-based and direct HTTP requests with proxy support.
```python
html = RequestService(proxy).fetch_page_seleniumbase(url)
```

### ✅ **Tor Proxy Manager (`tor_proxy_manager.py`)**
Manages Tor instances, starts/stops services, and rotates IPs.
```python
tor = TorManager()
tor.start()
tor.request_new_identity()
tor.stop()
```

### ✅ **Nym Proxy Manager (`nym_proxy_manager.py`)**
Handles Nym network proxying for added anonymity.
```python
nym = NymProxyManager()
nym.start()
print(nym.get_proxy())
```

### ✅ **Data Service (`data_service.py`)**
Manages CSV & JSON storage operations.
```python
save_as_csv_and_json("output.csv", "output.json", data, fieldnames)
```

---

## 🎉 Conclusion
The **Onion Scraper** is a robust, privacy-focused web scraper with parallel scraping capabilities, data storage management, and built-in proxy support.

💪 Happy Scraping! 🚀

