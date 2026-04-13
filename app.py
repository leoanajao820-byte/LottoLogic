import streamlit as st
import pandas as pd
import random
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="LottoLogic Multi-Game", layout="wide")

# --- 2. NAVIGATION ---
with st.sidebar:
    st.title("Settings")
    game_mode = st.radio("Select Game Mode", ["Lotto 6/42", "3D Swertres", "4D Lotto"])
    st.divider()

# Set database filename based on game
if game_mode == "Lotto 6/42":
    CSV_FILE = 'lotto_data.csv'
    cols = ['Date', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6']
    max_num = 42
elif game_mode == "3D Swertres":
    CSV_FILE = '3d_data.csv'
    cols = ['Date', 'P1', 'P2', 'P3']
    max_num = 9
else:
    CSV_FILE = '4d_data.csv'
    cols = ['Date', 'P1', 'P2', 'P3', 'P4']
    max_num = 9

# Ensure the selected CSV exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=cols).to_csv(CSV_FILE, index=False)

df = pd.read_csv(CSV_FILE)

# --- 3. DATA ENTRY (SIDEBAR) ---
with st.sidebar:
    st.header(f"Add {game_mode} Result")
    with st.form("entry_form", clear_on_submit=True):
        new_date = st.date_input("Draw Date")
        n_input = st.text_input("Numbers (comma separated)")
        submit = st.form_submit_button("Save Result")
        
        if submit:
            try:
                num_list = [int(x.strip()) for x in n_input.split(',')]
                if len(num_list) == len(cols) - 1:
                    new_row = [new_date] + num_list
                    df.loc[len(df)] = new_row
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Saved!")
                    st.rerun()
                else:
                    st.error(f"Please enter exactly {len(cols)-1} numbers.")
            except:
                st.error("Invalid format.")

# --- 4. MAIN DASHBOARD ---
st.title(f"Analysis: {game_mode}")

if game_mode == "Lotto 6/42":
    # (Insert your existing 6/42 Logic here - Sum, Odd/Even filters)
    st.write("Use your existing Golden Zone strategy here.")
    # [Keep the 6/42 code block from your previous script here]

else:
    # 3D and 4D POSITIONAL ANALYSIS
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Positional Heatmap")
        if not df.empty:
            # Show which digits (0-9) are hot for each slot
            pos_data = df.drop(columns=['Date'])
            st.bar_chart(pos_data.apply(pd.Series.value_counts).fillna(0))
            st.caption("Each color represents a different position (Slot 1, Slot 2, etc.)")
        else:
            st.info("Add data to see positional patterns.")

    with col2:
        st.subheader("Quick Pick")
        if st.button('Generate 3D/4D Pick'):
            if game_mode == "3D Swertres":
                pick = [random.randint(0, 9) for _ in range(3)]
            else:
                pick = [random.randint(0, 9) for _ in range(4)]
            st.success(f"### Proposed: {' - '.join(map(str, pick))}")

# --- 5. LOG ---
st.divider()
st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
