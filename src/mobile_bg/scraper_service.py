import os
import json
import time
from multiprocessing import Pool

from src.shared.logger_service import LoggingService
from src.shared.request_service import RequestService
from src.mobile_bg.parser_service import parse_listings, parse_brands, parse_models, parse_post, extract_last_page
from src.shared.data_service import save_as_csv_and_json, load_json
from config import BASE_URL, NUM_WORKERS, MOBILE_BG_OUTPUT_FOLDER
from src.shared.tor_proxy_manager import TorManager

logger = LoggingService().initialize_logger()

def scrape_mobile_bg():
    tor = TorManager()

    try:
        tor.start()
        proxy = tor.proxies["http"]

        folders, files = __setup_output_folders()

        brands = __phase_one_brands(proxy, files)

        if brands is not None and len(brands) > 0:
            __phase_two_models(proxy, folders, brands)

            __phase_three_listings(proxy, folders)

            __phase_four_posts(proxy, folders)

            __merge_all_posts(folders.get("listings_data"), files.get("posts_json"), files.get("posts_csv"))

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
    response = []

    try:
        tor.start()
        proxy = tor.proxies["http"]

        folders, files = __setup_output_folders()

        brands = __phase_one_brands(proxy, files)
        response = brands

    except Exception as e:
        tor.stop()
        logger.warn(str(e))
        return response

    finally:
        tor.stop()
        logger.info("🎉 Phase one successfully finished! 🚀")
        return response

def scrape_mobile_bg_phase_two_only(folder: str):
    tor = TorManager()

    output_folder = os.path.join(MOBILE_BG_OUTPUT_FOLDER, folder)

    folders = {
        "output": output_folder,
        "models": os.path.join(output_folder, "models"),
        "listings": os.path.join(output_folder, "listings"),
        "listings_data": os.path.join(output_folder, "listings_data"),
    }

    try:
        brands_file = os.path.join(output_folder, "brands.json")
        if not os.path.exists(brands_file):
            raise FileNotFoundError(f"❌ Brands file not found: {brands_file} ❌")

        brands = load_json(brands_file)

        tor.start()
        proxy = tor.proxies["http"]
        __phase_two_models(proxy, folders, brands)

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

    folders = {
        "output": output_folder,
        "models": os.path.join(output_folder, "models"),
        "listings": os.path.join(output_folder, "listings"),
        "listings_data": os.path.join(output_folder, "listings_data"),
    }

    try:
        tor.start()
        proxy = tor.proxies["http"]

        __phase_three_listings(proxy, folders)

    except Exception as e:
        tor.stop()
        logger.warn(str(e))
        return False

    finally:
        tor.stop()
        logger.info("🎉 Phase one successfully finished! 🚀")
        return True

def scrape_mobile_bg_phase_four_only(folder: str):
    tor = TorManager()

    output_folder = os.path.join(MOBILE_BG_OUTPUT_FOLDER, folder)

    folders = {
        "output": output_folder,
        "models": os.path.join(output_folder, "models"),
        "listings": os.path.join(output_folder, "listings"),
        "listings_data": os.path.join(output_folder, "listings_data"),
    }

    try:
        tor.start()
        proxy = tor.proxies["http"]

        __phase_four_posts(proxy, folders)

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

    folders = {
        "output": output_folder,
        "models": os.path.join(output_folder, "models"),
        "listings": os.path.join(output_folder, "listings"),
        "listings_data": os.path.join(output_folder, "listings_data"),
    }

    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)

    files = {
        "brands_csv": os.path.join(output_folder, "brands.csv"),
        "brands_json": os.path.join(output_folder, "brands.json"),
        "posts_json": os.path.join(output_folder, "posts.json"),
        "posts_csv": os.path.join(output_folder, "posts.csv"),
    }

    return folders, files


# Phases
def __phase_one_brands(proxy, files):
    logger.info("🔍 Phase 1: Scraping all brands... 🔍")

    response = []

    try:
        brands = parse_brands(RequestService(proxy).fetch_page_seleniumbase(BASE_URL))
        save_as_csv_and_json(files.get("brands_csv"), files.get("brands_json"), brands, ["name", "url", "count"])

        logger.info("✅ Phase 1 Complete: Brands saved. ✅")

        response = brands

    except Exception as e:
        response = []
        logger.warn(f"❌ Phase 1: Scraping all brands failed... Reason: {str(e)}❌")

    finally:
        return response

def __phase_two_models(proxy, folders, brands):
    try:
        logger.info("🔍 Phase 2: Scraping all models in parallel... 🔍")

        with Pool(processes=NUM_WORKERS) as pool:
            pool.starmap(__scrape_models, [(proxy, brand, folders.get("models")) for brand in brands])

        logger.info("✅ Phase 2 Complete: Models saved. ✅")

    except Exception as e:
        raise Exception(f"❌ Phase 2: Scraping all models failed... Reason: {str(e)}❌")

def __phase_three_listings(proxy, folders):
    try:
        logger.info("🔍 Phase 3: Scraping all listings in parallel... 🔍")

        model_files = [os.path.join(folders.get("models"), file) for file in os.listdir(folders.get("models")) if
                       file.endswith(".json")]

        with Pool(processes=NUM_WORKERS) as pool:
            pool.starmap(__scrape_listings, [(proxy, model, folders.get("listings"))
                                             for model in model_files])

        logger.info("✅ Phase 3 Complete: Listings saved. ✅")

    except Exception as e:
        raise Exception(f"❌ Phase 3: Scraping all listings failed... Reason: {str(e)}❌")

