import os
from multiprocessing import Pool

from src.mobile_bg.db_service import *
from src.shared.service.logger_service import LoggingService
from src.shared.service.request_service import RequestService
from src.mobile_bg.parser_service import parse_listings, parse_brands, parse_models, parse_post, extract_last_page
from config import BASE_URL, NUM_WORKERS, MOBILE_BG_OUTPUT_FOLDER
from src.shared.utils.tor_proxy_manager import TorManager

logger = LoggingService().initialize_logger()

def scrape_mobile_bg():
    tor = TorManager()

    try:
        tor.start()
        proxy = tor.proxies["http"]

        brands_file, posts_file = __setup_output_folders()

        __init_databases(brands_file, posts_file)

        __phase_one_brands(proxy, brands_file)

        if get_brands_count(brands_file) > 0:
            __phase_two_models(proxy, brands_file)

            __phase_three_listings(proxy, brands_file, posts_file)

        else:
            raise Exception(f"❌ Phase 1: Scraping all brands did not return a response ❌")

    except Exception as e:
        tor.stop()
        logger.warn(str(e))
        return False

    finally:
        tor.stop()
        logger.info("🎉 Scraping completed successfully! 🚀")
        return True


# Separate functions for each phases
def scrape_mobile_bg_phase_one_only():
    tor = TorManager()

    try:
        tor.start()
        proxy = tor.proxies["http"]

        brands_file, posts_file = __setup_output_folders()

        __init_databases(brands_file, posts_file)

        __phase_one_brands(proxy, brands_file)

    except Exception as e:
        tor.stop()
        logger.warn(str(e))
        return False

    finally:
        tor.stop()
        logger.info("🎉 Phase one successfully finished! 🚀")
        return True

def scrape_mobile_bg_phase_two_only(folder: str):
    tor = TorManager()

    output_folder = os.path.join(MOBILE_BG_OUTPUT_FOLDER, folder)

    brands_file = os.path.join(output_folder, "brands.db")

    try:
        if not os.path.exists(brands_file):
            raise FileNotFoundError(f"❌ Brands file not found: {brands_file} ❌")

        tor.start()
        proxy = tor.proxies["http"]

        __phase_two_models(proxy, brands_file)

    except Exception as e:
        tor.stop()
        logger.warn(str(e))
        return False

    finally:
        tor.stop()
        logger.info("🎉 Phase one successfully finished! 🚀")
        return True

def scrape_mobile_bg_phase_three_only(folder: str):
    tor = TorManager()

    output_folder = os.path.join(MOBILE_BG_OUTPUT_FOLDER, folder)

    brands_file = os.path.join(output_folder, "brands.db")
    posts_file = os.path.join(output_folder, "posts.db")

    try:
        tor.start()
        proxy = tor.proxies["http"]

        __phase_three_listings(proxy, brands_file, posts_file)

    except Exception as e:
        tor.stop()
        logger.warn(str(e))
        return False

    finally:
        tor.stop()
        logger.info("🎉 Phase one successfully finished! 🚀")
        return True


# Private Utility functions
def __setup_output_folders(base_path=MOBILE_BG_OUTPUT_FOLDER):
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    output_folder = os.path.join(base_path, timestamp)

    os.makedirs(output_folder, exist_ok=True)

    return os.path.join(output_folder, "brands.db"), os.path.join(output_folder, "posts.db")

def __init_databases(brands_file, posts_file):
    create_brands_database(brands_file)
    create_posts_database(posts_file)


# Phases
def __phase_one_brands(proxy, brands_file):
    logger.info("🔍 Phase 1: Scraping all brands... 🔍")

    try:
        brands = parse_brands(RequestService(proxy).fetch_page_seleniumbase(BASE_URL))
        insert_brands_bulk(brands_file, brands)

        logger.info("✅ Phase 1 Complete: Brands saved. ✅")

    except Exception as e:
        logger.warn(f"❌ Phase 1: Scraping all brands failed... Reason: {str(e)}❌")

def __phase_two_models(proxy, brands_file):
    try:
        logger.info("🔍 Phase 2: Scraping all models in parallel... 🔍")

        with Pool(processes=NUM_WORKERS) as pool:
            pool.starmap(__scrape_models, [(proxy, brand, brands_file) for brand in fetch_all_brands(brands_file)])

        logger.info("✅ Phase 2 Complete: Models saved. ✅")

    except Exception as e:
        raise Exception(f"❌ Phase 2: Scraping all models failed... Reason: {str(e)}❌")

def __phase_three_listings(proxy, brands_file, posts_file):
    try:
        logger.info("🔍 Phase 3: Scraping all listings in parallel... 🔍")

        with Pool(processes=NUM_WORKERS) as pool:
            pool.starmap(__scrape_listings, [(proxy, model, posts_file)
                                             for model in fetch_all_models(brands_file)])

        logger.info("✅ Phase 3 Complete: Listings saved. ✅")

    except Exception as e:
        raise Exception(f"❌ Phase 3: Scraping all listings failed... Reason: {str(e)}❌")


# Scraping functions
def __scrape_models(proxy, brand, brands_file):
    brand_name = brand["name"]
    brand_url = brand["url"]

    try:
        logger.info(f"🔍 Scraping models for brand: {brand_name} 🔍")

        models = parse_models(RequestService(proxy).fetch_page_seleniumbase(brand_url))
        insert_models_bulk(brands_file, brand_name, models)

    except Exception as e:
        logger.info(f"❌ Failed to scrape models for {brand_name}: {e} ❌")

    finally:
        logger.info(f"Exiting models scraping for: {brand_name}")

def __scrape_listings(proxy, model, listings_folder):
    brand_name = model["brand_name"]
    model_name = model["name"]
    model_url = model["url"]

    # logger.info(f"🔍 Scraping listings for {brand_name} - {model_name} 🔍")

    try:
        first_page_response = RequestService(proxy).fetch_page_seleniumbase(url=model_url, max_retries=3)
        if not first_page_response:
            logger.warn(f"❌ Failed to fetch first page of {model_name}. Skipping. ❌")
            return

        last_page = extract_last_page(first_page_response)
        logger.info(f"📌 Last page found: {last_page} 📌")

        for page_number in range(1, last_page + 1):
            response = RequestService(proxy).fetch_page_seleniumbase(url=f"{model_url}/p-{page_number}" if page_number > 1 else model_url, max_retries=3)

            if not response:
                logger.warn(f"❌ Failed to fetch page {page_number}. Skipping. ❌")
                continue

            page_listings = parse_listings(response, brand_name, model_name)

            if not page_listings:
                logger.info(f"✅ No more listings found for {model_name}. ✅")
                break

            for listing in page_listings:
                post_url = listing["url"]
                try:
                    post_response = RequestService(proxy).fetch_page_seleniumbase(url=post_url, max_retries=3)

                    if post_response:
                        post_details = parse_post(post_response, post_url, brand_name, model_name)

                        insert_post(listings_folder, post_details)
                    else:
                        logger.warn(f"❌ Failed to fetch post: {post_url} ❌")
                except:
                    logger.warn(f"❌ Failed to fetch post: {post_url} ❌")

        logger.info(f"✅ Saved listings for {brand_name} - {model_name}. ✅")

    except Exception as e:
        logger.warn(f"❌ Failed to scrape listings for {brand_name}: {e} ❌")

    finally:
        logger.info(f"Exiting listing scraping for: {brand_name}")