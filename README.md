# OK.ru Community Post Comments Scraper

Fetch comments from a list of OK.ru **mobile** post links and save them to CSV.

> ⚠️ **Disclaimer**: Scraping may violate a website's Terms of Service and/or applicable laws. Use responsibly. This tool is provided for educational/research purposes only. You are solely responsible for how you use it.

---

## Features

- Logs into OK.ru using provided credentials (session-based)
- Reads a list of **mobile** post URLs from `input/<suffix>.txt`
- Iterates through "previous comments" pagination
- Writes UTF-8 CSV to `data/records-<suffix>-<timestamp>.csv`
- CLI flags **and** environment variable support
- Dockerized (no local Python setup required)
- Minimal, dependency-light

---
## Quick Start

### 1) Prepare input

Create a text file with **mobile** post URLs, one per line, for example:

```
https://m.ok.ru/group/1234567890/topic/1234567890
```

Save it to `input/news.txt` and then use `news` as the `--file-suffix`.

### 2) Run with Python

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python app.py "<your_email>" "<your_password>" "<fileSuffix>"
```

### 3) Or run with Docker

Build the image and run, mounting `input/` and `data/`:

```bash
docker build -t okru-scraper:latest .

# Using env vars
docker run --rm -it   -e OK_EMAIL="<your_email>"   -e OK_PASSWORD="<your_password>"   -e FILE_SUFFIX="news"   -v "$(pwd)/input:/app/input"   -v "$(pwd)/data:/app/data"   okru-scraper:latest

# Or pass CLI args directly
docker run --rm -it   -v "$(pwd)/input:/app/input"   -v "$(pwd)/data:/app/data"   okru-scraper:latest   --email "<your_email>" --password "<your_password>" --file-suffix "news"
```

---


## Development

- Python 3.10+ recommended
- `requests`, `beautifulsoup4`


## License

MIT
