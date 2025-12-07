import streamlit as st
import pandas as pd

st.title("JUPAS Game Theory: Fair Seat Allocation and Payoff Analysis")

# --- Input Section ---
st.header("Input Parameters")

N = st.number_input("Total number of students (N)", min_value=1, value=1000)
num_group_A = st.number_input("Number of Group A students", min_value=0, max_value=N, value=300)
num_group_B = N - num_group_A

seats_type_A = st.number_input("Seats in Type A", min_value=0, value=270)
seats_type_B = st.number_input("Seats in Type B", min_value=0, value=360)
seats_type_C = st.number_input("Seats in Type C", min_value=0, value=270)

# --- Preference Section ---
st.header("Preference and Payoff Matrix")

st.markdown("#### Set the value (payoff) for each group-programme combination:")

payoff_A_A = st.number_input("Group A value for Type A", value=3)
payoff_A_B = st.number_input("Group A value for Type B", value=2)
payoff_A_C = st.number_input("Group A value for Type C", value=1)
payoff_B_A = st.number_input("Group B value for Type A", value=1)
payoff_B_B = st.number_input("Group B value for Type B", value=3)
payoff_B_C = st.number_input("Group B value for Type C", value=2)

payoff_matrix = {
    'A': {'Type A': payoff_A_A, 'Type B': payoff_A_B, 'Type C': payoff_A_C},
    'B': {'Type A': payoff_B_A, 'Type B': payoff_B_B, 'Type C': payoff_B_C}
}

# --- Allocation Algorithm ---
group_A_pref = sorted(payoff_matrix['A'], key=payoff_matrix['A'].get, reverse=True)
group_B_pref = sorted(payoff_matrix['B'], key=payoff_matrix['B'].get, reverse=True)

seats = {'Type A': seats_type_A, 'Type B': seats_type_B, 'Type C': seats_type_C}
allocation = {
    'A': {'Type A': 0, 'Type B': 0, 'Type C': 0},
    'B': {'Type A': 0, 'Type B': 0, 'Type C': 0}
}

# Allocate for Group A first
remaining_A = num_group_A
for prog in group_A_pref:
    alloc = min(remaining_A, seats[prog])
    allocation['A'][prog] = alloc
    seats[prog] -= alloc
    remaining_A -= alloc

# Then allocate for Group B
remaining_B = num_group_B
for prog in group_B_pref:
    alloc = min(remaining_B, seats[prog])
    allocation['B'][prog] = alloc
    seats[prog] -= alloc
    remaining_B -= alloc

# --- Output Section ---
st.header("Result Analysis")

# 1. Absolute Programme Value (number of students in each programme by group)
st.subheader("Absolute Programme Allocation")
df_alloc = pd.DataFrame(allocation).T
st.dataframe(df_alloc)

# 2. Payoff Analysis
st.subheader("Payoff Analysis (using current values)")

payoff_A = sum(allocation['A'][prog] * payoff_matrix['A'][prog] for prog in allocation['A'])
payoff_B = sum(allocation['B'][prog] * payoff_matrix['B'][prog] for prog in allocation['B'])
total_payoff = payoff_A + payoff_B

st.write(f"**Group A total payoff:** {payoff_A}")
st.write(f"**Group B total payoff:** {payoff_B}")
st.write(f"**Total system payoff:** {total_payoff}")

# 3. Mixed Strategy Equilibrium (MSE) Analysis
st.subheader("Mixed Strategy Equilibrium (MSE) Analysis")

# Calculate frequencies (probabilities) for each group
freq_A = {prog: allocation['A'][prog] / num_group_A if num_group_A > 0 else 0 for prog in allocation['A']}
freq_B = {prog: allocation['B'][prog] / num_group_B if num_group_B > 0 else 0 for prog in allocation['B']}

st.markdown("**Group A frequency of allocation:**")
st.write(pd.DataFrame([freq_A], index=["Frequency"]))

st.markdown("**Group B frequency of allocation:**")
st.write(pd.DataFrame([freq_B], index=["Frequency"]))

st.markdown("""
- The frequency for each programme is the proportion of students in that group allocated to that programme.
- The sum of frequencies for each group may be less than 1 if not all students are allocated a seat.
""")

st.markdown("---")
st.markdown("You can change the payoff values above to see how the analysis changes.")
