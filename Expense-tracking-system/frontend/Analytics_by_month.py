import pandas as pd
import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

def analytics_by_month_tab():
    st.title("Analytics by month")

    #Fetch all years with data to populate the selectable
    try:
        years_response = requests.get(f"{API_URL}/analytics/years")
        if years_response.status_code == 200:
            years_data = years_response.json()
            years = [y['year'] for y in years_data]

            #use the current year as the default selection if it exists, otherwise use the first year.
            current_year = datetime.now().year
            if str(current_year) in years:
                default_year_index = years.index(str(current_year))
            else:
                default_year_index = 0

            #create a selectbox for the user to choose a year
            selected_year = st.selectbox("Select Year", years, index=default_year_index)

            #make the api call with the selected years as a query parameter
            response = requests.get(f"{API_URL}/analytics/month?year={selected_year}")

            if response.status_code == 200:
                response_json = response.json()
                if not response_json:
                    st.info("No data available for this year {selected_year}")
                    return

                df = pd.DataFrame(response_json)

                #sort the dataframe by a new column that's good for sorting
                df['sort_key'] = pd.to_datetime(df['month'], format='%B-%Y')
                df = df.sort_values(by='sort_key', ascending=True)

                #prepare the dataframe for plotting
                df['total_amount'] = df['total_amount'].astype(float)
                df_for_chart = df.set_index('month')

                st.bar_chart(data=df_for_chart['total_amount'], use_container_width=True)

                #format the table display
                df['total_amount'] = df['total_amount'].map("{:,.2f}".format)
                st.table(df[['month','total_amount']])

            else:
                st.error(f"Error fetching data for year {selected_year} : {response.status_code} - {response.text}")

        else:
            st.error(f"Error fetching available years: {years_response.status_code} - {years_response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Connection error.Please ensure your FastAPI server is running.")

