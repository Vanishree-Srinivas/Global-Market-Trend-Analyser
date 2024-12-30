import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from backend.database import init_db, add_user, add_market_data
from backend.auth import validate_username, validate_password, authenticate_user

# Initialize Database
init_db()

# Purple Theme
st.markdown("<style>" + open('templates/purple_theme.css').read() + "</style>", unsafe_allow_html=True)

st.title("🌎 Global Market Trends Analyzer")
st.sidebar.title("Navigation")
navigation = st.sidebar.radio("Go to", ["Login", "Register", "Dashboard", "Trend Analyzer","Search & Comparative Analysis" , "Admin"])

# Registration
if navigation == "Register":
    st.header("Register")
    username = st.text_input("Username (Min 4 characters)")
    password = st.text_input("Password (Min 6 characters)", type="password")
    if st.button("Register"):
        if validate_username(username) and validate_password(password):
            try:
                add_user(username, password)
                st.success("User registered successfully!")
            except:
                st.error("Username already exists!")
        else:
            st.error("Invalid username or password")

# Login
elif navigation == "Login":
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.success(f"Welcome {username}!")
            st.session_state['user'] = username
        else:
            st.error("Invalid credentials")

# Dashboard
elif navigation == "Dashboard":
    if 'user' in st.session_state:
        st.header(f"Hello {st.session_state['user']}!")
        
        # Upload dataset
        uploaded_file = st.file_uploader("Upload your market data CSV", type=["csv"])
        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            st.dataframe(data)
        
            # Filter data based on Region
            region = st.selectbox("Select Region", data['Region'].unique())
            filtered_data = data[data['Region'] == region]
            st.subheader(f"Showing Data for Region: {region}")
            st.dataframe(filtered_data)

            # Visualizations
            st.subheader("Market Trends")
            option = st.selectbox("Choose Visualization", ["Line Chart", "Bar Chart", "Pie Chart", "Heatmap", "Scatter Plot"])

            if option == "Line Chart":
                fig = px.line(filtered_data, x='Date', y='Units Sold', title=f"Units Sold in {region}")
                st.plotly_chart(fig)

            elif option == "Bar Chart":
                fig = px.bar(filtered_data, x='Date', y='Units Sold', title=f"Units Sold in {region}")
                st.plotly_chart(fig)

            elif option == "Pie Chart":
                fig = px.pie(filtered_data, names='Category', values='Units Sold', title=f"Units Sold by Category in {region}")
                st.plotly_chart(fig)

            elif option == "Scatter Plot":
                fig = px.scatter(filtered_data, x='Units Sold', y='Price', color='Category', 
                                 title=f"Units Sold vs Price in {region}")
                st.plotly_chart(fig)
    else:
        st.error("Please log in to view the dashboard")

# Trend Analyzer
elif navigation == "Trend Analyzer":
    if 'user' in st.session_state:
        st.header(f"Market Trend Analyzer for {st.session_state['user']}")
        
        # Upload dataset for trend analysis
        uploaded_file = st.file_uploader("Upload your market trend data CSV", type=["csv"])
        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            st.dataframe(data)
            
            # Date Filtering
            st.subheader("Filter Data by Date Range")
            start_date = st.date_input("Start Date", value=pd.to_datetime(data['Date']).min())
            end_date = st.date_input("End Date", value=pd.to_datetime(data['Date']).max())
            filtered_data = data[(pd.to_datetime(data['Date']) >= pd.to_datetime(start_date)) & 
                                  (pd.to_datetime(data['Date']) <= pd.to_datetime(end_date))]
            st.dataframe(filtered_data)
            
            # Region Filter
            st.subheader("Filter Data by Region")
            regions = data['Region'].unique()
            selected_region = st.selectbox("Select Region", regions)
            region_data = filtered_data[filtered_data['Region'] == selected_region]
            st.dataframe(region_data)

            # Correlation matrix and predictions
            st.subheader("Market Trend Report")
            numeric_data = region_data.select_dtypes(include=['number', 'float64', 'int64'])
            if not numeric_data.empty:
                corr_matrix = numeric_data.corr()
                st.write("Correlation Matrix:")
                st.dataframe(corr_matrix)

                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                st.pyplot(fig)

                st.line_chart(region_data.set_index('Date')['Units Sold'])
            else:
                st.error("No numeric data available for analysis.")
    else:
        st.error("Please log in to analyze trends")

# Admin
elif navigation == "Admin":
    st.header("Admin Dashboard")
    st.write("Perform CRUD operations here")

# Search and Comparative Analysis Service
elif navigation == "Search & Comparative Analysis":
    st.header("Search and Comparative Analysis Service")
    
    # Upload Dataset
    uploaded_file = st.file_uploader("Upload Salary Dataset", type=["csv"])
    if uploaded_file:
        from backend.salary_analysis import load_salary_dataset
        load_salary_dataset(uploaded_file)
        st.success("Dataset loaded successfully!")
    
    # Search Functionality
    st.subheader("Search Salary Data")
    search_column = st.selectbox("Search by Column", ["company_name", "job_title", "location", "job_roles"])
    search_value = st.text_input("Enter search value")
    if st.button("Search"):
        from backend.salary_analysis import search_salary_data
        result = search_salary_data(search_column, search_value)
        st.dataframe(result)
    
    # Comparative Analysis
    st.subheader("Comparative Analysis")
    compare_column = st.selectbox("Compare by", ["salary", "rating"])
    group_by = st.selectbox("Group By", ["location", "job_title", "company_name"])
    if st.button("Compare"):
        from backend.salary_analysis import compare_salary_data
        result = compare_salary_data(compare_column, group_by)
        st.dataframe(result)
    
    # Predictive Insights
    st.subheader("Predictive Insights")
    feature_columns = st.multiselect("Select Features for Prediction", ["rating", "salaries_reported"])
    if st.button("Predict Salary"):
        from backend.salary_analysis import predict_salary
        try:
            predictions, mse = predict_salary(feature_columns)
            st.write(f"Mean Squared Error: {mse}")
            st.write("Predictions:", predictions)
        except ValueError as e:
            st.error(str(e))

elif navigation == "Search Salary Data":
    st.header("Search Salary Data")

    # Search by column and value
    search_column = st.selectbox("Search by Column", ["job_roles", "location", "company_name", "job_title"])
    search_value = st.text_input("Enter search value")

    if st.button("Search"):
        try:
            from backend.salary_analysis import search_salary_data
            result = search_salary_data(search_column, search_value)
            if not result.empty:
                st.write("Search Results:")
                st.dataframe(result)
            else:
                st.warning("No data found for your search.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
