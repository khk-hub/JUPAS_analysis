import streamlit as st
import pandas as pd

st.title("JUPAS Game Theory: MSE Analysis for Heterogeneous Groups")

# --- Input Section ---
st.header("Input Parameters")

num_group_A = st.number_input("Number of Group A students", min_value=0, value=3000)
num_group_B = st.number_input("Number of Group B students", min_value=0, value=7000)

seats_type_A = st.number_input("Seats in Type A", min_value=0, value=3000)
seats_type_B = st.number_input("Seats in Type B", min_value=0, value=4200)
seats_type_C = st.number_input("Seats in Type C", min_value=0, value=2800)

# --- Programme Values (allow fractions) ---
st.header("Programme Values (Payoff Matrix)")
payoff_A = st.number_input("Value of Type A Programme", value=3.0, format="%.3f")
payoff_B = st.number_input("Value of Type B Programme", value=2.0, format="%.3f")
payoff_C = st.number_input("Value of Type C Programme", value=1.0, format="%.3f")

# --- Group A Allocation ---
st.header("Group A Allocation (Absolute)")
if num_group_A > seats_type_A:
    st.warning("Number of Group A students exceeds Type A seats. Only the first seats_type_A students will be allocated.")
group_A_alloc = min(num_group_A, seats_type_A)
st.write(f"Group A fills all Type A seats: {group_A_alloc} students.")

# --- Group B MSE Analysis ---
st.header("Group B Mixed Strategy Equilibrium (MSE) Analysis")

# Group B cannot access Type A
N_B = num_group_B
S_B = seats_type_B
S_C = seats_type_C
v_B = payoff_B
v_C = payoff_C

# MSE calculation
if N_B == 0:
    st.info("No Group B students.")
    x_star = 0
    expected_payoff_B = 0
    expected_payoff_C = 0
else:
    denom = v_B * S_B + v_C * S_C
    if denom == 0:
        x_star = 0
    else:
        x_star = v_B * S_B / denom

    # Clamp x_star to [0,1]
    if x_star > 1:
        x_star = 1.0
    elif x_star < 0:
        x_star = 0.0

    # Expected payoffs at equilibrium
    if x_star == 0:
        # All choose Type C
        admission_prob_C = S_C / N_B if N_B > 0 else 0
        expected_payoff_C = v_C * admission_prob_C
        expected_payoff_B = 0
    elif x_star == 1:
        # All choose Type B
        admission_prob_B = S_B / N_B if N_B > 0 else 0
        expected_payoff_B = v_B * admission_prob_B
        expected_payoff_C = 0
    else:
        admission_prob_B = S_B / (x_star * N_B) if x_star * N_B > 0 else 0
        admission_prob_C = S_C / ((1 - x_star) * N_B) if (1 - x_star) * N_B > 0 else 0
        expected_payoff_B = v_B * admission_prob_B
        expected_payoff_C = v_C * admission_prob_C

# Show results
st.markdown(f"**Fraction of Group B choosing Type B:** {x_star:.3f}")
st.markdown(f"**Fraction of Group B choosing Type C:** {1-x_star:.3f}")

if x_star == 1:
    st.info("All Group B students choose Type B (corner solution).")
elif x_star == 0:
    st.info("All Group B students choose Type C (corner solution).")
else:
    st.info("Group B students split between Type B and Type C (interior MSE).")

st.markdown(f"**Expected payoff for Group B (Type B):** {expected_payoff_B:.3f}")
st.markdown(f"**Expected payoff for Group B (Type C):** {expected_payoff_C:.3f}")

# Show frequencies in a table
df_mse = pd.DataFrame({
    "Fraction": [x_star, 1-x_star],
    "Expected Payoff": [expected_payoff_B, expected_payoff_C]
}, index=["Type B", "Type C"])
st.subheader("Group B MSE Table")
st.dataframe(df_mse)

st.markdown("""
- The above table shows the equilibrium frequencies (probabilities) with which Group B students choose each programme type, and their expected payoffs.
- The sum of fractions is 1 (all Group B students are allocated between Type B and C).
- If the value of Type B is much higher than Type C, all Group B students will choose Type B.
- If the value of Type B is close to Type C, some will choose Type C for a safer seat.
""")

st.markdown("---")
st.markdown("You can adjust the values and seat numbers to see how the equilibrium changes.")
