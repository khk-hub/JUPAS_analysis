import streamlit as st

st.title("JUPAS Game Theory Payoff Analysis")

# Sidebar inputs
st.sidebar.header("Input Parameters")

N = st.sidebar.number_input("Total number of students (N)", min_value=1, value=1000)
S = st.sidebar.number_input("Total number of seats (S)", min_value=1, value=800)

prop_group_A = st.sidebar.slider("Proportion of Group A students", min_value=0.0, max_value=1.0, value=0.6)
prop_group_B = 1.0 - prop_group_A

prop_type_A = st.sidebar.slider("Proportion of Type A programme seats", min_value=0.0, max_value=1.0, value=0.5)
prop_type_B = st.sidebar.slider("Proportion of Type B programme seats", min_value=0.0, max_value=1.0, value=0.3)
prop_type_C = 1.0 - prop_type_A - prop_type_B

if prop_type_C < 0:
    st.error("Proportions of Type A and B seats must add up to less than or equal to 1.")
    st.stop()

num_group_A = int(N * prop_group_A)
num_group_B = N - num_group_A

seats_type_A = int(S * prop_type_A)
seats_type_B = int(S * prop_type_B)
seats_type_C = S - seats_type_A - seats_type_B

payoff_matrix = {
    'A': {'Type A': 3, 'Type B': 2, 'Type C': 1},
    'B': {'Type A': 1, 'Type B': 3, 'Type C': 2}
}

def allocate_seats(num_students, seats, payoff):
    allocation = {'Type A': 0, 'Type B': 0, 'Type C': 0}
    preferred_type = max(payoff, key=payoff.get)
    allocated = min(num_students, seats[preferred_type])
    allocation[preferred_type] = allocated
    remaining_students = num_students - allocated
    seats[preferred_type] -= allocated

    if remaining_students > 0:
        types_sorted = sorted(payoff, key=payoff.get, reverse=True)
        for t in types_sorted:
            if t == preferred_type:
                continue
            alloc = min(remaining_students, seats[t])
            allocation[t] += alloc
            seats[t] -= alloc
            remaining_students -= alloc
            if remaining_students == 0:
                break
    return allocation

seats = {'Type A': seats_type_A, 'Type B': seats_type_B, 'Type C': seats_type_C}

alloc_A = allocate_seats(num_group_A, seats.copy(), payoff_matrix['A'])
alloc_B = allocate_seats(num_group_B, seats.copy(), payoff_matrix['B'])

def total_payoff(allocation, payoff):
    return sum(allocation[t] * payoff[t] for t in allocation)

payoff_A = total_payoff(alloc_A, payoff_matrix['A'])
payoff_B = total_payoff(alloc_B, payoff_matrix['B'])

st.subheader("Results")

st.write(f"**Group A students:** {num_group_A}")
st.write(f"**Group B students:** {num_group_B}")
st.write(f"**Seats in Type A:** {seats_type_A}")
st.write(f"**Seats in Type B:** {seats_type_B}")
st.write(f"**Seats in Type C:** {seats_type_C}")

st.write("### Allocation")
st.write("**Group A allocation:**", alloc_A)
st.write("**Group B allocation:**", alloc_B)

st.write("### Payoffs")
st.write(f"**Group A total payoff:** {payoff_A}")
st.write(f"**Group B total payoff:** {payoff_B}")
st.write(f"**Total system payoff:** {payoff_A + payoff_B}")

st.write("---")
st.write("Adjust the sliders in the sidebar to explore different scenarios!")
