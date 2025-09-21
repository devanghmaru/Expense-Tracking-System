import pandas as pd
import streamlit as st
from datetime import datetime
import requests
from io import BytesIO

API_URL = "http://localhost:8000"


def analytics_tab():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))

    with col2:
        end_date = st.date_input("End Date", datetime(2024, 8, 2))

    if st.button("Get Analytics"):
        payload = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        }

        try:
            # Fetch analytics data
            response = requests.post(f"{API_URL}/analytics/", json=payload)

            if response.status_code == 200:
                analytics_data = response.json()

                # Process and display analytics
                data = {
                    "Category": list(analytics_data.keys()),
                    "Total": [analytics_data[category]['total_amount'] for category in analytics_data],
                    "Percentage": [analytics_data[category]['percentage'] for category in analytics_data],
                }
                df = pd.DataFrame(data)
                df_sort = df.sort_values(by=['Percentage'], ascending=False)

                st.title("Expense Breakdown by Category")
                st.bar_chart(data=df_sort.set_index('Category')['Percentage'])

                df_sort['Total'] = df_sort['Total'].map("{:,.2f}".format)
                df_sort['Percentage'] = df_sort['Percentage'].map("{:,.2f}".format)
                st.table(df_sort)

                # Fetch all entries to create the Excel file
                response_entries = requests.get(
                    f"{API_URL}/expenses/",json=payload)

                if response_entries.status_code == 200:
                    entries_data = response_entries.json()
                    df_entries = pd.DataFrame(entries_data)

                    # Create Excel file with two sheets
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_entries.to_excel(writer, sheet_name='Entries', index=False)
                        df_sort.to_excel(writer, sheet_name='Summary', index=False)
                    output.seek(0)

                    # Add download button
                    st.download_button(
                        label="Download Excel",
                        data=output,
                        file_name=f"expense_data_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error(f"Error fetching entries: {response_entries.status_code} - {response_entries.text}")

            else:
                st.error(f"Error fetching analytics: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("Connection failed. Please ensure your FastAPI server is running.")