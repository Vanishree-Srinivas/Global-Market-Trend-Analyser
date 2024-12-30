import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sqlalchemy.sql import text
from backend.database import engine  # Ensure this points to the correct engine setup

# Metadata and Table Setup
metadata = MetaData()

# Define the salary_data table schema
salary_data_table = Table(
    'salary_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('rating', Float),
    Column('company_name', String),
    Column('job_title', String),
    Column('salary', Float),
    Column('salaries_reported', Integer),
    Column('location', String),
    Column('employment_status', String),
    Column('job_roles', String)
)

# Create the table in the database
metadata.create_all(engine)

# Session setup
Session = sessionmaker(bind=engine)
session = Session()

# Function to Load Dataset to Database
def load_salary_dataset(file_path):
    """
    Loads the salary dataset from a CSV file into the database.
    :param file_path: Path to the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        df.to_sql('salary_data', engine, if_exists='replace', index=False)
        print("Dataset loaded successfully!")
    except Exception as e:
        print(f"Error loading dataset: {e}")

# Function to Search Salary Data
def search_salary_data(column, value):
    """
    Searches the salary_data table based on a column and value.
    :param column: Column name to search.
    :param value: Value to search for.
    :return: DataFrame containing the search results.
    """
    with engine.connect() as conn:
        query = text(f"SELECT * FROM salary_data WHERE {column} LIKE :value")
        result = conn.execute(query, {"value": f"%{value}%"})
        return pd.DataFrame(result.fetchall(), columns=result.keys())

# Function for Comparative Analysis
def compare_salary_data(column, group_by):
    """
    Performs comparative analysis on the salary_data table.
    :param column: Column to analyze.
    :param group_by: Column to group by.
    :return: DataFrame containing comparative analysis results.
    """
    with engine.connect() as conn:
        query = text(f"SELECT {group_by}, AVG({column}) AS avg_salary FROM salary_data GROUP BY {group_by}")
        result = conn.execute(query)
        return pd.DataFrame(result.fetchall(), columns=result.keys())

# Function for Predictive Insights
def predict_salary(features):
    """
    Predict salary based on selected features using linear regression.
    """
    try:
        # Load data from the database
        df = pd.read_sql_table('salary_data', engine)
        
        # Check if the features exist in the dataset
        if not set(features).issubset(df.columns):
            raise ValueError("Invalid features provided for prediction.")

        # Drop rows with missing values in the selected features and the target
        df = df.dropna(subset=features + ['salary'])

        # Prepare the data for prediction
        X = df[features]
        y = df['salary']

        # Convert categorical features to numeric using one-hot encoding if needed
        X = pd.get_dummies(X, drop_first=True)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions
        predictions = model.predict(X_test)

        # Calculate mean squared error (MSE) for evaluation
        mse = mean_squared_error(y_test, predictions)

        # Return predictions and MSE
        return predictions, mse

    except Exception as e:
        raise ValueError(f"Error in predictive analysis: {e}")

