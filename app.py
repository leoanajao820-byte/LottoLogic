import streamlit as st
import pandas as pd
import random
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="LottoLogic Pro", layout="wide")
st.title("LottoLogic: Professional Edition")

# --- 2. DATABASE MANAGEMENT ---
CSV_FILE = 'lotto_data.csv'

# Ensure the CSV exists with correct headers
if not os.path.exists(CSV_FILE):
    df_empty = pd.DataFrame(columns=['Date', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6'])
    df_empty.to_csv(CSV_FILE, index=False)

try:
    # Load the database
    df = pd.read_csv(CSV_FILE)

    # --- 3. SIDEBAR: DATA ENTRY & DUPLICATE CHECK ---
    with st.sidebar:
        st.header("Admin: Add New Result")
        st.write("Enter official winning numbers here.")
        
        with st.form("entry_form", clear_on_submit=True):
            new_date = st.date_input("Draw Date")
            n_input = st.text_input("Numbers (e.g., 1, 15, 22, 30, 35, 42)")
            submit = st.form_submit_button("Save to Database")
            
            if submit:
                try:
                    # Clean, sort, and validate numbers
                    num_list = sorted([int(x.strip()) for x in n_input.split(',')])
                    
                    # Prevent Duplicate Dates
                    if str(new_date) in df['Date'].values.astype(str):
                        st.error(f"Error: Data for {new_date} already exists!")
                    elif len(num_list) == 6 and all(1 <= x <= 42 for x in num_list):
                        new_row = [new_date] + num_list
                        df.loc[len(df)] = new_row
                        df.to_csv(CSV_FILE, index=False)
                        st.success("Result Saved!")
                        st.rerun()
                    else:
                        st.error("Enter 6 unique numbers between 1 and 42.")
                except:
                    st.error("Format error! Use commas to separate numbers.")

    # --- 4. MAIN DASHBOARD LAYOUT ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Frequency Analysis")
        if not df.empty:
            # Flatten numbers to count frequency
            all_numbers = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
            freq = pd.Series(all_numbers).value_counts().sort_index()
            st.bar_chart(freq)
            st.caption("Higher bars represent 'Hot' numbers in your current database.")
        else:
            st.info("Database is empty. Add results in the sidebar to begin analysis.")

    with col2:
        st.subheader("Smart Picker (Triple Filter)")
        
        # User-adjustable Sum Range (Golden Zone: 100-160)
        min_sum = st.slider("Min Sum", 80, 120, 100)
        max_sum = st.slider("Max Sum", 140, 180, 160)
        
        if st.button('Generate Optimized Pick'):
            attempts = 0
            while True:
                attempts += 1
                pick = sorted(random.sample(range(1, 43), 6))
                
                # Filter 1: Odd/Even (3-3 split)
                odds = [n for n in pick if n % 2 != 0]
                
                # Filter 2: High/Low (1-21 vs 22-42)
                lows = [n for n in pick if n <= 21]
                
                # Filter 3: Sum Range
                total_sum = sum(pick)
                
                # Check if all conditions are met
                if len(odds) == 3 and len(lows) == 3 and min_sum <= total_sum <= max_sum:
                    st.success(f"### Proposed Pick: {pick}")
                    st.write("**Strategy Report:**")
                    st.write(f"🔹 Sum: **{total_sum}**")
                    st.write(f"🔹 Mix: **3 Odd / 3 Even**")
                    st.write(f"🔹 Range: **3 Low / 3 High**")
                    st.caption(f"Filtered {attempts:,} combinations to find this match.")
                    break

    # --- 5. HISTORICAL LOG WITH SUM ANALYSIS ---
    st.divider()
    if st.checkbox('Show Raw Historical Log', value=True):
        # Create a display copy so we don't save the sum column to the actual CSV
        display_df = df.copy()
        
        if not display_df.empty:
            # Calculate Sum for the table
            display_df['Total Sum'] = display_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].sum(axis=1)
            
            # Sort by newest date
            display_df = display_df.sort_values(by='Date', ascending=False)
            
            st.dataframe(display_df, use_container_width=True)
            
            # Display average stats
            avg_sum = display_df['Total Sum'].mean()
            st.info(f"💡 The average sum of your recorded draws is **{avg_sum:.1f}**. Most winners fall between 100 and 160.")
        else:
            st.write("No data to display.")

except Exception as e:
    st.error(f"System Error: {e}")