import numpy as np
from typing import Dict, Tuple, Optional, List
import matplotlib.pyplot as plt

class JUPASAnalyzer:
    """
    A tool for analyzing JUPAS competition scenarios based on game theory.
    Implements the analysis flow from Situations 4 and 5 of the paper.
    """
    
    def __init__(self):
        """Initialize the analyzer with default parameters."""
        self.reset_parameters()
    
    def reset_parameters(self):
        """Reset all parameters to default values."""
        # Default parameters (can be customized)
        self.N = 10000  # Total number of applicants
        self.S = 9000   # Total number of seats
        
        # Group proportions
        self.group_A_prop = 0.3  # Top 30% (More Competitive)
        self.group_B_prop = 0.7  # Remaining 70% (Less Competitive)
        
        # Programme values
        self.V_A = 3.0  # Value of Type A programmes
        self.V_B = 2.0  # Value of Type B programmes
        self.V_C = 1.0  # Value of Type C programmes
        
        # Seat distribution proportions across programme types
        self.seat_prop_A = 1/3  # Proportion of seats in Type A
        self.seat_prop_B = 1/3  # Proportion of seats in Type B
        self.seat_prop_C = 1/3  # Proportion of seats in Type C
        
        # Programme size distribution within each type (for mixed strategy analysis)
        self.prog_sizes = [20, 50, 100]  # Different programme capacities
        self.size_dist_A = [0.4, 0.4, 0.2]  # Distribution for Type A
        self.size_dist_B = [0.4, 0.4, 0.2]  # Distribution for Type B
        self.size_dist_C = [0.4, 0.4, 0.2]  # Distribution for Type C
        
        # Derived quantities
        self._calculate_derived_quantities()
    
    def _calculate_derived_quantities(self):
        """Calculate derived quantities from current parameters."""
        # Group sizes
        self.n_A = int(self.N * self.group_A_prop)
        self.n_B = self.N - self.n_A
        
        # Seat counts by type
        self.S_A = int(self.S * self.seat_prop_A)
        self.S_B = int(self.S * self.seat_prop_B)
        self.S_C = self.S - self.S_A - self.S_B
        
        # Validate value ordering
        if not (self.V_A > self.V_B > self.V_C):
            raise ValueError("Programme values must satisfy: V_A > V_B > V_C")
        
        # Validate proportions sum to 1
        if abs(self.seat_prop_A + self.seat_prop_B + self.seat_prop_C - 1) > 0.01:
            raise ValueError("Seat proportions must sum to 1")
    
    def set_parameters(self, **kwargs):
        """Set custom parameters for the analysis."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
        
        self._calculate_derived_quantities()
    
    def analyze_group_A(self) -> Dict:
        """
        Step 1: Analyze Group A (More Competitive) strategy.
        
        Returns:
            Dictionary containing Group A analysis results
        """
        results = {}
        
        # Check if Group A can occupy all Type A seats
        if self.n_A <= self.S_A:
            # Enough Type A seats for all Group A
            results['occupancy'] = 'complete'
            results['admission_rate'] = 1.0
            results['expected_payoff'] = self.V_A
            
            # Mixed strategy across programme sizes
            mixed_strategy = []
            for i, size in enumerate(self.prog_sizes):
                # Calculate number of programmes of this size
                n_progs = int(self.S_A * self.size_dist_A[i] / size)
                if n_progs > 0:
                    admission_prob = 1.0  # Guaranteed admission for Group A
                    expected_payoff = admission_prob * self.V_A
                    mixed_strategy.append({
                        'programme_type': 'A',
                        'size': size,
                        'probability': self.size_dist_A[i],
                        'admission_prob': admission_prob,
                        'expected_payoff': expected_payoff
                    })
            
            results['mixed_strategy'] = mixed_strategy
            results['all_admitted'] = True
            
        else:
            # Not enough Type A seats for all Group A
            results['occupancy'] = 'partial'
            results['admission_rate'] = self.S_A / self.n_A
            results['expected_payoff'] = results['admission_rate'] * self.V_A
            results['all_admitted'] = False
        
        return results
    
    def analyze_group_B_mse_condition(self) -> Dict:
        """
        Step 2: Analyze Mixed Strategy Equilibrium (MSE) condition for Group B.
        Based on Situation 5 analysis with variable K.
        
        Returns:
            Dictionary containing MSE analysis results
        """
        results = {}
        
        # Calculate effective K (relative value of Type B vs Type C)
        K = self.V_B / self.V_C  # This is the K from Situation 5
        
        # Calculate the range for MSE existence (from Situation 5 analysis)
        K_lower = 0.75  # 3/4
        K_upper = 4/3   # approximately 1.333
        
        results['K'] = K
        results['K_lower'] = K_lower
        results['K_upper'] = K_upper
        results['mse_exists'] = K_lower < K < K_upper
        
        if results['mse_exists']:
            # Calculate equilibrium fraction f (from Situation 5)
            f = K / (1 + K)  # This is the equilibrium fraction choosing Type B
            
            # Ensure f is within feasible range considering capacity constraints
            # Capacity constraints: f must satisfy P_B <= 1 and P_C <= 1
            P_B = self.S_B / (self.n_B * f) if f > 0 else float('inf')
            P_C = self.S_C / (self.n_B * (1 - f)) if f < 1 else float('inf')
            
            # Adjust f if probability constraints are violated
            if P_B > 1:
                f_min = self.S_B / self.n_B
                f = max(f, f_min)
            if P_C > 1:
                f_max = 1 - (self.S_C / self.n_B)
                f = min(f, f_max)
            
            results['f_equilibrium'] = f
            results['P_B'] = self.S_B / (self.n_B * f) if f > 0 else 0
            results['P_C'] = self.S_C / (self.n_B * (1 - f)) if f < 1 else 0
            
            # Expected payoffs
            results['E_B'] = results['P_B'] * self.V_B
            results['E_C'] = results['P_C'] * self.V_C
            
            # Check if indifference condition holds
            results['indifference_holds'] = abs(results['E_B'] - results['E_C']) < 0.001
        
        return results
    
    def analyze_group_B_corner_solution(self) -> Dict:
        """
        Analyze Group B corner solution when MSE doesn't exist.
        Based on Situation 4 analysis.
        
        Returns:
            Dictionary containing corner solution analysis
        """
        results = {}
        
        # Symmetric move analysis (all choose same type)
        # If all choose Type B
        P_B_all = min(1.0, self.S_B / self.n_B)
        E_B_all = P_B_all * self.V_B
        
        # If all choose Type C
        P_C_all = min(1.0, self.S_C / self.n_B)
        E_C_all = P_C_all * self.V_C
        
        # Determine which corner solution is better
        results['P_B_symmetric'] = P_B_all
        results['E_B_symmetric'] = E_B_all
        results['P_C_symmetric'] = P_C_all
        results['E_C_symmetric'] = E_C_all
        
        if E_B_all > E_C_all:
            results['preferred_corner'] = 'Type B'
            results['equilibrium_type'] = 'corner_B'
            results['admission_rate'] = P_B_all
            results['expected_payoff'] = E_B_all
        elif E_C_all > E_B_all:
            results['preferred_corner'] = 'Type C'
            results['equilibrium_type'] = 'corner_C'
            results['admission_rate'] = P_C_all
            results['expected_payoff'] = E_C_all
        else:
            results['preferred_corner'] = 'indifferent'
            results['equilibrium_type'] = 'multiple_corners'
            results['admission_rate'] = P_B_all  # Both equal
            results['expected_payoff'] = E_B_all
        
        # Asymmetric move analysis
        results['threshold_analysis'] = self._analyze_asymmetric_threshold()
        
        return results
    
    def _analyze_asymmetric_threshold(self) -> Dict:
        """
        Analyze the condition for rational switching to Type C.
        From Situation 4 analysis.
        """
        results = {}
        
        # The condition: P_C > 2 * P_B (when V_B = 2, V_C = 1)
        # Generalized: P_C > (V_B / V_C) * P_B
        
        threshold_ratio = self.V_B / self.V_C
        
        # Find x (number switching to C) that satisfies the condition
        # We'll find if there exists any x such that the condition holds
        
        # Check boundary conditions
        # When x is very small (almost no one in C)
        x_small = 1
        P_B_small = min(1.0, self.S_B / (self.n_B - x_small))
        P_C_small = min(1.0, self.S_C / x_small)
        condition_small = P_C_small > threshold_ratio * P_B_small
        
        # When x is half
        x_half = self.n_B // 2
        P_B_half = min(1.0, self.S_B / (self.n_B - x_half))
        P_C_half = min(1.0, self.S_C / x_half)
        condition_half = P_C_half > threshold_ratio * P_B_half
        
        results['threshold_ratio'] = threshold_ratio
        results['condition_small_x'] = condition_small
        results['condition_half_x'] = condition_half
        results['hard_to_achieve'] = not (condition_small or condition_half)
        
        return results
    
    def suggest_value_adjustment(self, current_K: float) -> Dict:
        """
        Suggest how to adjust programme values to achieve MSE.
        
        Args:
            current_K: Current K value (V_B / V_C)
            
        Returns:
            Dictionary with adjustment suggestions
        """
        suggestions = {}
        K_lower = 0.75
        K_upper = 4/3
        
        if current_K <= K_lower:
            suggestions['issue'] = 'K too low for MSE'
            suggestions['current_range'] = f"K = {current_K:.3f} ≤ {K_lower}"
            suggestions['suggestion'] = f"Increase V_B or decrease V_C to achieve K > {K_lower}"
            suggestions['target_K'] = (K_lower + K_upper) / 2  # Target middle of range
            
        elif current_K >= K_upper:
            suggestions['issue'] = 'K too high for MSE'
            suggestions['current_range'] = f"K = {current_K:.3f} ≥ {K_upper}"
            suggestions['suggestion'] = f"Decrease V_B or increase V_C to achieve K < {K_upper}"
            suggestions['target_K'] = (K_lower + K_upper) / 2  # Target middle of range
            
        else:
            suggestions['issue'] = 'MSE exists'
            suggestions['current_range'] = f"{K_lower} < K = {current_K:.3f} < {K_upper}"
            suggestions['suggestion'] = "No adjustment needed for MSE"
            suggestions['target_K'] = current_K
        
        return suggestions
    
    def full_analysis(self) -> Dict:
        """
        Perform complete analysis following the paper's flow.
        
        Returns:
            Comprehensive analysis results
        """
        print("=" * 60)
        print("JUPAS COMPETITION ANALYSIS TOOL")
        print("=" * 60)
        print(f"\nParameters:")
        print(f"  Total Applicants (N): {self.N:,}")
        print(f"  Total Seats (S): {self.S:,}")
        print(f"  Group A (Top {self.group_A_prop*100:.0f}%): {self.n_A:,}")
        print(f"  Group B (Remaining {self.group_B_prop*100:.0f}%): {self.n_B:,}")
        print(f"  Programme Values: A={self.V_A}, B={self.V_B}, C={self.V_C}")
        print(f"  Seat Distribution: A={self.seat_prop_A:.1%}, B={self.seat_prop_B:.1%}, C={self.seat_prop_C:.1%}")
        
        # Step 1: Group A analysis
        print("\n" + "=" * 60)
        print("STEP 1: GROUP A ANALYSIS (More Competitive)")
        print("=" * 60)
        group_A_results = self.analyze_group_A()
        
        print(f"\nGroup A Statistics:")
        print(f"  Number of applicants: {self.n_A:,}")
        print(f"  Type A seats available: {self.S_A:,}")
        
        if group_A_results['all_admitted']:
            print(f"  ✅ All Group A applicants can be admitted to Type A programmes")
            print(f"  Admission rate: {group_A_results['admission_rate']:.1%}")
            print(f"  Expected payoff: {group_A_results['expected_payoff']:.3f}")
        else:
            print(f"  ⚠️  Not enough Type A seats for all Group A applicants")
            print(f"  Admission rate: {group_A_results['admission_rate']:.1%}")
            print(f"  Expected payoff: {group_A_results['expected_payoff']:.3f}")
        
        # Step 2: Group B analysis
        print("\n" + "=" * 60)
        print("STEP 2: GROUP B ANALYSIS (Less Competitive)")
        print("=" * 60)
        
        # First check MSE condition
        mse_analysis = self.analyze_group_B_mse_condition()
        
        print(f"\nMixed Strategy Equilibrium (MSE) Analysis:")
        print(f"  K = V_B / V_C = {self.V_B:.2f} / {self.V_C:.2f} = {mse_analysis['K']:.3f}")
        print(f"  MSE exists when: {mse_analysis['K_lower']:.3f} < K < {mse_analysis['K_upper']:.3f}")
        
        if mse_analysis['mse_exists']:
            print(f"  ✅ MSE EXISTS for current parameters")
            print(f"  Equilibrium fraction choosing Type B (f): {mse_analysis['f_equilibrium']:.3f}")
            print(f"  Admission probability - Type B: {mse_analysis['P_B']:.3f}")
            print(f"  Admission probability - Type C: {mse_analysis['P_C']:.3f}")
            print(f"  Expected payoff - Type B: {mse_analysis['E_B']:.3f}")
            print(f"  Expected payoff - Type C: {mse_analysis['E_C']:.3f}")
            
            if mse_analysis['indifference_holds']:
                print(f"  ✅ Indifference condition holds (E_B ≈ E_C)")
            else:
                print(f"  ⚠️  Small deviation from indifference: Δ = {abs(mse_analysis['E_B'] - mse_analysis['E_C']):.4f}")
            
            equilibrium_type = "MSE"
            
        else:
            print(f"  ❌ MSE DOES NOT EXIST for current parameters")
            print(f"  K = {mse_analysis['K']:.3f} is outside the range ({mse_analysis['K_lower']:.3f}, {mse_analysis['K_upper']:.3f})")
            
            # Analyze corner solution
            corner_analysis = self.analyze_group_B_corner_solution()
            
            print(f"\nCorner Solution Analysis:")
            print(f"  Symmetric move - All choose Type B:")
            print(f"    Admission rate: {corner_analysis['P_B_symmetric']:.3f}")
            print(f"    Expected payoff: {corner_analysis['E_B_symmetric']:.3f}")
            print(f"  Symmetric move - All choose Type C:")
            print(f"    Admission rate: {corner_analysis['P_C_symmetric']:.3f}")
            print(f"    Expected payoff: {corner_analysis['E_C_symmetric']:.3f}")
            
            print(f"\n  Preferred corner solution: {corner_analysis['preferred_corner']}")
            print(f"  Equilibrium type: {corner_analysis['equilibrium_type']}")
            print(f"  Admission rate at equilibrium: {corner_analysis['admission_rate']:.3f}")
            print(f"  Expected payoff at equilibrium: {corner_analysis['expected_payoff']:.3f}")
            
            # Asymmetric move analysis
            threshold = corner_analysis['threshold_analysis']
            print(f"\n  Asymmetric move analysis:")
            print(f"    Threshold ratio V_B/V_C = {threshold['threshold_ratio']:.3f}")
            print(f"    Is switching rational? {not threshold['hard_to_achieve']}")
            
            equilibrium_type = corner_analysis['equilibrium_type']
            
            # Provide value adjustment suggestions
            suggestions = self.suggest_value_adjustment(mse_analysis['K'])
            print(f"\n  Value Adjustment Suggestions:")
            print(f"    Issue: {suggestions['issue']}")
            print(f"    Current: {suggestions['current_range']}")
            print(f"    Suggestion: {suggestions['suggestion']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        summary = {
            'group_A': group_A_results,
            'mse_analysis': mse_analysis,
            'equilibrium_type': equilibrium_type,
            'parameters': {
                'N': self.N,
                'S': self.S,
                'n_A': self.n_A,
                'n_B': self.n_B,
                'V_A': self.V_A,
                'V_B': self.V_B,
                'V_C': self.V_C,
                'S_A': self.S_A,
                'S_B': self.S_B,
                'S_C': self.S_C
            }
        }
        
        if mse_analysis['mse_exists']:
            summary['group_B'] = {
                'equilibrium_type': 'MSE',
                'f_equilibrium': mse_analysis['f_equilibrium'],
                'admission_rate_B': mse_analysis['P_B'],
                'admission_rate_C': mse_analysis['P_C'],
                'expected_payoff_B': mse_analysis['E_B'],
                'expected_payoff_C': mse_analysis['E_C']
            }
            print(f"✅ Equilibrium Type: Mixed Strategy Equilibrium (MSE)")
            print(f"   Fraction choosing Type B: {mse_analysis['f_equilibrium']:.3f}")
            print(f"   Expected payoff (both types): ~{mse_analysis['E_B']:.3f}")
        else:
            summary['group_B'] = {
                'equilibrium_type': corner_analysis['equilibrium_type'],
                'preferred_corner': corner_analysis['preferred_corner'],
                'admission_rate': corner_analysis['admission_rate'],
                'expected_payoff': corner_analysis['expected_payoff']
            }
            print(f"📊 Equilibrium Type: Corner Solution ({corner_analysis['equilibrium_type']})")
            print(f"   Preferred choice: {corner_analysis['preferred_corner']}")
            print(f"   Admission rate: {corner_analysis['admission_rate']:.3f}")
            print(f"   Expected payoff: {corner_analysis['expected_payoff']:.3f}")
        
        return summary
    
    def visualize_analysis(self, summary: Dict):
        """Create visualizations of the analysis results."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('JUPAS Competition Analysis', fontsize=16)
        
        # Plot 1: Group sizes and seat distribution
        ax1 = axes[0, 0]
        groups = ['Group A', 'Group B']
        group_sizes = [self.n_A, self.n_B]
        seats_by_group = [self.S_A, min(self.S_B + self.S_C, self.n_B)]
        
        x = np.arange(len(groups))
        width = 0.35
        
        ax1.bar(x - width/2, group_sizes, width, label='Applicants', color='skyblue')
        ax1.bar(x + width/2, seats_by_group, width, label='Available Seats', color='lightcoral')
        
        ax1.set_xlabel('Group')
        ax1.set_ylabel('Count')
        ax1.set_title('Applicants vs Available Seats by Group')
        ax1.set_xticks(x)
        ax1.set_xticklabels(groups)
        ax1.legend()
        
        # Plot 2: Programme values
        ax2 = axes[0, 1]
        programme_types = ['Type A', 'Type B', 'Type C']
        values = [self.V_A, self.V_B, self.V_C]
        
        bars = ax2.bar(programme_types, values, color=['gold', 'silver', 'brown'])
        ax2.set_xlabel('Programme Type')
        ax2.set_ylabel('Value')
        ax2.set_title('Programme Values')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # Plot 3: Seat distribution
        ax3 = axes[1, 0]
        seat_counts = [self.S_A, self.S_B, self.S_C]
        colors = ['gold', 'silver', 'brown']
        
        ax3.pie(seat_counts, labels=programme_types, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax3.set_title('Seat Distribution by Programme Type')
        
        # Plot 4: K-value analysis for MSE
        ax4 = axes[1, 1]
        K = self.V_B / self.V_C
        K_range = np.linspace(0.5, 2.0, 100)
        mse_region = (K_range > 0.75) & (K_range < 4/3)
        
        ax4.axvspan(0.75, 4/3, alpha=0.3, color='green', label='MSE Region')
        ax4.axvline(K, color='red', linestyle='--', linewidth=2, label=f'Current K = {K:.3f}')
        ax4.axvline(0.75, color='black', linestyle=':', linewidth=1, label='K lower bound')
        ax4.axvline(4/3, color='black', linestyle=':', linewidth=1, label='K upper bound')
        
        ax4.set_xlabel('K = V_B / V_C')
        ax4.set_ylabel('MSE Feasibility')
        ax4.set_title('Mixed Strategy Equilibrium Region')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


def interactive_analysis():
    """Interactive function to run the analyzer with custom parameters."""
    analyzer = JUPASAnalyzer()
    
    print("Welcome to the JUPAS Competition Analyzer!")
    print("\nDefault parameters:")
    print(f"  Total applicants: {analyzer.N:,}")
    print(f"  Total seats: {analyzer.S:,}")
    print(f"  Group A proportion: {analyzer.group_A_prop:.1%}")
    print(f"  Programme values: A={analyzer.V_A}, B={analyzer.V_B}, C={analyzer.V_C}")
    
    while True:
        print("\n" + "="*50)
        print("Options:")
        print("1. Run analysis with current parameters")
        print("2. Modify parameters")
        print("3. Reset to default")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            try:
                summary = analyzer.full_analysis()
                visualize = input("\nGenerate visualizations? (y/n): ").lower()
                if visualize == 'y':
                    analyzer.visualize_analysis(summary)
            except ValueError as e:
                print(f"Error: {e}")
        
        elif choice == '2':
            print("\nEnter new parameters (press Enter to keep current value):")
            
            try:
                N = input(f"Total applicants [{analyzer.N}]: ").strip()
                if N:
                    analyzer.N = int(N)
                
                S = input(f"Total seats [{analyzer.S}]: ").strip()
                if S:
                    analyzer.S = int(S)
                
                group_A = input(f"Group A proportion [{analyzer.group_A_prop:.2f}]: ").strip()
                if group_A:
                    analyzer.group_A_prop = float(group_A)
                
                V_A = input(f"Value of Type A programmes [{analyzer.V_A}]: ").strip()
                if V_A:
                    analyzer.V_A = float(V_A)
                
                V_B = input(f"Value of Type B programmes [{analyzer.V_B}]: ").strip()
                if V_B:
                    analyzer.V_B = float(V_B)
                
                V_C = input(f"Value of Type C programmes [{analyzer.V_C}]: ").strip()
                if V_C:
                    analyzer.V_C = float(V_C)
                
                # Recalculate seat proportions if needed
                analyzer._calculate_derived_quantities()
                
                print("Parameters updated successfully!")
                
            except ValueError as e:
                print(f"Invalid input: {e}")
        
        elif choice == '3':
            analyzer.reset_parameters()
            print("Parameters reset to default values.")
        
        elif choice == '4':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")


# Example usage
if __name__ == "__main__":
    # Create analyzer instance
    analyzer = JUPASAnalyzer()
    
    # Example 1: Run with default parameters (Situation 4)
    print("EXAMPLE 1: Default Parameters (Situation 4)")
    summary1 = analyzer.full_analysis()
    
    # Example 2: Modify parameters for MSE (Situation 5)
    print("\n" + "="*60)
    print("EXAMPLE 2: Modified Parameters for MSE (Situation 5)")
    analyzer.set_parameters(V_B=1.2, V_C=1.0)  # K = 1.2, within MSE range
    summary2 = analyzer.full_analysis()
    
    # Example 3: Interactive analysis
    print("\n" + "="*60)
    print("Starting Interactive Analysis...")
    interactive_analysis()
