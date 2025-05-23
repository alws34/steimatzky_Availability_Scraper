from datetime import datetime
from flask import Flask, request, redirect, render_template
from scraper import check_book, resolve_book_url
import json, os
from apscheduler.schedulers.background import BackgroundScheduler
import requests

app = Flask(__name__)
BOOKS_FILE = "books.json"
EMAIL_UTILS_URL = os.environ.get("EMAIL_UTILS_URL")

def load_books():
    if not os.path.exists(BOOKS_FILE):
        return {}
    try:
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        os.rename(BOOKS_FILE, BOOKS_FILE + ".bak")
        print("⚠️ books.json was invalid. Backup saved as books.json.bak")
        return {}


def save_books(data):
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    books = load_books()
    return render_template("index.html", books=books)

@app.route("/add", methods=["POST"])
def add_book():
    name = request.form["book_name"]
    books = load_books()

    if name not in books:
        books[name] = {
            "query": name,
            "selected_url": None,
            "available_formats": [],
            "prices": {},
            "last_checked": None
        }

        # Try to resolve and scrape now
        search_result = resolve_book_url(name)
        if search_result:
            books[name]["suggestions"] = search_result
            # Optionally auto-select if only one result
            if len(search_result) == 1:
                books[name]["selected_url"] = search_result[0]["url"]
                books[name]["image"] = search_result[0].get("image")
                result = check_book(search_result[0]["url"])
                books[name]["available_formats"] = result["formats"]
                books[name]["prices"] = result["prices"]
                books[name]["last_checked"] = result["last_checked"]
                books[name]["author_name"] = result.get("author_name")
                books[name]["author_link"] = result.get("author_link")
                books[name]["description"] = result.get("description")
            else:
                books[name]["available_formats"] = []
                books[name]["prices"] = {}
        else:
            books[name]["suggestions"] = []
            books[name]["available_formats"] = []
            books[name]["prices"] = {}

        books[name]["last_checked"] = datetime.now().isoformat()
        save_books(books)

    return redirect("/")

@app.route("/remove", methods=["POST"])
def remove_book():
    name = request.form["book_name"]
    books = load_books()
    if name in books:
        del books[name]
        save_books(books)
    return redirect("/")

@app.route("/select", methods=["POST"])
def select_book_url():
    name = request.form["book_name"]
    url = request.form["selected_url"]
    books = load_books()
    if name in books:
        books[name]["selected_url"] = url
        for suggestion in books[name].get("suggestions", []):
            if suggestion["url"] == url:
                books[name]["image"] = suggestion.get("image")
                break

        # Fetch full info now
        result = check_book(url)
        books[name]["available_formats"] = result["formats"]
        books[name]["prices"] = result["prices"]
        books[name]["last_checked"] = result["last_checked"]
        books[name]["author_name"] = result.get("author_name")
        books[name]["author_link"] = result.get("author_link")
        books[name]["description"] = result.get("description")
        save_books(books)
    return redirect("/")

def scheduled_check():
    books = load_books()
    updated = False

    for name, info in books.items():
        if info.get("selected_url"):
            result = check_book(info["selected_url"])

            # Compare digital availability
            old_formats = {f["type"]: f for f in info.get("available_formats", [])}
            new_formats = {f["type"]: f for f in result["formats"]}
            was_digital_available = old_formats.get("דיגיטלי", {}).get("available", False)
            is_digital_now = new_formats.get("דיגיטלי", {}).get("available", False)

            books[name]["available_formats"] = result["formats"]
            books[name]["prices"] = result["prices"]
            books[name]["last_checked"] = result["last_checked"]

            # Send email notification if book just became available digitally
            if not was_digital_available and is_digital_now and EMAIL_UTILS_URL and not info.get("notified_digital"):
                try:
                    payload = {
                        "service": "book-monitor",
                        "subject": f"📖 Book Available Digitally: {name}",
                        "message": (
                            f"The book \"{name}\" is now available digitally!\n\n"
                            f"📱 Digital Price: {result['prices'].get('דיגיטלי', 'N/A')}\n"
                            f"📘 Printed Price: {result['prices'].get('מודפס', 'N/A')}\n"
                            f"🔗 Link: {info['selected_url']}"
                        )
                    }
                    response = requests.post(
                        f"{EMAIL_UTILS_URL.rstrip('/')}/send", json=payload, timeout=5
                    )
                    response.raise_for_status()
                    if response.status_code == 200:
                        books[name]["notified_digital"] = True
                except Exception as e:
                    print(f"❌ Failed to send email notification: {e}")

            # Fill missing image
            if not books[name].get("image"):
                for s in books[name].get("suggestions", []):
                    if s["url"] == info["selected_url"]:
                        books[name]["image"] = s.get("image")
                        break

            updated = True

        else:
            search_result = resolve_book_url(info["query"])
            books[name]["last_checked"] = datetime.now().isoformat()

            if search_result:
                books[name]["suggestions"] = search_result
                books[name]["available_formats"] = []
            else:
                books[name]["suggestions"] = []
                books[name]["available_formats"] = []

            updated = True

    if updated:
        save_books(books)
        
        

# Run background job
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_check, 'interval', hours=1)
scheduler.start()

if __name__ == "__main__":
    scheduled_check()
    app.run(debug=False, host="0.0.0.0")
