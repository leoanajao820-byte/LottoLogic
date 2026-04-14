import streamlit as st
import pandas as pd
import os
from datetime import datetime
import random

# --- 1. INITIAL SETUP ---
st.set_page_config(page_title="LottoLogic Pro", layout="wide")

# Sidebar for Game Selection
st.sidebar.title("🏆 LottoLogic Pro")
game_mode = st.sidebar.radio("Select Game Mode", ["Lotto 6/42", "3D Swertres", "4D Lotto"])

# Define filenames and columns based on mode
if game_mode == "Lotto 6/42":
    csv_file = "lotto_data.csv"
    cols = ["Date", "N1", "N2", "N3", "N4", "N5", "N6"]
elif game_mode == "3D Swertres":
    csv_file = "3d_data.csv"
    cols = ["Date", "P1", "P2", "P3"]
else:
    csv_file = "4d_data.csv"
    cols = ["Date", "P1", "P2", "P3", "P4"]

# --- 2. DATA LOAD ---
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=cols)
    df.to_csv(csv_file, index=False)
else:
    df = pd.read_csv(csv_file)

# --- 3. SIDEBAR: ADD NEW DATA ---
st.sidebar.divider()
st.sidebar.subheader(f"Add {game_mode} Result")
new_date = st.sidebar.date_input("Draw Date", datetime.now())
new_nums = st.sidebar.text_input("Numbers (comma separated)", placeholder="e.g. 4,1,9")

if st.sidebar.button("Save Result"):
    try:
        num_list = [int(n.strip()) for n in new_nums.split(",")]
        if len(num_list) == len(cols) - 1:
            new_row = [new_date.strftime("%Y-%m-%d")] + num_list
            new_df = pd.DataFrame([new_row], columns=cols)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(csv_file, index=False)
            st.sidebar.success("Result Saved!")
            st.rerun()
        else:
            st.sidebar.error(f"Please enter exactly {len(cols)-1} numbers.")
    except:
        st.sidebar.error("Invalid format. Use numbers and commas.")

# --- 4. MAIN INTERFACE ---
st.title(f"Analysis: {game_mode}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Positional Gap Analysis")
    if not df.empty and game_mode in ["3D Swertres", "4D Lotto"]:
        slots = [c for c in cols if c != 'Date']
        gap_results = []
        for digit in range(10):
            row = {"Digit": digit}
            for slot in slots:
                last_pos = df[df[slot] == digit].index
                if not last_pos.empty:
                    gap = len(df) - 1 - last_pos[-1]
                    row[slot] = gap
                else:
                    row[slot] = "NEW"
            gap_results.append(row)
        
        gap_df = pd.DataFrame(gap_results)
        
        def highlight_sweet_spot(val):
            if isinstance(val, int) and 8 <= val <= 12:
                return 'background-color: #2e7d32; color: white'
            return ''
        
        try:
            st.dataframe(gap_df.style.map(highlight_sweet_spot), use_container_width=True)
        except AttributeError:
            st.dataframe(gap_df.style.applymap(highlight_sweet_spot), use_container_width=True)
    else:
        st.info("No historical data found for Gaps. Add some results in the sidebar!")

with col2:
    st.subheader("Quick Pick")
    if st.button(f"Generate {game_mode}"):
        st.write("🎯 **Recommended Pick:**")
        if game_mode == "Lotto 6/42":
            pick = sorted(random.sample(range(1, 43), 6))
            st.code("-".join(map(str, pick)))
        else:
            pick = [str(random.randint(0, 9)) for _ in range(len(cols)-1)]
            st.code(" - ".join(pick))

# --- 5. HISTORICAL LOG ---
st.divider()
st.subheader("Historical Log")
st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
