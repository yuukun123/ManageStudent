# ManageStudent - Student Score Management System

A desktop application built with Python and PyQt5, designed to assist lecturers in managing student information, tracking scores, and viewing academic statistics for their assigned classes.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## About The Project

This is a personal project developed to explore and apply GUI programming with Python. It simulates a compact tool for university lecturers, aiming to simplify student management and the grading process.

The project uses **PyQt5** for the user interface and **SQLite** for local data storage, ensuring portability and eliminating the need for complex database setups.

## Key Features

-   **✅ Secure Login:** Each lecturer has a dedicated account to access the system.
-   **👨‍🎓 Student List Management:**
    -   View lists of students from assigned classes.
    -   Search and sort students by name or ID.
-   **📝 Score Entry and Updates:**
    -   Easily enter or edit midterm, final, and overall scores (on a 10-point scale).
    -   The system automatically calculates the final grade based on subject weights.
-   **📊 Statistics and Data Visualization:**
    -   **Score Analysis:** View score distribution charts (histogram, box plot) for a class or subject.
    -   **Pass/Fail Ratio:** Automatically calculate and display pie charts showing the pass/fail rates for a specific class.
    -   **Cross-Class Comparison:** Analyze average scores to compare academic performance across different classes taught by the lecturer.
-   **🗂️ Flexible Data Filtering:** Filter students and view statistics by academic year and semester.

## Tech Stack

-   **Language:** Python 3.10
-   **GUI Framework:** PyQt5
-   **Database:** SQLite
-   **Tools:** Qt Designer, pyuic5, pyrcc5

## Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

-   [Python](https://www.python.org/downloads/) 3.10 or higher installed.
-   `pip` package manager (usually comes with Python).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ManageStudent.git
    ```
    *(Replace `your-username` with your actual GitHub username)*

2.  **Navigate to the project directory:**
    ```bash
    cd ManageStudent
    ```

3.  **Install the required dependencies:**
    Run the following command in your terminal to install all necessary packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application
Once the installation is complete, run the `main.py` script to start the application:
'''bash
python main.py

#### Alternatively, you can open the project in your favorite IDE (like VSCode or PyCharm) and run the main.py file directly.

# Acknowledgments
##### This project was developed with the assistance and guidance of Large Language Models, including OpenAI's ChatGPT and Google's Gemini.
```bash
