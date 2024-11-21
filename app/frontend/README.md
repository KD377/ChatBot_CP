## Usage

Follow these steps to set up the environment, run the scraper, set up the frontend, and start the application using Docker Compose.

### 1. Activate the Virtual Environment

```bash
# On Unix or MacOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 2. Run the Scraper

```bash
cd app/backend/helpers
python scraper.py
```

**Prompts:**
- **Years:** Enter comma-separated years (e.g., `2022,2023`) or type `all`.
- **Document Limit:** Enter the number of documents per year or `0` for all.

### 3. Set Up the Frontend

```bash
cd app/frontend
npm install
```

### 4. Build and Run with Docker Compose

```bash
cd ../../..
docker-compose up -d --build
```

### 5. Access the Frontend

Open [http://localhost:3000/](http://localhost:3000/) in your browser.
