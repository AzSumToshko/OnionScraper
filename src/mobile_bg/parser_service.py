import re

from bs4 import BeautifulSoup

def parse_brands(html):
    soup = BeautifulSoup(html, "html.parser")
    brands = []

    for brand in soup.select(".marki nobr a"):
        name = brand.find("span").text.strip()

        if name == "--Всички Марки--":
            continue

        count = brand.find("n").text.strip().replace("(", "").replace(")", "")
        url = "https:" + brand["href"]
        brands.append({"name": name, "url": url, "count": count})

    brands.sort(key=lambda x: x["count"], reverse=True)

    return brands

def parse_models(html):
    soup = BeautifulSoup(html, "html.parser")

    marki_divs = soup.find_all("div", class_="marki")

    if len(marki_divs) < 2:
        print("⚠️ Warning: Second 'marki' container not found!")
        return []

    models_container = marki_divs[1]
    models = []

    for model in models_container.select("nobr a"):
        name = model.find("span").text.strip()

        if name == "--Всички--":
            continue

        count = model.find("n").text.strip().replace("(", "").replace(")", "")
        url = "https:" + model["href"]
        models.append({"name": name, "url": url, "count": count})

    return models

def extract_last_page(html):
    soup = BeautifulSoup(html, "html.parser")

    pagination = soup.select_one(".pagination")

    if not pagination:
        print("⚠️ No pagination found. Assuming single page.")
        return 1

    next_button = pagination.select_one("a.saveSlink.next")

    if next_button:
        last_page_element = next_button.find_previous_sibling("div")

        if last_page_element:
            try:
                last_page = int(last_page_element.text.strip())
                return last_page
            except ValueError:
                print("⚠️ Failed to extract last page number. Assuming 1 page.")
                return 1

    print("⚠️ Could not find last page indicator. Assuming 1 page.")
    return 1

def parse_listings(html, brand, model):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for item in soup.select(".ads2023 .item"):
        if "fakti" in item.get("class", []):
            break

        try:
            post_url = "https:" + item.select_one(".zaglavie a.title")["href"]

            title = item.select_one(".zaglavie a.title").text.strip()

            price_element = item.select_one(".price div")
            price = price_element.text.strip() if price_element else "N/A"

            image_element = item.select_one(".photo .big img")
            image_url = "https:" + image_element["src"] if image_element else None

            listings.append({
                "brand": brand,
                "model": model,
                "title": title,
                "url": post_url,
                "price": price,
                "image": image_url,
            })

        except Exception as e:
            print(f"⚠️ Error parsing listing: {e}")

    shortlist_container = soup.select_one("#shortList6")
    if shortlist_container:
        for item in shortlist_container.select(".item"):
            try:
                post_url = "https:" + item.select_one(".zaglavie a.title")["href"]
                title = item.select_one(".zaglavie a.title").text.strip()
                price_element = item.select_one(".price div")
                price = price_element.text.strip() if price_element else "N/A"
                image_element = item.select_one(".photo .big img")
                image_url = "https:" + image_element["src"] if image_element else None

                listings.append({
                    "title": title,
                    "url": post_url,
                    "price": price,
                    "image": image_url,
                })

            except Exception as e:
                print(f"⚠️ Error parsing shortlist listing: {e}")

    return listings

def parse_post(html, url, brand, model):
    soup = BeautifulSoup(html, 'html.parser')

    wrapper = soup.select_one(".ad2023")

    left = wrapper.select_one(".left")
    right = wrapper.select_one(".right")

    #Stuff from right

    title = ""
    link=url
    subtitle = ""
    post_number = ""
    location = ""
    current_price = ""
    price_history = []

    images = []
    car_params = {}
    technical_data = {}
    additional_info = ""
    extras = []

    obTitle = right.select_one(".obTitle h1")
    if obTitle:
        title = obTitle.contents[0].strip() if obTitle.contents else ""

        subtitle_span = obTitle.select_one("span")
        subtitle = subtitle_span.text.strip() if subtitle_span else ""

        post_number_div = obTitle.select_one(".obiava")
        if post_number_div:
            post_number = post_number_div.text.replace("Обява:", "").strip()

    title = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    subtitle = re.sub(r"[^a-zA-Z0-9\s]", "", subtitle)
    post_number = re.sub(r"\D", "", post_number)

    location_span = right.select_one(".carLocation span")
    if location_span:
        location = location_span.text.replace("Намира се в", "").strip()

    price_div = right.select_one(".Price")
    if price_div:
        price_text = price_div.text.strip().split("\n")[0]
        current_price = price_text

    price_history_div = right.select_one(".priceHistory statistiki")
    if price_history_div:
        price_entries = price_history_div.find_all("div")
        for i in range(3, len(price_entries), 3):
            date = price_entries[i].text.strip()
            change = price_entries[i + 1].text.strip()
            price = price_entries[i + 2].text.strip()
            price_history.append({"date": date, "change": change, "price": price})


    # Stuff from left

    image_divs = left.select(".smallPicturesGallery img")
    if image_divs:
        for img in image_divs:
            img_url = img.get("src")
            if img_url:
                full_url = f"https:{img_url}"
                images.append(full_url)

    car_params_div = left.select_one(".mainCarParams")
    if car_params_div:
        items = car_params_div.select(".item")
        for item in items:
            label = item.select_one(".mpLabel")
            value = item.select_one(".mpInfo")
            if label and value:
                car_params[label.text.strip()] = value.text.strip()

    tech_data_div = left.select_one(".techData .items")
    if tech_data_div:
        tech_items = tech_data_div.select(".item")
        for item in tech_items:
            key_div = item.select("div")[0] if len(item.select("div")) > 0 else None
            value_div = item.select("div")[1] if len(item.select("div")) > 1 else None
            if key_div and value_div:
                technical_data[key_div.text.strip()] = value_div.text.strip()

    more_info_div = left.select_one(".moreInfo .text")
    if more_info_div:
        additional_info = more_info_div.get_text(separator=" ").strip()

    extras_div = left.select_one(".carExtri")
    if extras_div:
        items_divs = extras_div.select(".items div")
        for item in items_divs:
            extras.append(item.text.strip())

    return {
        "brand": brand,
        "model": model,
        "title": title,
        "link": link,
        "subtitle": subtitle,
        "post_number": post_number,
        "location": location,
        "current_price": current_price,
        "price_history": price_history,
        "images": images,
        "car_parameters": car_params,
        "technical_data": technical_data,
        "additional_info": additional_info,
        "extras": extras
    }