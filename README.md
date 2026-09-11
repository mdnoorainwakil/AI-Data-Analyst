# 🤖 AI Data Analyst

An AI-powered data analysis application built with Python and Streamlit.

The application allows users to upload CSV or Excel datasets, automatically understand and clean the data, explore data quality, generate summaries and visualizations, and ask questions about the dataset using natural language.

The goal of this project is to simplify the data analysis workflow by combining automated data cleaning, exploratory analysis, visualization, and AI-assisted insights in one interface.

---

## 📌 Overview

Traditional data analysis often requires multiple steps such as:

- Loading the dataset
- Understanding columns and data types
- Cleaning missing and duplicate values
- Performing exploratory data analysis
- Creating visualizations
- Writing queries for specific business questions
- Interpreting the results

This project brings these steps together into a single Streamlit application.

Users can upload their own CSV or Excel dataset and interact with the data through an easy-to-use interface.

The application automatically analyzes the structure of the uploaded dataset and adapts the analysis according to the available columns and data types.

---

## ✨ Key Features

### 📂 Dataset Upload
- Upload CSV and Excel (`.xlsx`) files.
- Automatically reads the uploaded dataset.

### 🧹 Automatic Data Cleaning
- Handles missing values and duplicate records.
- Detects numerical, categorical and date columns.
- Cleans common formatting issues in numerical data.
- Converts data into suitable formats for analysis.

### 🔍 Data Profiling
- Displays total rows and columns.
- Shows missing values and duplicate records.
- Displays column names and data types.
- Provides an overview of the uploaded dataset.

### 📊 Data Exploration
- View dataset records and statistical summaries.
- Explore numerical and categorical columns.
- Filter and analyze the uploaded data.

### 📈 Interactive Visualizations
- Generate charts based on the uploaded dataset.
- Explore trends, comparisons and distributions visually.

### 🤖 AI Data Analyst
- Ask questions about your dataset using natural language.
- AI understands the question based on the actual dataset.
- Generates an analysis plan and performs the required analysis.
- Displays the result in an easy-to-understand format.

### 🗃️ SQL Analysis
- Generates SQL queries for supported analytical questions.
- Executes read-only queries on the uploaded dataset.
- Displays the generated query and result.

### 💡 AI Insights
- Converts analytical results into simple explanations.
- Helps users understand important findings from their data.

### 🕘 Question History
- Keeps track of recent questions asked during the session.
- Allows users to review previous analysis results.

## 🔄 How It Works

The application follows a simple data analysis workflow:

```text
Upload Dataset
      ↓
Read & Understand Data
      ↓
Detect Data Types
      ↓
Clean the Dataset
      ↓
Explore Data & Generate KPIs
      ↓
Create Visualizations
      ↓
Ask Questions in Natural Language
      ↓
AI Generates Analysis Plan
      ↓
Generate & Execute SQL
      ↓
Display Results & AI Insights

## 🛠️ Tech Stack

### 💻 Programming Language
- Python

### 🌐 Framework
- Streamlit

### 📊 Data Analysis & Processing
- Pandas
- NumPy

### 📈 Data Visualization
- Plotly
- Matplotlib

### 🗄️ Database & Querying
- SQLite
- SQL

### 🤖 AI Integration
- Groq API

### ⚙️ Configuration
- python-dotenv

### 🧰 Development Tools
- VS Code
- Git
- GitHub

## ⚙️ Installation & Run

### 1. Clone the Repository

```bash
git clone https://github.com/mdnoorainwakil/AI-Data-Analyst.git
cd AI-Data-Analyst

## Create a Virtual Environment

- python -m venv venv

## Activate the Virtual Environment

- venv\Scripts\activate

## Install Dependencies

- pip install -r requirements.txt

## Configure API Key

- GROQ_API_KEY=your_api_key_here

## Run the Application

- streamlit run app/app.py



