import seaborn as sns
import matplotlib.pyplot as plt

# --- 5. DATA LOG & DYNAMIC ANALYSIS ---
st.divider()
if not df.empty:
    st.header("📊 Advanced Probability Mapping")
    
    # --- HEAT MAP GENERATION ---
    if game_mode in ["3D Swertres", "4D Lotto"]:
        st.subheader("Positional Heat Map (Frequency)")
        
        # Calculate frequency of each digit (0-9) per position
        slots = [c for c in cols if c != 'Date']
        heat_data = pd.DataFrame(index=range(10), columns=slots)
        
        for slot in slots:
            counts = df[slot].value_counts()
            for i in range(10):
                heat_data.loc[i, slot] = counts.get(i, 0)
        
        # Plotting the Heat Map
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(heat_data.astype(int), annot=True, cmap="YlOrRd", fmt="d", ax=ax)
        ax.set_title(f"Digit Frequency per Position: {game_mode}")
        ax.set_xlabel("Slot Position")
        ax.set_ylabel("Digit (0-9)")
        st.pyplot(fig)
        st.caption("🔥 Red = Hot (Frequent) | ❄️ Yellow/White = Cold (Rare)")

    # --- TABLE LOG ---
    st.subheader("Historical Log")
    display_df = df.copy()
    if game_mode == "Lotto 6/42":
        display_df['Total Sum'] = display_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].sum(axis=1)
    
    st.dataframe(display_df.sort_values(by='Date', ascending=False), use_container_width=True)