def __phase_four_posts(proxy, folders):
    try:
        logger.info("🔍 Phase 4: Scraping all post details in parallel... 🔍")

        listings_files = [os.path.join(folders.get("listings"), file) for file in os.listdir(folders.get("listings")) if
                          file.endswith(".json")]

        with Pool(processes=NUM_WORKERS) as pool:
            pool.starmap(__scrape_post_details,
                         [(proxy, listings_file, folders.get("listings_data")) for listings_file in listings_files])

        logger.info(f"✅ Phase 4 Complete: Posts saved. ✅")

    except Exception as e:
        raise Exception(f"❌ Phase 4: Scraping all posts failed... Reason: {str(e)}❌")



# Scraping functions
def __scrape_models(proxy, brand, models_folder):
    brand_name = brand["name"]
    brand_url = brand["url"]

    try:
        logger.info(f"🔍 Scraping models for brand: {brand_name} 🔍")

        models = parse_models(RequestService(proxy).fetch_page_seleniumbase(brand_url))

        brand_models_json = os.path.join(models_folder, f"{brand_name}.json")
        brand_models_csv = os.path.join(models_folder, f"{brand_name}.csv")

        save_as_csv_and_json(brand_models_csv, brand_models_json, models, ["name", "url", "count"])

    except Exception as e:
        logger.info(f"❌ Failed to scrape models for {brand_name}: {e} ❌")

    finally:
        logger.info(f"Exiting models scraping for: {brand_name}")

def __scrape_listings(proxy, model_file, listings_folder):
    brand_name = os.path.splitext(os.path.basename(model_file))[0]

    try:
        with open(model_file, "r", encoding="utf-8") as f:
            models = json.load(f)

        for model in models:
            model_name = model["name"]
            model_url = model["url"]

            logger.info(f"🔍 Scraping listings for {brand_name} - {model_name} 🔍")
            first_page_response = RequestService(proxy).fetch_page_seleniumbase(url=model_url, max_retries=3)
            if not first_page_response:
                logger.warn(f"❌ Failed to fetch first page of {model_name}. Skipping. ❌")
                return

            last_page = extract_last_page(first_page_response)
            logger.info(f"📌 Last page found: {last_page} 📌")

            model_listings_json = os.path.join(listings_folder, f"{brand_name}_{model_name}.json")
            model_listings_csv = os.path.join(listings_folder, f"{brand_name}_{model_name}.csv")

            listings = []

            for page_number in range(1, last_page + 1):
                page_url = f"{model_url}/p-{page_number}" if page_number > 1 else model_url
                response = RequestService(proxy).fetch_page_seleniumbase(url=page_url, max_retries=3)

                if not response:
                    logger.warn(f"❌ Failed to fetch page {page_number}. Skipping. ❌")
                    continue

                page_listings = parse_listings(response, brand_name, model_name)

                if not page_listings:
                    logger.info(f"✅ No more listings found for {model_name}. ✅")
                    break

                listings.extend(page_listings)

            save_as_csv_and_json(model_listings_csv, model_listings_json, listings, ["brand", "model", "title", "url", "price", "image"])
            logger.info(f"✅ Saved {len(listings)} listings for {brand_name} - {model_name}. ✅")

    except Exception as e:
        logger.warn(f"❌ Failed to scrape listings for {brand_name}: {e} ❌")

    finally:
        logger.info(f"Exiting listing scraping for: {brand_name}")

def __scrape_post_details(proxy, listings_file, listings_data_folder):
    with open(listings_file, "r", encoding="utf-8") as f:
        listings = json.load(f)

    brand_model_name = os.path.basename(listings_file).replace(".json", "")  # Extract brand_model from filename
    output_json = os.path.join(listings_data_folder, f"{brand_model_name}_posts.json")
    output_csv = os.path.join(listings_data_folder, f"{brand_model_name}_posts.csv")

    try:
        posts = []

        for listing in listings:
            post_url = listing["url"]
            brand_name = listing["brand"]
            model_name = listing["model"]
            try:
                post_response = RequestService(proxy).fetch_page_seleniumbase(url=post_url, max_retries=3)

                if post_response:
                    post_details = parse_post(post_response, post_url, brand_name, model_name)
                    posts.append(post_details)
                    logger.info(f"✅ Extracted post: {post_details['title']} ✅")
                else:
                    logger.warn(f"❌ Failed to fetch post: {post_url} ❌")
            except:
                logger.warn(f"❌ Failed to fetch post: {post_url} ❌")

        if posts:
            save_as_csv_and_json(output_csv, output_json, posts, posts[0].keys())
            logger.info(f"✅ Saved {len(posts)} posts for {brand_model_name}. ✅")

    except:
        logger.warn(f"❌ Failed to fetch posts for: {brand_model_name} ❌")

    finally:
        logger.info(f"Exiting post details scraping for: {brand_model_name}")

def __merge_all_posts(listings_data_folder, final_json, final_csv):
    try:
        all_posts = []

        for file in os.listdir(listings_data_folder):
            if file.endswith("_posts.json"):
                file_path = os.path.join(listings_data_folder, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        posts = json.load(f)
                        if isinstance(posts, list):
                            all_posts.extend(posts)
                    except json.JSONDecodeError:
                        logger.warn(f"⚠️ Error reading {file_path}. Skipping. ⚠️")

        if all_posts:
            save_as_csv_and_json(final_csv, final_json, all_posts, all_posts[0].keys())
            logger.info(f"✅ Final merged posts saved ({len(all_posts)} total posts). ✅")
        else:
            logger.warn("⚠️ No post data found to merge. ⚠️")

    except:
        logger.warn("⚠️ Failed to merge files. ⚠️")

    finally:
        logger.info(f"Exiting post details scraping for: {final_json}")