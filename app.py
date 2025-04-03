import os

import pandas as pd
import requests
import streamlit as st
from streamlit_option_menu import option_menu

API_BASE_URL = os.environ["API_BASE_URL"]

st.set_page_config(layout="wide")
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Best Bets", "Profit"],
        menu_icon="cast",
        default_index=0,
    )
st.title("NBA Betting Engine")

if selected == "Home":
    st.title("🏠 Home Page")
    st.write("Welcome to the Home Page of the Player Betting App!")


elif selected == "Best Bets":
    st.title("Best Bets Page")
    st.write("Select button below to see today's best player bets.")

    daily_bank = st.text_input("Enter the daily bet amount you want to play")
    st.write("The current daily bet amount is:", daily_bank)

    if st.button("Get Best Bets"):
        st.width = 900
        with st.spinner("Fetching bets from API..."):
            try:
                response = requests.get(f"{API_BASE_URL}/best_bets")
                if response.status_code == 200:
                    best_bets = response.json()
                    # Add 'Select' column to each bet
                    for bet in best_bets:
                        bet["Select"] = False
                    st.session_state["bets"] = best_bets
                    st.success("Fetched best bets successfully!")
                else:
                    st.error(f"Failed to fetch bets: {response.status_code}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Show the editable table with checkboxes
    if "bets" in st.session_state and st.session_state["bets"]:
        st.subheader("Top Player Bets Based on Expected Values")

        bets_df = pd.DataFrame(st.session_state["bets"])

        # Use st.data_editor for inline checkboxes!
        edited_bets_df = st.data_editor(
            bets_df,
            column_config={"Select": st.column_config.CheckboxColumn(required=False)},
            hide_index=True,
            use_container_width=True,
        )

        # Show filtered bets by EV in a table
        selected_bets_df = edited_bets_df[edited_bets_df["Select"]]
        if not selected_bets_df.empty:
            # Table of bets selected via Checkbox from EV table above
            st.subheader("Bets Selected for Submission")
            st.dataframe(selected_bets_df, use_container_width=True)

            if st.button("Submit Bets"):
                select = pd.DataFrame(selected_bets_df)

                # Convert DataFrame to JSON to send in request
                bets_json = select.to_dict(
                    orient="records"
                )  # ✅ This creates a list of dicts

                payload = {"bets": bets_json, "daily_bankroll": daily_bank}

                response = requests.post(f"{API_BASE_URL}/player_bets", json=payload)

                if response.status_code == 200:
                    st.success("✅ Bets submitted successfully!")
                    st.json(response.json())
                else:
                    st.error(
                        f"Failed to submit bets: {response.status_code} - {response.text}"
                    )


elif selected == "Profit":
    st.title("Profit Page")
    st.write("Select button below to see total profit metrics.")

    if st.button("Get Profit Metrics"):
        try:
            response = requests.get(f"{API_BASE_URL}/profit")
            if response.status_code == 200:
                st.session_state = response.json()

                st.success("Fetched profit successfully!")
            else:
                st.error(f"Failed to fetch profit: {response.status_code}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

        cols = st.columns(5)
        cols[0].metric(label="Total bet", value=round(st.session_state["total_bet"], 2))
        cols[1].metric(label="Total Profit", value=round(st.session_state["profit"], 2))
        cols[2].metric(label="Total Number of Bets", value=st.session_state["num_bets"])
        cols[3].metric(
            label="Strikerate", value=round(st.session_state["strike_rate"], 2)
        )
        cols[4].metric(label="ROI", value=round(st.session_state["roi"], 2))

    if st.button("Get Daily Profit Over Time"):
        try:
            response = requests.get(f"{API_BASE_URL}/daily_profit")
            if response.status_code == 200:
                st.session_state = response.json()

                st.success("Fetched profit successfully!")
            else:
                st.error(f"Failed to fetch profit: {response.status_code}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

        df = pd.DataFrame.from_dict(st.session_state)
        df["Date"] = pd.to_datetime(df["Date"])

        df.set_index("Date", inplace=True)
        df_daily = df.resample("D").sum()
        df_daily.index = df_daily.index.strftime("%Y-%m-%d")

        st.title("Daily Profit Over Time")
        st.write(df_daily)
        st.line_chart(df_daily)

    if st.button("Get Cumulative Profit Over Time"):
        try:
            response = requests.get(f"{API_BASE_URL}/cumulative_profit")
            if response.status_code == 200:
                st.session_state = response.json()

                st.success("Fetched cumulative profit successfully!")
            else:
                st.error(f"Failed to fetch profit: {response.status_code}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

        df = pd.DataFrame.from_dict(st.session_state)
        df["Date"] = pd.to_datetime(df["Date"])

        df.set_index("Date", inplace=True)
        df_daily = df.resample("D").sum()
        df_daily.index = df_daily.index.strftime("%Y-%m-%d")

        st.title("Cumulative Profit Over Time")

        st.line_chart(df_daily[["Cumulative Profit"]])
        st.write(df_daily[["Cumulative Profit"]])
