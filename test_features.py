"""Quick test script to verify all advanced features work"""

from thread_engagement import *

# Test thread
thread = parse_metric_thread("M10")
F_design = 15000
sigma_y_bolt = 900  # Grade 10.9
sigma_y_hole = 276  # 6061-T6 Aluminum
n_bolt = 2.5
n_hole = 2.0

print("=" * 60)
print("TESTING ADVANCED FEATURES")
print("=" * 60)

# Calculate basic engagement
Le = required_engagement_for_design_load(thread, F_design, sigma_y_hole, n_hole)
print(f"\n1. Basic Calculation:")
print(f"   Thread: {thread.designation}")
print(f"   Required engagement: {Le:.2f} mm")

# Test stress analysis
print(f"\n2. Stress Analysis:")
stress = calculate_stress_analysis(thread, F_design, Le, sigma_y_bolt, sigma_y_hole)
print(f"   ✓ Bolt stress: {stress['bolt_stress_MPa']:.1f} MPa ({stress['bolt_utilization']*100:.1f}%)")
print(f"   ✓ Thread shear: {stress['thread_shear_stress_MPa']:.1f} MPa ({stress['thread_utilization']*100:.1f}%)")

# Test torque calculation
print(f"\n3. Torque Calculation:")
try:
    torque = calculate_assembly_torque(thread, sigma_y_bolt, n_bolt, friction_coef=0.15)
    print(f"   ✓ Recommended torque: {torque['torque_recommended_Nm']:.1f} Nm")
    print(f"   ✓ Range: {torque['torque_min_Nm']:.1f} - {torque['torque_max_Nm']:.1f} Nm")
    print(f"   ✓ Preload: {torque['preload_force_N']:.0f} N")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test recommendations
print(f"\n4. Design Recommendations:")
try:
    results_dict = {
        'stress_analysis': stress,
        'L_e_mm': Le,
        'n_threads': Le / thread.p,
        'margin': 2.5,
        'F_design_N': F_design
    }
    recs = generate_design_recommendations(
        results_dict,
        thread,
        sigma_y_bolt,
        sigma_y_hole
    )
    print(f"   ✓ Critical: {len(recs.get('critical', []))}")
    print(f"   ✓ Warnings: {len(recs.get('warnings', []))}")
    print(f"   ✓ Info: {len(recs.get('recommendations', []))}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test fatigue analysis
print(f"\n5. Fatigue Analysis:")
try:
    fatigue = fatigue_analysis(
        thread, F_mean_N=F_design, F_amplitude_N=5000,
        sigma_y_bolt_MPa=sigma_y_bolt, cycles_expected=1e7, surface_finish='machined'
    )
    print(f"   ✓ Status: {fatigue['status']}")
    print(f"   ✓ Safety factor: {fatigue['fatigue_safety_factor']:.2f}")
    print(f"   ✓ Endurance limit: {fatigue['endurance_limit_MPa']:.1f} MPa")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test helicoil design
print(f"\n6. Helicoil Analysis:")
try:
    helicoil = helicoil_design(thread, sigma_y_hole, F_design, n_hole)
    print(f"   ✓ Insert type: {helicoil['insert_type']}")
    print(f"   ✓ New engagement: {helicoil['engagement_with_insert_mm']:.2f} mm")
    print(f"   ✓ Reduction: {helicoil['engagement_reduction_percent']:.1f}%")
    print(f"   ✓ Recommendation: {helicoil['recommendation']}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test standards compliance
print(f"\n7. Standards Compliance:")
try:
    results_dict = {
        'stress_analysis': stress,
        'L_e_mm': Le,
        'n_threads': Le / thread.p,
        'margin': 2.5
    }
    standards = check_standards_compliance(
        results_dict,
        thread,
        standard='VDI2230'
    )
    print(f"   ✓ Standard: {standards['standard']}")
    print(f"   ✓ Compliant: {standards['compliant']}")
    print(f"   ✓ Checks: {len(standards['checks'])}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test load cases
print(f"\n8. Multiple Load Cases:")
try:
    cases = [
        LoadCase("Assembly", 5000, 0.5),
        LoadCase("Operating", 15000, 1.0),
        LoadCase("Peak", 22000, 0.8)
    ]
    results = analyze_load_cases(thread, cases, sigma_y_bolt, sigma_y_hole, n_bolt, n_hole)
    print(f"   ✓ Cases analyzed: {len(results['all_cases'])}")
    print(f"   ✓ Critical load: {results['design_for']}")
    print(f"   ✓ Design engagement: {results['design_engagement_mm']:.2f} mm")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test unit conversions
print(f"\n9. Unit Conversions:")
try:
    force_lbf = convert_units(15000, 'N', 'lbf')
    torque_ftlb = convert_units(22.5, 'Nm', 'ft-lbf')
    stress_ksi = convert_units(400, 'MPa', 'ksi')
    print(f"   ✓ 15000 N = {force_lbf:.1f} lbf")
    print(f"   ✓ 22.5 Nm = {torque_ftlb:.1f} ft-lbf")
    print(f"   ✓ 400 MPa = {stress_ksi:.1f} ksi")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE!")
print("=" * 60)
