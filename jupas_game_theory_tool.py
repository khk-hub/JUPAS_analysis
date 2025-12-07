import streamlit as st
import numpy as np

# Initialize session state for parameters
if 'params' not in st.session_state:
    st.session_state.params = {
        'N': 10000,
        'S': 9000,
        'group_A_prop': 0.3,
        'V_A': 3.0,
        'V_B': 2.0,
        'V_C': 1.0,
        'seat_prop_A': 1/3,
        'seat_prop_B': 1/3,
        'seat_prop_C': 1/3
    }

st.title("JUPAS Competition Analyzer")
st.markdown("Analyze game-theoretic equilibrium in JUPAS-style admissions")

# Sidebar for parameter inputs
with st.sidebar:
    st.header("Parameters")
    
    # Basic parameters
    N = st.number_input("Total Applicants (N)", min_value=1000, max_value=50000, 
                       value=st.session_state.params['N'], step=1000)
    S = st.number_input("Total Seats (S)", min_value=100, max_value=50000, 
                       value=st.session_state.params['S'], step=100)
    
    # Group proportion
    group_A_prop = st.slider("Group A Proportion (More Competitive)", 
                            min_value=0.1, max_value=0.5, 
                            value=float(st.session_state.params['group_A_prop']), 
                            step=0.05)
    
    # Programme values
    st.subheader("Programme Values")
    V_A = st.number_input("Value of Type A", min_value=1.0, max_value=10.0, 
                         value=float(st.session_state.params['V_A']), step=0.1)
    V_B = st.number_input("Value of Type B", min_value=0.1, max_value=10.0, 
                         value=float(st.session_state.params['V_B']), step=0.1)
    V_C = st.number_input("Value of Type C", min_value=0.1, max_value=10.0, 
                         value=float(st.session_state.params['V_C']), step=0.1)
    
    # Seat distribution
    st.subheader("Seat Distribution")
    seat_prop_A = st.slider("Proportion of seats in Type A", 
                           min_value=0.0, max_value=1.0, 
                           value=float(st.session_state.params['seat_prop_A']), step=0.05)
    seat_prop_B = st.slider("Proportion of seats in Type B", 
                           min_value=0.0, max_value=1.0, 
                           value=float(st.session_state.params['seat_prop_B']), step=0.05)
    seat_prop_C = 1.0 - seat_prop_A - seat_prop_B
    st.markdown(f"**Proportion of seats in Type C:** {seat_prop_C:.2f}")
    
    if seat_prop_C < 0:
        st.error("Seat proportions must sum to 1 or less!")
    
    # Update session state
    st.session_state.params.update({
        'N': N, 'S': S, 'group_A_prop': group_A_prop,
        'V_A': V_A, 'V_B': V_B, 'V_C': V_C,
        'seat_prop_A': seat_prop_A, 'seat_prop_B': seat_prop_B, 'seat_prop_C': seat_prop_C
    })

