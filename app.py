import streamlit as st
import pandas as pd
import random
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="LottoLogic Pro", layout="wide")

# --- 2. NAVIGATION & DATABASE LOGIC ---
with st.sidebar:
    st.title("🏆 LottoLogic Pro")
    game_mode = st.radio("Select Game Mode", ["Lotto 6/42", "3D Swertres", "4D Lotto"])
    
    # Range Slider for 6/42 (Golden Zone)
    if game_mode == "Lotto 6/42":
        st.divider()
        st.subheader("Picker Settings")
        sum_range = st.slider("Target Sum Range", 21, 237, (120, 140))
        st.caption("Standard 'Golden Zone' is 120-140.")
    
    st.divider()

# Set file and columns based on selection
if game_mode == "Lotto 6/42":
    CSV_FILE, cols = 'lotto_data.csv', ['Date', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6']
elif game_mode == "3D Swertres":
    CSV_FILE, cols = '3d_data.csv', ['Date', 'P1', 'P2', 'P3']
else:
    CSV_FILE, cols = '4d_data.csv', ['Date', 'P1', 'P2', 'P3', 'P4']

# Initialize files if they don't exist
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
                    st.success("Result Saved!")
                    st.rerun()
                else:
                    st.error(f"Please enter exactly {len(cols)-1} numbers.")
            except:
                st.error("Invalid format. Use numbers separated by commas.")

# --- 4. MAIN DASHBOARD ---
st.title(f"Analysis: {game_mode}")

# --- CASE A: LOTTO 6/42 (FREQUENCY + SMART PICKER) ---
if game_mode == "Lotto 6/42":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Frequency Chart")
        if not df.empty:
            all_nums = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
            st.bar_chart(pd.Series(all_nums).value_counts().sort_index())
        else:
            st.info("Input data to see frequency trends.")

    with col2:
        st.subheader("Smart Picker")
        st.write(f"Targeting: **{sum_range[0]}-{sum_range[1]} Sum**")
        if st.button('Generate 6/42 Pick'):
            attempts = 0
            while True:
                attempts += 1
                pick = sorted(random.sample(range(1, 43), 6))
                odd_count = len([n for n in pick if n % 2 != 0])
                low_count = len([n for n in pick if n <= 21])
                total_sum = sum(pick)
                
                if odd_count == 3 and low_count == 3 and sum_range[0] <= total_sum <= sum_range[1]:
                    st.success(f"### {pick}")
                    st.write(f"**Sum:** {total_sum} | **Mix:** 3 Odd/3 Even")
                    st.caption(f"Filtered {attempts:,} combinations to find this match.")
                    break

# --- CASE B: 3D & 4D (GAP ANALYSIS) ---
else:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Positional Gap Analysis")
        if not df.empty:
            slots = [c for c in cols if c != 'Date']
            gap_results = {}
            for slot in slots:
                last_seen = {}
                for digit in range(10):
                    idx = df.index[df[slot] == digit].tolist()
                    last_seen[digit] = (len(df) - 1 - max(idx)) if idx else "NEW"
                gap_results[slot] = last_seen
            st.table(pd.DataFrame(gap_results).T)
        else:
            st.info("No historical data found for Gaps.")

    with col2:
        st.subheader("Quick Pick")
        if st.button(f'Generate {game_mode}'):
            pick_count = 3 if game_mode == "3D Swertres" else 4
            pick = [random.randint(0, 9) for _ in range(pick_count)]
            st.success(f"### {' - '.join(map(str, pick))}")

# --- 5. HISTORICAL LOG WITH DYNAMIC SUM ---
st.divider()
if not df.empty:
    st.subheader("Historical Log")
    display_df = df.copy()
    
    # Calculate Sum and Average ONLY for 6/42 mode
    if game_mode == "Lotto 6/42":
        display_df['Total Sum'] = display_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].sum(axis=1)
        avg_sum = display_df['Total Sum'].mean()
        st.info(f"💡 The average sum of your recorded draws is **{avg_sum:.1f}**.")
    
    st.dataframe(display_df.sort_values(by='Date', ascending=False), use_container_width=True)
    
    # Backup Button
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Backup CSV", csv_data, f"{game_mode}_data.csv", "text/csv")
