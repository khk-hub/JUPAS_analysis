import streamlit as st
import pandas as pd

st.title("JUPAS Game Theory: MSE and Value Range Analysis")

# --- Input Section ---
st.header("Input Parameters")

num_group_A = st.number_input("Number of Group A students", min_value=0, value=3000)
num_group_B = st.number_input("Number of Group B students", min_value=0, value=7000)

seats_type_A = st.number_input("Seats in Type A", min_value=0, value=3000)
seats_type_B = st.number_input("Seats in Type B", min_value=0, value=4200)
seats_type_C = st.number_input("Seats in Type C", min_value=0, value=2800)

st.header("Programme Values (Payoff Matrix)")
payoff_A = st.number_input("Value of Type A Programme", value=3.0, format="%.3f")
payoff_B = st.number_input("Value of Type B Programme", value=2.0, format="%.3f")
payoff_C = st.number_input("Value of Type C Programme", value=1.0, format="%.3f")

# --- Step 1: Group A Case ---
st.subheader("Step 1: Group A Case")
if num_group_A <= seats_type_A:
    st.success(f"All {num_group_A} Group A students fill Type A seats.")
    group_A_allocation = {"Type A": num_group_A, "Type B": 0, "Type C": 0}
else:
    st.warning(f"Group A students ({num_group_A}) exceed Type A seats ({seats_type_A}). Only {seats_type_A} can be allocated to Type A.")
    group_A_allocation = {"Type A": seats_type_A, "Type B": 0, "Type C": 0}

st.write("Group A allocation:", group_A_allocation)

# --- Step 2: Group B Case ---
st.subheader("Step 2: Group B Case")

N_B = num_group_B
S_B = seats_type_B
S_C = seats_type_C
v_B = payoff_B
v_C = payoff_C

# Calculate MSE fraction
denom = v_B * S_B + v_C * S_C
x_star = v_B * S_B / denom if denom > 0 else 0

# Calculate admission probabilities at MSE
admission_prob_B = S_B / (x_star * N_B) if x_star * N_B > 0 else 0
admission_prob_C = S_C / ((1 - x_star) * N_B) if (1 - x_star) * N_B > 0 else 0

# Find value range for which both admission probabilities ≤ 1
# For Type B: S_B / (x_star * N_B) ≤ 1  =>  x_star ≥ S_B / N_B
# For Type C: S_C / ((1-x_star) * N_B) ≤ 1  =>  (1-x_star) ≥ S_C / N_B  =>  x_star ≤ 1 - S_C / N_B

lower_bound = S_B / N_B if N_B > 0 else 0
upper_bound = 1 - (S_C / N_B) if N_B > 0 else 1

# Now, x_star = v_B * S_B / (v_B * S_B + v_C * S_C)
# For MSE to be valid: lower_bound ≤ x_star ≤ upper_bound

st.write(f"**Calculated MSE fraction (Type B):** {x_star:.3f}")
st.write(f"**Admission probability for Type B at MSE:** {admission_prob_B:.3f}")
st.write(f"**Admission probability for Type C at MSE:** {admission_prob_C:.3f}")

st.write(f"**Value range for MSE to be valid:**")
st.latex(r"\text{lower bound} \leq x^* \leq \text{upper bound}")
st.write(f"Lower bound: {lower_bound:.3f}")
st.write(f"Upper bound: {upper_bound:.3f}")

if lower_bound < upper_bound:
    if lower_bound <= x_star <= upper_bound:
        st.success("MSE is valid for current values.")
        expected_payoff_B = v_B * admission_prob_B
        expected_payoff_C = v_C * admission_prob_C
        st.write(f"Fraction of Group B choosing Type B: {x_star:.3f}")
        st.write(f"Fraction of Group B choosing Type C: {1-x_star:.3f}")
        st.write(f"Expected payoff for Group B (Type B): {expected_payoff_B:.3f}")
        st.write(f"Expected payoff for Group B (Type C): {expected_payoff_C:.3f}")
        df_mse = pd.DataFrame({
            "Fraction": [x_star, 1-x_star],
            "Admission Probability": [admission_prob_B, admission_prob_C],
            "Expected Payoff": [expected_payoff_B, expected_payoff_C]
        }, index=["Type B", "Type C"])
        st.dataframe(df_mse)
    else:
        st.warning("MSE is NOT valid for current values.")
        st.write("Corner solution applies:")
        if x_star < lower_bound:
            st.info("All Group B students choose Type C.")
            admission_prob_C = S_C / N_B if N_B > 0 else 0
            expected_payoff_C = v_C * admission_prob_C
            st.write(f"Admission probability for Type C: {admission_prob_C:.3f}")
            st.write(f"Expected payoff for Group B: {expected_payoff_C:.3f}")
        elif x_star > upper_bound:
            st.info("All Group B students choose Type B.")
            admission_prob_B = S_B / N_B if N_B > 0 else 0
            expected_payoff_B = v_B * admission_prob_B
            st.write(f"Admission probability for Type B: {admission_prob_B:.3f}")
            st.write(f"Expected payoff for Group B: {expected_payoff_B:.3f}")
        st.write(f"To have MSE, adjust programme values so that {lower_bound:.3f} ≤ x* ≤ {upper_bound:.3f} (Type A > Type B > Type C).")
else:
    st.error("No valid value range for MSE (upper bound < lower bound). Check your seat and group numbers.")

st.markdown("---")
st.markdown("You can adjust the values and seat numbers to see how the equilibrium and value range change.")
