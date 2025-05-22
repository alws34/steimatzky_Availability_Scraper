import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote

def resolve_book_url(query):
    search_url = f"https://www.steimatzky.co.il/catalogsearch/result/?q={quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9",
        "Referer": "https://www.steimatzky.co.il/"
    }

    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching search results: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    for item in soup.find_all("li", class_="product-item"):
        name_tag = item.select_one("div.name a.product_link")
        image_tag = item.select_one("img.product-image-photo")

        if name_tag and image_tag:
            title = name_tag.text.strip()
            url = name_tag["href"].strip()
            image_url = image_tag["src"].strip()

            results.append({
                "title": title,
                "url": url,
                "image": image_url
            })

    return results

# def check_book(url):
#     response = requests.get(url, timeout=10)
#     soup = BeautifulSoup(response.text, "html.parser")

#     wrapper = soup.select_one(".product-wrapper")
#     if not wrapper:
#         return {
#             "formats": [],
#             "prices": {},
#             "last_checked": datetime.now().isoformat()
#         }

#     formats = []
#     prices = {}

#     # 📱 Digital
#     digital = wrapper.select_one(".digital_book")
#     if digital:
#         price_tag = digital.select_one(".price .price-wrapper .price")
#         price = price_tag.get_text(strip=True) if price_tag else "?"
#         formats.append({
#             "type": "דיגיטלי",
#             "available": True,
#             "price": price
#         })
#         prices["דיגיטלי"] = price
#     else:
#         formats.append({
#             "type": "דיגיטלי",
#             "available": False,
#             "price": None
#         })

#     # Check for physical format — prefer .regular_book, else fall back to main price
#     printed = wrapper.select_one(".regular_book")
#     if printed:
#         price_tag = printed.select_one(".price .price-wrapper .price")
#         price = price_tag.get_text(strip=True) if price_tag else "?"
#         formats.append({
#             "type": "מודפס",
#             "available": True,
#             "price": price
#         })
#         prices["מודפס"] = price
#     else:
#         # Only add if not already added
#         if "מודפס" not in prices:
#             price_tag = wrapper.select_one(".price .price-wrapper .price")
#             if price_tag:
#                 price = price_tag.get_text(strip=True)
#                 formats.append({
#                     "type": "מודפס",
#                     "available": True,
#                     "price": price
#                 })
#                 prices["מודפס"] = price
#             else:
#                 formats.append({
#                     "type": "מודפס",
#                     "available": False,
#                     "price": None
#                 })

#     return {
#         "formats": formats,
#         "prices": prices,
#         "last_checked": datetime.now().isoformat()
#     }



from bs4 import BeautifulSoup
from datetime import datetime
import requests

def check_book(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    wrapper = soup.select_one(".product-wrapper")
    if not wrapper:
        return {
            "formats": [],
            "prices": {},
            "last_checked": datetime.now().isoformat(),
            "image": None,
            "author_name": None,
            "author_link": None,
            "description": None
        }

    formats = []
    prices = {}

    # 📱 Digital
    digital = wrapper.select_one(".digital_book")
    if digital:
        price_tag = digital.select_one(".price .price-wrapper .price")
        price = price_tag.get_text(strip=True) if price_tag else "?"
        formats.append({
            "type": "דיגיטלי",
            "available": True,
            "price": price
        })
        prices["דיגיטלי"] = price
    else:
        formats.append({
            "type": "דיגיטלי",
            "available": False,
            "price": None
        })

    # 📘 Printed
    printed = wrapper.select_one(".regular_book")
    if printed:
        price_tag = printed.select_one(".price .price-wrapper .price")
        price = price_tag.get_text(strip=True) if price_tag else "?"
        formats.append({
            "type": "מודפס",
            "available": True,
            "price": price
        })
        prices["מודפס"] = price
    else:
        if "מודפס" not in prices:
            price_tag = wrapper.select_one(".price .price-wrapper .price")
            if price_tag:
                price = price_tag.get_text(strip=True)
                formats.append({
                    "type": "מודפס",
                    "available": True,
                    "price": price
                })
                prices["מודפס"] = price
            else:
                formats.append({
                    "type": "מודפס",
                    "available": False,
                    "price": None
                })

    # 🖼️ Image
    img_tag = wrapper.select_one(".product-page-gallery img")
    image = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

    # 👤 Author
    author_tag = wrapper.select_one(".author a")
    author_name = author_tag.text.strip() if author_tag else None
    author_link = f"https://www.steimatzky.co.il{author_tag['href']}" if author_tag else None

    # 📖 Description
    desc_tag = wrapper.select_one("li.product-detail.description")
    description = ""
    if desc_tag:
        short = desc_tag.select_one("span.product-short-desc")
        rest = desc_tag.select_one("span.product-rest-desc")
        if short:
            description += short.decode_contents().strip()
        if rest:
            description += rest.decode_contents().strip()

    return {
        "formats": formats,
        "prices": prices,
        "last_checked": datetime.now().isoformat(),
        "image": image,
        "author_name": author_name,
        "author_link": author_link,
        "description": description or None
    }
