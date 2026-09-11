# AI Data Analyst

An interactive AI-powered data analysis application that allows users to upload datasets, automatically clean and understand their data, explore insights, create visualizations, and ask questions about their dataset using natural language.

## 🚀 Project Overview

AI Data Analyst is a Streamlit-based web application designed to simplify the data analysis process.

Instead of manually writing Python or SQL queries for every analysis, users can upload a CSV or Excel dataset and interact with the data through an easy-to-use interface.

The application automatically analyzes the uploaded dataset, identifies data types, performs data cleaning, provides dataset statistics, generates visualizations, and allows users to ask questions in natural language.

The goal of this project is to make exploratory data analysis more accessible and reduce the amount of manual work required to understand a dataset.

## ✨ Key Features

### 1. Dataset Upload

Users can upload datasets in supported formats such as:

- CSV
- Excel (.xlsx)

After uploading a dataset, the application loads the data and displays its basic information.

### 2. Automatic Data Understanding

The application automatically examines the dataset and identifies:

- Number of rows
- Number of columns
- Column names
- Data types
- Numerical columns
- Categorical columns
- Date columns
- Missing values
- Duplicate records

This helps the user understand the structure of the dataset quickly.

### 3. Automatic Data Cleaning

The application performs data-cleaning operations based on the characteristics of the uploaded dataset.

Examples include:

- Handling missing values
- Removing duplicate records
- Detecting numerical columns
- Detecting categorical/string columns
- Detecting date columns
- Converting numeric values stored as text
- Cleaning currency symbols and unnecessary characters
- Handling inconsistent data formats
- Converting columns to appropriate data types where possible

For example, a value such as:

`$68.84`

can be recognized as a numerical value instead of being treated as a normal string.

Similarly, numeric values stored with commas, currency symbols, or other formatting can be processed before analysis.

### 4. Dataset Summary

The application provides an overview of the uploaded dataset including:

- Total records
- Total columns
- Missing values
- Duplicate records
- Data types
- Numerical and categorical features

### 5. Data Exploration

Users can explore the uploaded dataset through tables and statistical summaries.

For numerical columns, the application can provide useful statistics such as:

- Mean
- Median
- Minimum
- Maximum
- Standard deviation
- Count

### 6. Data Visualization

The application can generate visualizations based on the available columns and the user's analysis requirements.

Possible visualizations include:

- Bar charts
- Line charts
- Histograms
- Scatter plots
- Pie charts
- Distribution charts
- Category-wise comparisons

The application attempts to select suitable columns for visualization based on their data types.

### 7. Natural Language Data Questions

Users can ask questions about their dataset using normal language.

For example:

- How many rows are in this dataset?
- What is the average sales?
- Which city has the highest revenue?
- Show me the total revenue by city.
- Which product is sold the most?
- What is the maximum value of sales?
- Show the monthly trend.
- Which category has the highest quantity?

The application converts supported questions into an analysis plan and executes the corresponding query on the dataset.

### 8. SQL-Based Analysis

For supported analytical questions, the application generates SQL queries to perform operations such as:

- COUNT
- SUM
- AVG
- MIN
- MAX
- GROUP BY
- Filtering
- Sorting
- Aggregation

The generated SQL is displayed to the user for transparency.

### 9. Analysis Plan

Before executing a supported question, the application shows an analysis plan describing:

- Operation
- Grouping column
- Metric
- Aggregation
- Filters
- Sorting
- Limit

This helps users understand how their question is being interpreted.

### 10. Query Results

After analysis, the application displays the result in an easy-to-read table.

This allows users to directly understand the answer without manually writing queries.

### 11. Question History

The application keeps track of previously asked questions during the current session.

Users can review:

- Previous questions
- Generated answers

This makes it easier to continue the analysis workflow.

## 🧠 How It Works

The general workflow of the application is:

```text
Upload Dataset
      ↓
Read Dataset
      ↓
Understand Data Structure
      ↓
Detect Data Types
      ↓
Clean Data
      ↓
Generate Dataset Summary
      ↓
User Asks a Question
      ↓
Interpret the Question
      ↓
Generate Analysis Plan
      ↓
Generate SQL / Analysis Operation
      ↓
Execute Analysis
      ↓
Display Result


---

## 🛠️ Technical Stack

### Programming Language
- Python

### Frontend / Application Framework
- Streamlit

### Data Processing
- Pandas
- NumPy

### Data Visualization
- Plotly
- Matplotlib

### Database / Query Engine
- SQLite

### AI Integration
- Groq API
- Natural Language Question Understanding
- AI-generated SQL Analysis

### Configuration & Security
- python-dotenv
- Environment Variables
- `.env` file for API credentials

### File Formats Supported
- CSV
- XLSX / Excel

### Development Tools
- Visual Studio Code
- Git
- GitHub


---

## 📁 Project Structure

```text
AI-Data-Analyst/
│
├── app/
│   └── app.py
│
├── .streamlit/
│   └── config.toml
│
├── .env
│
├── .gitignore
│
└── README.md

<img width="653" height="345" alt="image" src="https://github.com/user-attachments/assets/9447541f-0d68-4511-9ce3-ac9dd0c0cb4a" />



###  ⚙️ Installation & Run

1. Clone the repository.

2. Install the required libraries:

```bash
pip install -r requirements.txt

## Run the application:
streamlit run app/app.py


## 👨‍💻 Author

Md Noorain Wakil

B.Tech CSE (Data Science)