# Main analysis function
def analyze_jupas(N, S, group_A_prop, V_A, V_B, V_C, seat_prop_A, seat_prop_B, seat_prop_C):
    """Core analysis function following the paper's logic."""
    
    # Derived quantities
    n_A = int(N * group_A_prop)
    n_B = N - n_A
    
    S_A = int(S * seat_prop_A)
    S_B = int(S * seat_prop_B)
    S_C = int(S * seat_prop_C)
    
    # Validate value ordering
    if not (V_A > V_B > V_C):
        st.error("Programme values must satisfy: V_A > V_B > V_C")
        return None
    
    results = {}
    
    # Step 1: Group A Analysis
    st.header("Step 1: Group A Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Group A Applicants", f"{n_A:,}")
        st.metric("Type A Seats", f"{S_A:,}")
    
    if n_A <= S_A:
        admission_rate_A = 1.0
        expected_payoff_A = V_A
        status = "✅ All Group A can be admitted to Type A"
    else:
        admission_rate_A = S_A / n_A
        expected_payoff_A = admission_rate_A * V_A
        status = f"⚠️ Only {admission_rate_A:.1%} of Group A can be admitted to Type A"
    
    with col2:
        st.metric("Admission Rate", f"{admission_rate_A:.1%}")
        st.metric("Expected Payoff", f"{expected_payoff_A:.2f}")
    
    st.info(status)
    results['group_A'] = {'admission_rate': admission_rate_A, 'expected_payoff': expected_payoff_A}
    
    # Step 2: Group B Analysis
    st.header("Step 2: Group B Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Group B Applicants", f"{n_B:,}")
        st.metric("Type B Seats", f"{S_B:,}")
        st.metric("Type C Seats", f"{S_C:,}")
    
    # Calculate K = V_B / V_C
    K = V_B / V_C
    K_lower = 0.75  # 3/4
    K_upper = 4/3   # ~1.333
    
    with col2:
        st.metric("K = V_B/V_C", f"{K:.3f}")
        st.metric("MSE Range", f"({K_lower:.3f}, {K_upper:.3f})")
    
    # Check MSE condition
    st.subheader("Mixed Strategy Equilibrium (MSE) Analysis")
    
    if K_lower < K < K_upper:
        st.success(f"✅ MSE EXISTS (K = {K:.3f} is within range)")
        
        # Calculate equilibrium fraction f
        f = K / (1 + K)
        
        # Apply probability constraints
        f_min = S_B / n_B if S_B < n_B else 0
        f_max = 1 - (S_C / n_B) if S_C < n_B * (1 - f) else 1
        
        # Adjust f to stay within constraints
        f = max(f_min, min(f, f_max))
        
        # Calculate admission probabilities
        P_B = S_B / (n_B * f) if f > 0 else 0
        P_C = S_C / (n_B * (1 - f)) if f < 1 else 0
        
        # Cap probabilities at 1
        P_B = min(P_B, 1.0)
        P_C = min(P_C, 1.0)
        
        # Calculate expected payoffs
        E_B = P_B * V_B
        E_C = P_C * V_C
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Equilibrium f", f"{f:.3f}")
            st.caption("Fraction choosing Type B")
        with col2:
            st.metric("P(B)", f"{P_B:.3f}")
            st.caption("Admission prob Type B")
        with col3:
            st.metric("P(C)", f"{P_C:.3f}")
            st.caption("Admission prob Type C")
        
        st.markdown(f"**Expected Payoffs:**")
        st.markdown(f"- Type B: E(B) = {P_B:.3f} × {V_B:.1f} = **{E_B:.3f}**")
        st.markdown(f"- Type C: E(C) = {P_C:.3f} × {V_C:.1f} = **{E_C:.3f}**")
        
        if abs(E_B - E_C) < 0.001:
            st.success("✅ Indifference condition holds (E_B ≈ E_C)")
        else:
            st.warning(f"⚠️ Small deviation: Δ = {abs(E_B - E_C):.4f}")
        
        results['group_B'] = {
            'equilibrium_type': 'MSE',
            'f': f,
            'P_B': P_B,
            'P_C': P_C,
            'E_B': E_B,
            'E_C': E_C
        }
        
    else:
        st.error(f"❌ MSE DOES NOT EXIST (K = {K:.3f} is outside range)")
        
        # Analyze corner solutions
        st.subheader("Corner Solution Analysis")
        
        # Symmetric move analysis
        P_B_all = min(1.0, S_B / n_B)
        E_B_all = P_B_all * V_B
        
        P_C_all = min(1.0, S_C / n_B)
        E_C_all = P_C_all * V_C
        
        # Determine which corner is better
        if E_B_all > E_C_all:
            preferred = "Type B"
            equilibrium_type = "corner_B"
            admission_rate = P_B_all
            expected_payoff = E_B_all
        elif E_C_all > E_B_all:
            preferred = "Type C"
            equilibrium_type = "corner_C"
            admission_rate = P_C_all
            expected_payoff = E_C_all
        else:
            preferred = "Indifferent"
            equilibrium_type = "multiple"
            admission_rate = P_B_all
            expected_payoff = E_B_all
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**All choose Type B:**")
            st.markdown(f"- Admission rate: {P_B_all:.3f}")
            st.markdown(f"- Expected payoff: {E_B_all:.3f}")
        
        with col2:
            st.markdown("**All choose Type C:**")
            st.markdown(f"- Admission rate: {P_C_all:.3f}")
            st.markdown(f"- Expected payoff: {E_C_all:.3f}")
        
        st.info(f"**Preferred corner:** {preferred}")
        st.info(f"**Admission rate:** {admission_rate:.3f}")
        st.info(f"**Expected payoff:** {expected_payoff:.3f}")
        
        # Asymmetric move analysis
        st.subheader("Asymmetric Move Analysis")
        
        threshold_ratio = V_B / V_C
        # For a switch to be rational: P_C > threshold_ratio × P_B
        
        # Quick check at boundaries
        x_small = 1
        P_B_small = min(1.0, S_B / (n_B - x_small))
        P_C_small = min(1.0, S_C / x_small)
        
        x_half = n_B // 2
        P_B_half = min(1.0, S_B / (n_B - x_half))
        P_C_half = min(1.0, S_C / x_half)
        
        condition_small = P_C_small > threshold_ratio * P_B_small
        condition_half = P_C_half > threshold_ratio * P_B_half
        
        st.markdown(f"**Threshold ratio:** {threshold_ratio:.3f} (V_B/V_C)")
        st.markdown(f"**Condition at x=1:** P_C({P_C_small:.3f}) > {threshold_ratio:.3f} × P_B({P_B_small:.3f}) = {condition_small}")
        st.markdown(f"**Condition at x=n_B/2:** P_C({P_C_half:.3f}) > {threshold_ratio:.3f} × P_B({P_B_half:.3f}) = {condition_half}")
        
        if not (condition_small or condition_half):
            st.markdown("**Conclusion:** Switching to Type C is hard to rationalize")
        
        # Value adjustment suggestions
        st.subheader("Value Adjustment Suggestions")
        
        if K <= K_lower:
            target_K = (K_lower + K_upper) / 2
            required_V_B = target_K * V_C
            required_V_C = V_B / target_K
            
            st.markdown(f"**Issue:** K = {K:.3f} ≤ {K_lower:.3f} (too low)")
            st.markdown("**To achieve MSE:**")
            st.markdown(f"- Increase V_B to at least **{required_V_B:.2f}**")
            st.markdown(f"- Or decrease V_C to at most **{required_V_C:.2f}**")
            
        elif K >= K_upper:
            target_K = (K_lower + K_upper) / 2
            required_V_B = target_K * V_C
            required_V_C = V_B / target_K
            
            st.markdown(f"**Issue:** K = {K:.3f} ≥ {K_upper:.3f} (too high)")
            st.markdown("**To achieve MSE:**")
            st.markdown(f"- Decrease V_B to at most **{required_V_B:.2f}**")
            st.markdown(f"- Or increase V_C to at least **{required_V_C:.2f}**")
        
        results['group_B'] = {
            'equilibrium_type': equilibrium_type,
            'preferred_corner': preferred,
            'admission_rate': admission_rate,
            'expected_payoff': expected_payoff,
            'K': K,
            'K_lower': K_lower,
            'K_upper': K_upper
        }
    
    return results

