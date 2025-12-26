# 📄 Research Paper Insights Dashboard

A Streamlit-powered application that uses AI (OpenAI GPT-4o) to automatically extract, analyze, and summarize key insights from academic research papers. This tool helps researchers and students quickly digest complex papers by breaking them down into structured, readable summaries.

---

## 🚀 Features

* **PDF Parsing:** Upload multiple PDF research papers simultaneously.
* **Smart Sectioning:** Automatically identifies and splits papers into logical sections (Abstract, Methodology, Results, etc.) using Regex.
* **AI Analysis:** Uses OpenAI's GPT-4o model to extract structured insights:
    * Executive Summary
    * Research Problem
    * Methodology
    * Key Findings
    * Limitations
    * Future Work
* **Modern UI:** A clean, card-based layout with high-contrast text for readability.
* **Export Options:** Download the analysis results as **CSV** or **JSON**.
* **Secure:** Supports API key injection via UI or `.env` file.

---

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [repo url]
    cd research-paper-dashboard
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install streamlit PyPDF2 openai pandas numpy python-dotenv
    ```

---

## ⚙️ Configuration

You need an OpenAI API Key to run the analysis. You can provide this in two ways:

### Option 1: .env file (Recommended)
Create a file named `.env` in the root directory and add your key:
OPENAI_API_KEY=sk-your-actual-api-key-here

### Option 2: UI Input
You can paste your API key directly into the sidebar text field when the app is running.

---

## 🏃‍♂️ Usage

1.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

2.  **Open your browser:**
    The app usually opens automatically at `http://localhost:8501`.

3.  **Analyze a paper:**
    * Upload a PDF file using the "Upload Research Papers" button.
    * (Optional) Toggle "Use Sample Data" to test the app logic immediately.
    * Click **🚀 Process Papers**.
    * View the extracted insights in the dashboard cards.
    * Export data using the download buttons at the bottom.

---

## 📂 Project Structure

research-paper-dashboard/
├── app.py                # Main Streamlit application
├── .env                  # Environment variables (Secrets)
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies

---

## 📦 Requirements

The following libraries are required to run this project:
* streamlit
* PyPDF2
* openai
* pandas
* numpy
* python-dotenv

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit a pull request.

## 📝 License

This project is licensed under the MIT License.
