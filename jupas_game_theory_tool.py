import streamlit as st
import pandas as pd

st.title("JUPAS Game Theory: Stepwise MSE Analysis")

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
    # Optionally, you can add logic for overflow to Type B/C if needed.

st.write("Group A allocation:", group_A_allocation)

# --- Step 2: Group B Case ---
st.subheader("Step 2: Group B Case")

# Remove Type A seats from available pool for Group B
available_B = seats_type_B
available_C = seats_type_C

if num_group_B <= available_B:
    st.success(f"All {num_group_B} Group B students fill Type B seats. No need for MSE.")
    group_B_allocation = {"Type B": num_group_B, "Type C": 0}
    st.write("Group B allocation:", group_B_allocation)
    st.write(f"Admission probability for Type B: {available_B/num_group_B:.3f}")
    st.write(f"Expected payoff for Group B: {payoff_B * available_B/num_group_B:.3f}")
else:
    st.info(f"Group B students ({num_group_B}) exceed Type B seats ({available_B}). MSE analysis needed.")
    # MSE calculation
    N_B = num_group_B
    S_B = available_B
    S_C = available_C
    v_B = payoff_B
    v_C = payoff_C

    denom = v_B * S_B + v_C * S_C
    x_star = v_B * S_B / denom if denom > 0 else 0

    # Clamp x_star to [0,1]
    if x_star > 1:
        x_star = 1.0
    elif x_star < 0:
        x_star = 0.0

    # Check if interior MSE is possible
    # For interior MSE, 0 < x_star < 1
    if 0 < x_star < 1:
        st.success("Interior MSE exists for Group B.")
        admission_prob_B = S_B / (x_star * N_B)
        admission_prob_C = S_C / ((1 - x_star) * N_B)
        expected_payoff_B = v_B * admission_prob_B
        expected_payoff_C = v_C * admission_prob_C

        st.write(f"Fraction of Group B choosing Type B: {x_star:.3f}")
        st.write(f"Fraction of Group B choosing Type C: {1-x_star:.3f}")
        st.write(f"Admission probability for Type B: {admission_prob_B:.3f}")
        st.write(f"Admission probability for Type C: {admission_prob_C:.3f}")
        st.write(f"Expected payoff for Group B (Type B): {expected_payoff_B:.3f}")
        st.write(f"Expected payoff for Group B (Type C): {expected_payoff_C:.3f}")

        df_mse = pd.DataFrame({
            "Fraction": [x_star, 1-x_star],
            "Admission Probability": [admission_prob_B, admission_prob_C],
            "Expected Payoff": [expected_payoff_B, expected_payoff_C]
        }, index=["Type B", "Type C"])
        st.dataframe(df_mse)
    else:
        # Corner solution: all choose B or all choose C
        if x_star >= 1:
            st.warning("Corner solution: All Group B students choose Type B.")
            admission_prob_B = S_B / N_B
            expected_payoff_B = v_B * admission_prob_B
            st.write(f"Admission probability for Type B: {admission_prob_B:.3f}")
            st.write(f"Expected payoff for Group B: {expected_payoff_B:.3f}")
            st.write("No Group B students choose Type C.")
        elif x_star <= 0:
            st.warning("Corner solution: All Group B students choose Type C.")
            admission_prob_C = S_C / N_B
            expected_payoff_C = v_C * admission_prob_C
            st.write(f"Admission probability for Type C: {admission_prob_C:.3f}")
            st.write(f"Expected payoff for Group B: {expected_payoff_C:.3f}")
            st.write("No Group B students choose Type B.")

        # Show the value range for which interior MSE is possible
        st.info("To have an interior MSE (0 < x < 1), the following must hold:")
        st.latex(r"0 < \frac{v_B S_B}{v_B S_B + v_C S_C} < 1")
        st.write("Which means:")
        st.write(f"- v_B > 0, v_C > 0, S_B > 0, S_C > 0")
        st.write(f"- Try adjusting the values of Type B and Type C to find a range where MSE exists (Type A > Type B > Type C).")

st.markdown("---")
st.markdown("You can adjust the values and seat numbers to see how the equilibrium changes.")