# Run analysis with current parameters
params = st.session_state.params

try:
    results = analyze_jupas(
        params['N'], params['S'], params['group_A_prop'],
        params['V_A'], params['V_B'], params['V_C'],
        params['seat_prop_A'], params['seat_prop_B'], params['seat_prop_C']
    )
    
    # Summary section
    if results:
        st.header("Summary")
        
        if results['group_B'].get('equilibrium_type') == 'MSE':
            st.success(f"**Equilibrium Type:** Mixed Strategy Equilibrium")
            st.info(f"**Fraction choosing Type B:** {results['group_B']['f']:.3f}")
            st.info(f"**Expected payoff for Group B:** ~{results['group_B']['E_B']:.3f}")
        else:
            st.info(f"**Equilibrium Type:** Corner Solution ({results['group_B']['equilibrium_type']})")
            st.info(f"**Preferred choice:** {results['group_B']['preferred_corner']}")
            st.info(f"**Expected payoff for Group B:** {results['group_B']['expected_payoff']:.3f}")
        
        st.info(f"**Expected payoff for Group A:** {results['group_A']['expected_payoff']:.3f}")
        
except Exception as e:
    st.error(f"Error in analysis: {str(e)}")

# Quick analysis examples
st.sidebar.header("Quick Examples")
if st.sidebar.button("Situation 4 (Default)"):
    st.session_state.params = {
        'N': 10000, 'S': 9000, 'group_A_prop': 0.3,
        'V_A': 3.0, 'V_B': 2.0, 'V_C': 1.0,
        'seat_prop_A': 1/3, 'seat_prop_B': 1/3, 'seat_prop_C': 1/3
    }
    st.rerun()

if st.sidebar.button("Situation 5 (MSE Example)"):
    st.session_state.params = {
        'N': 10000, 'S': 9000, 'group_A_prop': 0.3,
        'V_A': 3.0, 'V_B': 1.2, 'V_C': 1.0,  # K = 1.2, within MSE range
        'seat_prop_A': 1/3, 'seat_prop_B': 1/3, 'seat_prop_C': 1/3
    }
    st.rerun()

if st.sidebar.button("High Competition"):
    st.session_state.params = {
        'N': 15000, 'S': 9000, 'group_A_prop': 0.4,
        'V_A': 5.0, 'V_B': 3.0, 'V_C': 1.5,
        'seat_prop_A': 0.4, 'seat_prop_B': 0.4, 'seat_prop_C': 0.2
    }
    st.rerun()

# Display current parameters
with st.sidebar.expander("Current Parameters"):
    st.json(st.session_state.params)
