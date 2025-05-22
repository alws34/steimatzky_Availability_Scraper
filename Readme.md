# 📚 Book Availability Monitor

A Flask-based web tool for monitoring book availability on [Steimatzky.co.il](https://www.steimatzky.co.il/). Add a book by name, and the app will automatically:

- 🔍 Search the site and allow manual or auto-selection of the correct result  
- ✅ Track availability for printed and digital formats  
- 💰 Show current prices per format  
- 🖋️ Display author name (with link) and full book description  
- 🖼️ Render the book cover  

It runs both standalone and inside Docker.

---

## 🚀 Features

- 📦 Immediate scraping when a new book is added (no waiting for next cron)
- 🔁 Background auto-update every hour using APScheduler
- 📚 Book metadata (cover, author, description) parsed from the product page
- ❌ Remove tracking anytime via UI
- ❓ Handles multiple results with manual selection prompt

---

## ⚙️ Running Locally

### 🔧 Manual

```bash
git clone https://github.com/YOUR_USERNAME/book-monitor.git
cd book-monitor
pip install -r requirements.txt
python app.py

Then open: http://localhost:5000
```

### 🐳 Docker
```
docker build -t book-monitor .
docker run -d -p 5000:5000 -v $(pwd)/books.json:/app/books.json book-monitor
```

OR: 
```
docker-compose up --build -d
```
please not that you may change the port (8091) to whatever port you want toi be exposed. dont change port 5000 unless changing in the code. 
in ``` docker-compose.yml ```
```
ports:
      - "8091:5000" #Change only the 8091
```

### 📦 Requirements
- Python 3.7+

- Flask

- BeautifulSoup4

- Requests

- APScheduler

All dependencies are listed in requirements.txt.