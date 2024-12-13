import requests
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
import time
from random import randint
import threading

# Headers to mimic browser behavior
HEADERS = {
    "Referer": 'https://www.amazon.com/',
    "Sec-Ch-Ua": "Not_A Brand",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

BASE_URL = "https://www.amazon.com/s?k=data+engineering+books"


def get_amazon_data_books(num_books):
    """
    Extracts book data from Amazon search results for data engineering books.

    Args:
        num_books (int): Number of books to fetch.

    Returns:
        pd.DataFrame: A DataFrame containing book details like title, author, price, rating, reviews count, and format.
    """
    books = []
    seen_titles = set()
    page = 1

    while len(books) < num_books and page <= 3:  # Limit to 3 pages
        url = f"{BASE_URL}&page={page}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        book_containers = soup.find_all("div", {"class": "s-result-item"})

        print(f"Page {page}: Found {len(book_containers)} containers.")

        for book in book_containers:
            try:
                title = book.find("span", {"class": "a-text-normal"})
                author = book.find("a", {"class": "a-size-base"})
                price = book.find("span", {"class": "a-price-whole"})
                rating = book.find("span", {"class": "a-icon-alt"})
                reviews = book.find("span", {"class": "a-size-base"})
                format_tag = book.find("span", {"class": "a-size-base a-color-secondary"})

                if title and author and (price or format_tag) and rating:
                    book_title = title.text.strip()
                    if book_title not in seen_titles:
                        seen_titles.add(book_title)
                        books.append({
                            "Title": book_title,
                            "Author": author.text.strip() if author else "Unknown",
                            "Price": price.text.strip() if price else "N/A",
                            "Rating": rating.text.strip() if rating else "N/A",
                            "Reviews_Count": reviews.text.strip() if reviews else "0",
                            "Format": format_tag.text.strip() if format_tag else "Unknown",
                        })
            except Exception as e:
                print(f"Error parsing a book entry: {e}")

        if not book_containers:
            print("No more results found.")
            break

        page += 1
        time.sleep(randint(1, 3))  # Random delay to mimic human behavior

    df = pd.DataFrame(books).drop_duplicates(subset="Title")
    return df


def save_data_to_postgres(df, table_name):
    """
    Saves a DataFrame to a PostgreSQL database. Recreates the table and its data.
    """
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Archana02@',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()

        # Drop the table if it exists
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        print(f"Table '{table_name}' dropped successfully.")

        # Create the table
        cursor.execute(f"""
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            authors TEXT,
            price TEXT,
            rating TEXT,
            reviews_count TEXT,
            format TEXT
        );
        """)
        conn.commit()
        print(f"Table '{table_name}' created successfully.")

        # Insert data into the table
        if df.empty:
            print("No data to insert into the database.")
            return

        print("Preview of data to be inserted:")
        print(df.head())

        insert_query = f"""
        INSERT INTO {table_name} (title, authors, price, rating, reviews_count, format)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        for _, row in df.iterrows():
            print(f"Inserting row: {row['Title']}")
            cursor.execute(insert_query, (row['Title'], row['Author'], row['Price'], row['Rating'], row['Reviews_Count'], row['Format']))
        
        conn.commit()
        print(f"Data successfully replaced in the '{table_name}' table.")

        # Close the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error saving data to PostgreSQL: {e}")


def fetch_and_save():
    """
    Fetch data from Amazon and save it to PostgreSQL.
    """
    print("Fetching book data from Amazon...")
    book_data_df = get_amazon_data_books(100)

    if not book_data_df.empty:
        save_data_to_postgres(book_data_df, "books")


def schedule_fetch_and_save():
    """
    Schedule the fetch and save operation to run every 10 minutes.
    """
    while True:
        fetch_and_save()
        print("Waiting for the next schedule...")
        time.sleep(600)  # 10 minutes


if __name__ == "__main__":
    # Start fetching and saving immediately and then every 10 minutes
    threading.Thread(target=schedule_fetch_and_save).start()
