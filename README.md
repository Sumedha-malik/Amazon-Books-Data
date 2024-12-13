# Project: Amazon Books Analysis

This project is designed to scrape data from Amazon about data engineering books, save the data in a PostgreSQL database, and analyze it using a Streamlit web application. It provides users with data insights, visualizations, and basic statistics about the books.

## Directory Overview

- **`app.py`**: The main Streamlit application for analyzing and visualizing the data stored in the PostgreSQL database.
- **`fetch.py`**: Script to scrape book data from Amazon and save it into the PostgreSQL database.
- **`docker-compose.yml`**: Configuration for running the project in Docker containers, including the Streamlit app and the PostgreSQL database.
- **`Dockerfile`**: Defines the setup for the Docker image to run the Streamlit app.
- **`requirements.txt`**: Lists all the Python dependencies required to run the project.
- **`supervisord.conf`**: Configuration file to manage multiple processes (e.g., the fetch script and the Streamlit app) within the Docker container.

---

## Code Explanations

### `app.py`
This file contains the Streamlit application for:
1. **Viewing the Data**:
   - Fetches data from the PostgreSQL database.
   - Displays the data in a tabular format.
2. **Analyzing the Data**:
   - Performs statistical analysis on metrics such as average price, average rating, and total reviews.
   - Provides visualizations like price distribution, rating distribution, and reviews count by book format.
3. **Background Fetching**:
   - Includes a scheduled operation to fetch and save updated data from Amazon every 15 minutes using threading.

### `fetch.py`
This script handles the process of scraping book data from Amazon and storing it into a PostgreSQL database.
- **Scraping**:
  - Fetches book data such as title, author, price, rating, reviews count, and format.
  - Uses BeautifulSoup for parsing Amazon's HTML pages.
- **Database Integration**:
  - Recreates the `books` table in the PostgreSQL database.
  - Inserts the scraped data into the database.
- **Execution**:
  - Runs the scraping operation immediately when executed.

### `docker-compose.yml`
Configures the Docker environment to:
1. Run a PostgreSQL container for the database.
2. Run the Streamlit application in a separate container.
3. Expose the application on port 8501 for access.

### `Dockerfile`
Defines the image used for running the Streamlit app, including:
- Installation of required dependencies.
- Setting up the application environment.

### `requirements.txt`
Contains all necessary Python libraries for the project:
- `streamlit`: For building the web application.
- `pandas`: For data manipulation and analysis.
- `psycopg2-binary`: For interacting with the PostgreSQL database.
- `matplotlib`: For creating visualizations.
- `beautifulsoup4`: For parsing HTML content.
- `requests`: For making HTTP requests.
- `schedule`: For periodic scheduling.
- `time`: Built-in library for timing operations.
- `threading`: Built-in library for managing background tasks.
- `random`: Built-in library for generating random values (used for delays).

### `supervisord.conf`
Manages multiple processes within a single Docker container:
- Runs both the `fetch.py` script and the Streamlit app simultaneously.
- Ensures both services restart automatically if they crash.

---

## How to Run the Project

### Prerequisites
1. Install Docker and Docker Compose on your system.
2. Ensure your machine meets the requirements for running Docker containers.

### Steps
1. Clone the repository.
2. Navigate to the project directory.
3. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```
4. Access the Streamlit application in your browser at `http://localhost:8501`.

---

## Features

1. **Scraping**:
   - Dynamically fetches book data from Amazon.
   - Extracts essential details like price, rating, and reviews.
2. **Database Storage**:
   - Stores the scraped data in a PostgreSQL database for persistence.
3. **Data Analysis**:
   - Computes average price, ratings, and reviews.
   - Identifies the most common book format.
4. **Visualizations**:
   - Displays distributions for price and ratings.
   - Provides insights into reviews by book format.
