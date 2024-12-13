import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import threading
import time

# PostgreSQL connection details
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'Archana02@'
DB_HOST = 'localhost'
DB_PORT = '5432'
TABLE_NAME = 'books'

# Connect to PostgreSQL
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to PostgreSQL: {e}")
        return None

# Fetch and transform data from PostgreSQL
def fetch_and_transform_data():
    conn = connect_to_postgres()
    if conn:
        try:
            query = f"SELECT * FROM {TABLE_NAME};"
            df = pd.read_sql_query(query, conn)
            conn.close()

            # Data Transformation
            df['Price'] = pd.to_numeric(df['price'], errors='coerce')  # Convert price to numeric
            df['Rating'] = df['rating'].str.extract(r'(\d+\.\d+|\d+)').astype(float)  # Extract numeric rating
            df['Reviews_Count'] = pd.to_numeric(df['reviews_count'], errors='coerce')  # Convert reviews count to numeric
            df['Format'] = df['format'].str.title()  # Normalize format strings
            return df
        except Exception as e:
            st.error(f"Error fetching or transforming data: {e}")
            return None

# Perform analysis on the data
def analyze_data(df):
    # Basic statistics
    avg_price = df['Price'].mean()
    avg_rating = df['Rating'].mean()
    total_reviews = df['Reviews_Count'].sum()
    most_common_format = df['Format'].value_counts().idxmax()

    return {
        "Average Price": round(avg_price, 2),
        "Average Rating": round(avg_rating, 2),
        "Total Reviews": int(total_reviews),
        "Most Common Format": most_common_format
    }

# Plot Price Distribution
def plot_price_distribution(df):
    st.subheader("Price Distribution")
    df = df.dropna(subset=['Price'])  # Remove rows with NaN prices

    fig, ax = plt.subplots()
    df['Price'].plot(kind='hist', bins=20, color='blue', alpha=0.7, ax=ax)
    ax.set_title("Price Distribution")
    ax.set_xlabel("Price ($)")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

# Plot Rating Distribution
def plot_rating_distribution(df):
    st.subheader("Rating Distribution")
    df = df.dropna(subset=['Rating'])  # Remove rows with NaN ratings

    fig, ax = plt.subplots()
    df['Rating'].plot(kind='hist', bins=10, color='green', alpha=0.7, ax=ax)
    ax.set_title("Rating Distribution")
    ax.set_xlabel("Rating (Stars)")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

# Plot Reviews Count by Format
def plot_reviews_by_format(df):
    st.subheader("Reviews by Format")
    reviews_by_format = df.groupby('Format')['Reviews_Count'].sum()

    fig, ax = plt.subplots()
    reviews_by_format.plot(kind='bar', color='orange', alpha=0.7, ax=ax)
    ax.set_title("Reviews Count by Format")
    ax.set_xlabel("Format")
    ax.set_ylabel("Total Reviews")
    st.pyplot(fig)

# Scheduled fetch and save operation
def fetch_and_save():
    print("Fetching book data from PostgreSQL...")
    conn = connect_to_postgres()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME};")
            conn.close()
            print("Data fetched successfully.")
        except Exception as e:
            print(f"Error fetching data: {e}")

# Schedule to fetch every 15 minutes
def schedule_fetch_and_save():
    while True:
        fetch_and_save()
        print("Waiting for 15 minutes before the next fetch...")
        time.sleep(900)  # 15 minutes

# Streamlit App
def main():
    st.title("Amazon Books Analysis")
    st.sidebar.title("Menu")

    menu = st.sidebar.radio("Options", ["View Data", "Analyze Data"])

    if menu == "View Data":
        st.subheader("View Data from PostgreSQL")
        df = fetch_and_transform_data()
        if df is not None:
            st.write(f"### Data from `{TABLE_NAME}` table:")
            st.dataframe(df)

    elif menu == "Analyze Data":
        st.subheader("Data Analysis")
        df = fetch_and_transform_data()
        if df is not None:
            analysis_results = analyze_data(df)
            st.write("### Analysis Results:")
            for key, value in analysis_results.items():
                st.write(f"**{key}:** {value}")

            st.write("### Visualizations:")
            plot_price_distribution(df)
            plot_rating_distribution(df)
            plot_reviews_by_format(df)

if __name__ == "__main__":
    threading.Thread(target=schedule_fetch_and_save, daemon=True).start()
    main()
