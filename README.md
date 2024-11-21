# ChatBot_CP

A chatbot application designed for legal document analysis and query handling, powered by Python (FastAPI backend) and React (frontend). This project integrates MongoDB for persistent storage and includes utilities for processing legal documents.

---

## Features
- Process legal PDFs and extract key information.
- Search and query legal domains interactively.
- Frontend UI for user interaction.
- FastAPI backend with modular services.
- Integration with MongoDB for efficient data handling.

---

## Table of Contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
6. [License](#license)

---

## Requirements

Before you begin, ensure you have the following installed:
- **Python 3.9 or later**
- **Node.js** (for the React frontend)
- **MongoDB** (local or cloud instance)
- **Docker** (optional, for containerization)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ChatBot_CP.git
cd ChatBot_CP
```

### 2. Set Up the Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Set Up MongoDB
1. Ensure MongoDB is running locally or set up a remote MongoDB connection.
2. Modify the MongoDB connection URI in `backend/main.py` if needed.

### 4. Process Legal Documents
1. Place your legal PDFs in the `data` directory.
2. Run the script to load them into MongoDB:
   ```bash
   python helpers/load_pdfs.py
   ```

### 5. Set Up the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

---

## Usage

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```
   The FastAPI backend will be available at [http://localhost:8000](http://localhost:8000).

2. Access the frontend:
   Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

3. Interact with the chatbot to analyze and query legal documents.

---

## Project Structure
```plaintext
ChatBot_CP/
├── backend/                     # Backend (FastAPI)
│   ├── ContextMatcherService.py
│   ├── ExtendedContextMatcherService.py
│   ├── GenerateResponseService.py
│   ├── MongoDBHandler.py
│   ├── main.py                  # Backend entry point
│   ├── legal_fields/            # Legal domain data
│   ├── tests/                   # Backend tests
│   └── requirements.txt
├── data/                        # Persistent data (MongoDB)
├── frontend/                    # Frontend (React)
│   ├── src/                     # React source files
│   └── public/                  # React public assets
├── helpers/                     # Helper scripts
│   ├── load_pdfs.py             # PDF loader script
│   └── scraper.py               # Data scraper script
├── docker-compose.yml           # Docker configuration
├── LICENSE                      # Project license
└── README.md                    # Documentation
```

## License

This project is licensed under the [MIT License](LICENSE).