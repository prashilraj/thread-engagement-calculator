import math
import argparse
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import json

# Coarse pitch table for common ISO metric threads (mm)
COARSE_PITCH = {
    'M3': 0.5,
    'M4': 0.7,
    'M5': 0.8,
    'M6': 1.0,
    'M8': 1.25,
    'M10': 1.5,
    'M12': 1.75,
    'M14': 2.0,
    'M16': 2.0,
    'M18': 2.5,
    'M20': 2.5,
    'M24': 3.0,
    'M27': 3.0,
    'M30': 3.5,
    'M33': 3.5,
    'M36': 4.0,
    'M39': 4.0,
    'M42': 4.5,
    'M48': 5.0,
    'M56': 5.5,
    'M64': 6.0,
}

# Fine pitch options for metric threads
FINE_PITCH = {
    'M8': [1.0],
    'M10': [1.25, 1.0],
    'M12': [1.5, 1.25, 1.0],
    'M14': [1.5, 1.25],
    'M16': [1.5, 1.0],
    'M18': [2.0, 1.5, 1.0],
    'M20': [2.0, 1.5, 1.0],
    'M24': [2.0, 1.5],
    'M30': [2.0, 1.5],
    'M36': [3.0, 2.0],
}

# Common engineering materials database
MATERIALS = {
    # Steels
    'Steel_1018': {'name': 'Low Carbon Steel (1018)', 'sigma_y': 370, 'type': 'steel'},
    'Steel_4140': {'name': 'Alloy Steel (4140)', 'sigma_y': 415, 'type': 'steel'},
    'Steel_4340': {'name': 'Alloy Steel (4340)', 'sigma_y': 470, 'type': 'steel'},
    'Steel_8.8': {'name': 'Grade 8.8 Bolt Steel', 'sigma_y': 640, 'type': 'steel'},
    'Steel_10.9': {'name': 'Grade 10.9 Bolt Steel', 'sigma_y': 900, 'type': 'steel'},
    'Steel_12.9': {'name': 'Grade 12.9 Bolt Steel', 'sigma_y': 1080, 'type': 'steel'},
    'SS_304': {'name': 'Stainless Steel 304', 'sigma_y': 215, 'type': 'stainless'},
    'SS_316': {'name': 'Stainless Steel 316', 'sigma_y': 205, 'type': 'stainless'},
    
    # Aluminum
    'Al_6061_T6': {'name': 'Aluminum 6061-T6', 'sigma_y': 275, 'type': 'aluminum'},
    'Al_7075_T6': {'name': 'Aluminum 7075-T6', 'sigma_y': 505, 'type': 'aluminum'},
    'Al_2024_T3': {'name': 'Aluminum 2024-T3', 'sigma_y': 345, 'type': 'aluminum'},
    
    # Cast Iron
    'Cast_Iron': {'name': 'Gray Cast Iron', 'sigma_y': 275, 'type': 'cast_iron'},
    
    # Brass/Bronze
    'Brass': {'name': 'Brass (C36000)', 'sigma_y': 125, 'type': 'brass'},
    'Bronze': {'name': 'Phosphor Bronze', 'sigma_y': 345, 'type': 'bronze'},
}


@dataclass
class MetricThread:
    designation: str  # e.g. 'M8x1.25'
    D: float          # nominal diameter (mm)
    p: float          # pitch (mm)
    At: float         # tensile stress area (mm^2)


def get_material_yield_strength(material_key: str) -> float:
    """Get yield strength for a material from database."""
    if material_key not in MATERIALS:
        raise ValueError(f"Material '{material_key}' not found. Use list-materials command.")
    return MATERIALS[material_key]['sigma_y']


def list_available_materials() -> None:
    """Print available materials from database."""
    print("\n=== Available Materials ===")
    categories = {}
    for key, data in MATERIALS.items():
        mat_type = data['type']
        if mat_type not in categories:
            categories[mat_type] = []
        categories[mat_type].append((key, data['name'], data['sigma_y']))
    
    for cat_name, items in sorted(categories.items()):
        print(f"\n{cat_name.upper()}:")
        for key, name, sigma_y in items:
            print(f"  {key:20s} - {name:30s} (σ_y = {sigma_y} MPa)")
    print()


def parse_metric_thread(designation: str) -> MetricThread:
    """
    Parse an ISO metric thread designation like:
      'M8', 'M8x1.25', 'M8-1.25'
    and return MetricThread with D, pitch p and tensile area At.
    """
    s = designation.strip().upper().replace(' ', '')
    if not s.startswith('M'):
        raise ValueError(f'Invalid metric thread designation: {designation}')

    s = s[1:]  # drop leading 'M'

    # Split on 'x' or '-' if pitch specified
    for sep in ('X', '-'):
        if sep in s:
            d_str, p_str = s.split(sep, 1)
            D = float(d_str)
            p = float(p_str)
            break
    else:
        # No explicit pitch: assume coarse pitch from table
        D = float(s)
        key = f'M{int(D) if D.is_integer() else D}'
        if key not in COARSE_PITCH:
            raise ValueError(
                f'No coarse pitch defined for {key}. '
                f'Use explicit pitch like "M{D}x1.25".'
            )
        p = COARSE_PITCH[key]

    At = tensile_stress_area(D, p)
    return MetricThread(designation=f'M{D}x{p}', D=D, p=p, At=At)


def tensile_stress_area(D: float, p: float) -> float:
    """
    ISO metric tensile stress area (mm^2) for a bolt:
      At = 0.7854 * (D - 0.9382 * p)^2
    """
    return 0.7854 * (D - 0.9382 * p) ** 2


def bolt_tensile_capacity(
    thread: MetricThread,
    sigma_y_bolt_MPa: float,
    n_bolt: float = 2.0,
) -> float:
    """
    Allowable bolt tensile capacity (N) based on yield strength.
    F_allow = At * (sigma_y_bolt / n_bolt)
    """
    sigma_allow_bolt = sigma_y_bolt_MPa / n_bolt  # MPa = N/mm^2
    return thread.At * sigma_allow_bolt           # N


def required_engagement_for_design_load(
    thread: MetricThread,
    F_design_N: float,
    sigma_y_hole_MPa: float,
    n_hole: float = 2.0,
    k_shear: float = 0.62,
) -> float:
    """
    Engagement length L_e (mm) so that internal threads do NOT strip
    under a given design tensile load F_design_N.
    """
    D = thread.D
    p = thread.p

    # Allowable shear stress in tapped material
    tau_allow = k_shear * sigma_y_hole_MPa / n_hole  # N/mm^2

    # Internal thread shear area factor per mm of engagement:
    # As_int = 0.5625 * p * (D - 0.54127 * p) * L_e
    As_factor = 0.5625 * p * (D - 0.54127 * p)  # mm^2 per mm

    if As_factor <= 0 or tau_allow <= 0:
        raise ValueError('Invalid geometry or material properties.')

    L_e = F_design_N / (As_factor * tau_allow)
    return L_e


def required_engagement_for_equal_strength(
    thread: MetricThread,
    sigma_y_bolt_MPa: float,
    sigma_y_hole_MPa: float,
    n_bolt: float = 2.0,
    n_hole: float = 2.0,
    k_shear: float = 0.62,
) -> tuple[float, float]:
    """
    Engagement length L_e (mm) so that THREADS are as strong as the BOLT.
    i.e. thread shear capacity (with n_hole) >= bolt tensile capacity (with n_bolt).

    Returns:
      (L_e_mm, F_bolt_allow_N)
    """
    F_bolt_allow = bolt_tensile_capacity(thread, sigma_y_bolt_MPa, n_bolt)

    D = thread.D
    p = thread.p

    tau_allow = k_shear * sigma_y_hole_MPa / n_hole
    As_factor = 0.5625 * p * (D - 0.54127 * p)

    if As_factor <= 0 or tau_allow <= 0:
        raise ValueError('Invalid geometry or material properties.')

    L_e = F_bolt_allow / (As_factor * tau_allow)
    return L_e, F_bolt_allow


def calculate_stress_analysis(
    thread: MetricThread,
    F_applied_N: float,
    L_e_mm: float,
    sigma_y_bolt_MPa: float,
    sigma_y_hole_MPa: float,
    k_shear: float = 0.62,
) -> dict:
    """
    Calculate detailed stress analysis for a given load and engagement.
    Returns dict with stress values and utilization ratios.
    """
    # Bolt tensile stress
    bolt_stress = F_applied_N / thread.At  # MPa
    bolt_utilization = bolt_stress / sigma_y_bolt_MPa
    
    # Thread shear stress
    As_factor = 0.5625 * thread.p * (thread.D - 0.54127 * thread.p)
    As_total = As_factor * L_e_mm
    thread_shear_stress = F_applied_N / As_total if As_total > 0 else float('inf')
    tau_y = k_shear * sigma_y_hole_MPa
    thread_utilization = thread_shear_stress / tau_y
    
    # Bearing stress (simplified)
    bearing_area = math.pi * thread.D * L_e_mm * 0.75  # approximate contact area
    bearing_stress = F_applied_N / bearing_area if bearing_area > 0 else float('inf')
    
    return {
        'bolt_stress_MPa': bolt_stress,
        'bolt_utilization': bolt_utilization,
        'thread_shear_stress_MPa': thread_shear_stress,
        'thread_utilization': thread_utilization,
        'bearing_stress_MPa': bearing_stress,
        'shear_area_mm2': As_total,
    }


def engagement_summary_design(
    designation: str,
    F_design_N: float,
    sigma_y_hole_MPa: float,
    n_hole: float = 2.0,
    sigma_y_bolt_MPa: float | None = None,
    n_bolt: float = 2.0,
    k_shear: float = 0.62,
    show_stress: bool = False,
) -> dict:
    """
    Print a summary for DESIGN-LOAD mode.
    Returns dict with results for programmatic use.
    """
    th = parse_metric_thread(designation)
    L_e = required_engagement_for_design_load(
        th,
        F_design_N=F_design_N,
        sigma_y_hole_MPa=sigma_y_hole_MPa,
        n_hole=n_hole,
        k_shear=k_shear,
    )
    n_threads = L_e / th.p

    print(f'Thread:          {th.designation}')
    print(f'Nominal D:       {th.D:.3f} mm')
    print(f'Pitch p:         {th.p:.3f} mm')
    print(f'Tensile area At: {th.At:.2f} mm^2')
    print()
    print(f'Design load:     {F_design_N:.0f} N')
    print(f'Hole material:   σ_y = {sigma_y_hole_MPa:.0f} MPa')
    print(f'SF on shear:     n_hole = {n_hole:.2f}')
    print()
    print(f'Min engagement:  L_e = {L_e:.2f} mm')
    print(f'Threads engaged: ~{n_threads:.1f} (L_e / p)')

    results = {
        'thread': th.designation,
        'L_e_mm': L_e,
        'n_threads': n_threads,
        'F_design_N': F_design_N,
    }

    if sigma_y_bolt_MPa is not None:
        F_bolt = bolt_tensile_capacity(th, sigma_y_bolt_MPa, n_bolt)
        margin = F_bolt / F_design_N
        print()
        print(f'Bolt:            σ_y = {sigma_y_bolt_MPa:.0f} MPa, n_bolt = {n_bolt:.2f}')
        print(f'Bolt capacity:   F_allow ≈ {F_bolt:.0f} N')
        print(f'Margin bolt/design load: {margin:.2f}×')
        results['F_bolt_allow_N'] = F_bolt
        results['margin'] = margin
        
        if show_stress:
            stress = calculate_stress_analysis(th, F_design_N, L_e, sigma_y_bolt_MPa, sigma_y_hole_MPa, k_shear)
            print()
            print('=== Stress Analysis ===')
            print(f'Bolt tensile stress:    {stress["bolt_stress_MPa"]:.1f} MPa ({stress["bolt_utilization"]*100:.1f}% of yield)')
            print(f'Thread shear stress:    {stress["thread_shear_stress_MPa"]:.1f} MPa ({stress["thread_utilization"]*100:.1f}% of allowable)')
            print(f'Bearing stress (approx): {stress["bearing_stress_MPa"]:.1f} MPa')
            results['stress_analysis'] = stress
    
    return results


def engagement_summary_equal(
    designation: str,
    sigma_y_bolt_MPa: float,
    sigma_y_hole_MPa: float,
    n_bolt: float = 2.0,
    n_hole: float = 2.0,
    k_shear: float = 0.62,
) -> dict:
    """
    Print a summary for EQUAL-STRENGTH mode.
    Returns dict with results for programmatic use.
    """
    th = parse_metric_thread(designation)
    L_e, F_bolt_allow = required_engagement_for_equal_strength(
        th,
        sigma_y_bolt_MPa=sigma_y_bolt_MPa,
        sigma_y_hole_MPa=sigma_y_hole_MPa,
        n_bolt=n_bolt,
        n_hole=n_hole,
        k_shear=k_shear,
    )
    n_threads = L_e / th.p

    print(f'Thread:          {th.designation}')
    print(f'Nominal D:       {th.D:.3f} mm')
    print(f'Pitch p:         {th.p:.3f} mm')
    print(f'Tensile area At: {th.At:.2f} mm^2')
    print()
    print(f'Bolt material:   σ_y = {sigma_y_bolt_MPa:.0f} MPa, n_bolt = {n_bolt:.2f}')
    print(f'Hole material:   σ_y = {sigma_y_hole_MPa:.0f} MPa, n_hole = {n_hole:.2f}')
    print()
    print('Condition: thread shear capacity (with n_hole)')
    print('           ≥ bolt tensile capacity (with n_bolt)')
    print()
    print(f'Bolt capacity:   F_allow ≈ {F_bolt_allow:.0f} N')
    print(f'Required L_e:    {L_e:.2f} mm')
    print(f'Threads engaged: ~{n_threads:.1f} (L_e / p)')
    
    return {
        'thread': th.designation,
        'L_e_mm': L_e,
        'n_threads': n_threads,
        'F_bolt_allow_N': F_bolt_allow,
    }


# ============================================================================
# PHASE 1: MUST-HAVE FEATURES
# ============================================================================

def calculate_assembly_torque(
    thread: MetricThread,
    sigma_y_bolt_MPa: float,
    n_bolt: float = 2.0,
    friction_coef: float = 0.15,
    preload_fraction: float = 0.75
) -> dict:
    """
    Calculate recommended installation torque for bolts.
    
    T = K × d × F_preload
    where K is the torque coefficient (friction-dependent)
    """
    # Proof load (typically 90% of yield)
    proof_strength = 0.9 * sigma_y_bolt_MPa
    F_proof = thread.At * proof_strength
    
    # Recommended preload (70-75% of proof load)
    F_preload = preload_fraction * F_proof
    
    # Torque calculation
    # K = 0.2 for dry steel, 0.15 for lubricated
    K_dry = 0.20
    K_lubricated = friction_coef
    
    torque_dry = K_dry * thread.D * F_preload / 1000  # Convert to Nm
    torque_lubricated = K_lubricated * thread.D * F_preload / 1000
    
    return {
        'preload_force_N': F_preload,
        'proof_load_N': F_proof,
        'torque_dry_Nm': torque_dry,
        'torque_lubricated_Nm': torque_lubricated,
        'torque_min_Nm': torque_lubricated * 0.9,
        'torque_max_Nm': torque_dry * 1.1,
        'torque_recommended_Nm': torque_lubricated,
        'friction_coefficient': friction_coef
    }


def generate_design_recommendations(
    results: dict,
    thread: MetricThread,
    sigma_y_bolt_MPa: float,
    sigma_y_hole_MPa: float
) -> dict:
    """
    Generate intelligent design recommendations based on results.
    """
    recommendations = []
    warnings = []
    critical = []
    
    # Check if stress analysis exists
    if 'stress_analysis' in results:
        stress = results['stress_analysis']
        bolt_util = stress['bolt_utilization']
        thread_util = stress['thread_utilization']
        
        # Bolt utilization checks
        if bolt_util > 0.90:
            critical.append("🚨 CRITICAL: Bolt stress >90% of yield - INCREASE BOLT SIZE IMMEDIATELY")
        elif bolt_util > 0.80:
            warnings.append("⚠️ High bolt stress (>80%) - consider next larger size")
        elif bolt_util > 0.60:
            recommendations.append("💡 Bolt stress moderate (60-80%) - acceptable but monitor")
        elif bolt_util < 0.30:
            recommendations.append("💡 Low bolt utilization (<30%) - could use smaller size for cost savings")
        
        # Thread utilization checks
        if thread_util > 0.90:
            critical.append("🚨 CRITICAL: Thread stress >90% - INCREASE ENGAGEMENT OR USE INSERT")
        elif thread_util > 0.80:
            warnings.append("⚠️ High thread stress (>80%) - increase engagement length")
        elif thread_util < 0.30:
            recommendations.append("💡 Low thread utilization - engagement could be reduced if space limited")
    
    # Check engagement practicality
    L_e = results['L_e_mm']
    D = thread.D
    
    if L_e < D * 1.0:
        warnings.append("⚠️ Engagement < 1× diameter - may be difficult to manufacture")
    if L_e > D * 3.0:
        recommendations.append("💡 Long engagement (>3× diameter) - consider larger diameter bolt instead")
    
    # Check threads engaged
    n_threads = results['n_threads']
    if n_threads < 5:
        warnings.append("⚠️ Less than 5 threads engaged - vulnerable to stripping")
    elif n_threads < 3:
        critical.append("🚨 CRITICAL: Less than 3 threads - UNSAFE for most applications")
    
    # Material mismatch
    if sigma_y_bolt_MPa / sigma_y_hole_MPa > 3:
        recommendations.append("💡 Large strength mismatch - STRONGLY recommend thread insert (Helicoil)")
    
    # Safety factor
    if 'margin' in results:
        margin = results['margin']
        if margin < 1.0:
            critical.append("🚨 CRITICAL: Bolt capacity < design load - DESIGN FAILS")
        elif margin < 1.2:
            warnings.append("⚠️ Low safety margin (<1.2) - increase bolt size or reduce load")
        elif margin < 1.5:
            warnings.append("⚠️ Marginal safety factor (<1.5) - not recommended for production")
    
    # Soft material specific
    if sigma_y_hole_MPa < 300:
        recommendations.append("🔧 Soft hole material detected - recommend Helicoil or similar insert")
        recommendations.append("🔧 Consider higher safety factor (n=2.5-3.0) for soft materials")
    
    # Vibration considerations
    if results.get('F_design_N', 0) > 5000:
        recommendations.append("🔩 High load application - use thread locking (Loctite) and Nord-Lock washers")
    
    return {
        'critical': critical,
        'warnings': warnings,
        'recommendations': recommendations,
        'overall_status': 'FAIL' if critical else ('WARNING' if warnings else 'GOOD')
    }


def fatigue_analysis(
    thread: MetricThread,
    F_mean_N: float,
    F_amplitude_N: float,
    sigma_y_bolt_MPa: float,
    cycles_expected: float = 1e6,
    surface_finish: str = 'machined'
) -> dict:
    """
    Simplified fatigue life estimation based on Goodman criterion.
    """
    # Endurance limit for steel (simplified)
    if sigma_y_bolt_MPa <= 1400:
        S_e_prime = 0.5 * sigma_y_bolt_MPa
    else:
        S_e_prime = 700  # MPa
    
    # Surface finish factor
    finish_factors = {
        'polished': 1.0,
        'ground': 0.88,
        'machined': 0.78,
        'hot_rolled': 0.52,
        'as_forged': 0.39
    }
    k_surface = finish_factors.get(surface_finish, 0.78)
    
    # Size factor (for threads)
    k_size = 0.85
    
    # Reliability factor (99% reliability)
    k_reliability = 0.81
    
    # Corrected endurance limit
    S_e = S_e_prime * k_surface * k_size * k_reliability
    
    # Stresses
    sigma_mean = F_mean_N / thread.At if thread.At > 0 else 0
    sigma_alt = F_amplitude_N / thread.At if thread.At > 0 else 0
    
    # Goodman criterion for safety factor
    if S_e > 0 and sigma_y_bolt_MPa > 0:
        n_fatigue = 1 / ((sigma_alt / S_e) + (sigma_mean / sigma_y_bolt_MPa))
    else:
        n_fatigue = 0
    
    # Estimated cycles to failure (Basquin equation - simplified)
    if n_fatigue >= 1:
        status = 'INFINITE_LIFE'
        cycles_to_failure = float('inf')
    else:
        status = 'FINITE_LIFE'
        # Rough estimate using modified Basquin
        if sigma_alt > 0:
            cycles_to_failure = (S_e / sigma_alt) ** 9
        else:
            cycles_to_failure = float('inf')
    
    return {
        'endurance_limit_MPa': S_e,
        'mean_stress_MPa': sigma_mean,
        'alternating_stress_MPa': sigma_alt,
        'fatigue_safety_factor': n_fatigue,
        'estimated_cycles': cycles_to_failure,
        'status': status,
        'safe_for_cycles': cycles_to_failure > cycles_expected if cycles_to_failure != float('inf') else True
    }


def helicoil_design(
    thread: MetricThread,
    sigma_y_hole_original_MPa: float,
    F_design_N: float,
    n_hole: float = 2.0,
    insert_material: str = 'stainless'
) -> dict:
    """
    Calculate thread insert (Helicoil) requirements.
    """
    insert_yields = {
        'stainless': 520,  # MPa (304 SS)
        'phosphor_bronze': 380,
        'inconel': 1000
    }
    
    sigma_y_insert = insert_yields.get(insert_material, 520)
    
    # Calculate engagement with insert (much shorter!)
    L_e_with_insert = required_engagement_for_design_load(
        thread,
        F_design_N=F_design_N,
        sigma_y_hole_MPa=sigma_y_insert,
        n_hole=n_hole
    )
    
    # Calculate without insert for comparison
    L_e_without_insert = required_engagement_for_design_load(
        thread,
        F_design_N=F_design_N,
        sigma_y_hole_MPa=sigma_y_hole_original_MPa,
        n_hole=n_hole
    )
    
    # Insert hole size (typically 8-10% oversize)
    d_drill_insert = thread.D * 1.085
    
    # Savings
    reduction_percent = ((L_e_without_insert - L_e_with_insert) / L_e_without_insert) * 100
    
    return {
        'insert_type': f"M{thread.D} Helicoil",
        'insert_material': insert_material,
        'insert_yield_MPa': sigma_y_insert,
        'engagement_with_insert_mm': L_e_with_insert,
        'engagement_without_insert_mm': L_e_without_insert,
        'engagement_reduction_percent': reduction_percent,
        'drill_size_mm': d_drill_insert,
        'tap_size': f"M{thread.D}×{thread.p} STI",
        'threads_engaged': L_e_with_insert / thread.p,
        'recommendation': 'HIGHLY RECOMMENDED' if sigma_y_hole_original_MPa < 300 else 'OPTIONAL'
    }


def check_standards_compliance(
    results: dict,
    thread: MetricThread,
    standard: str = 'VDI2230'
) -> dict:
    """
    Check compliance with engineering standards.
    """
    standards_requirements = {
        'VDI2230': {
            'name': 'VDI 2230 (Systematic calculation of bolted joints)',
            'min_safety_factor': 1.5,
            'min_threads_engaged': 6,
            'max_engagement_ratio': 2.5,
            'preload_range': (0.6, 0.9)
        },
        'ISO898': {
            'name': 'ISO 898-1 (Mechanical properties of fasteners)',
            'min_safety_factor': 1.5,
            'min_threads_engaged': 5,
            'thread_tolerance': '6g/6H'
        },
        'ASME_BPVC': {
            'name': 'ASME Boiler & Pressure Vessel Code',
            'min_safety_factor': 2.0,
            'min_threads_engaged': 8
        },
        'DIN': {
            'name': 'DIN 13 (ISO metric screw threads)',
            'min_safety_factor': 1.5,
            'min_threads_engaged': 5
        }
    }
    
    std = standards_requirements.get(standard, standards_requirements['VDI2230'])
    
    checks = []
    passes = 0
    fails = 0
    
    # Calculate effective safety factor
    if 'stress_analysis' in results:
        bolt_util = results['stress_analysis']['bolt_utilization']
        thread_util = results['stress_analysis']['thread_utilization']
        n_effective = min(1/bolt_util if bolt_util > 0 else 999, 
                         1/thread_util if thread_util > 0 else 999)
    elif 'margin' in results:
        n_effective = results['margin']
    else:
        n_effective = 2.0  # Assume default
    
    # Safety factor check
    if n_effective >= std['min_safety_factor']:
        checks.append(f"✅ Safety factor {n_effective:.2f} meets {standard} (≥{std['min_safety_factor']})")
        passes += 1
    else:
        checks.append(f"❌ Safety factor {n_effective:.2f} FAILS {standard} (≥{std['min_safety_factor']})")
        fails += 1
    
    # Threads engaged check
    if 'min_threads_engaged' in std:
        n_threads = results['n_threads']
        if n_threads >= std['min_threads_engaged']:
            checks.append(f"✅ {n_threads:.1f} threads meets requirement (≥{std['min_threads_engaged']})")
            passes += 1
        else:
            checks.append(f"❌ {n_threads:.1f} threads FAILS requirement (≥{std['min_threads_engaged']})")
            fails += 1
    
    # Engagement ratio check
    if 'max_engagement_ratio' in std:
        ratio = results['L_e_mm'] / thread.D
        if ratio <= std['max_engagement_ratio']:
            checks.append(f"✅ Engagement ratio {ratio:.2f}× diameter is practical (≤{std['max_engagement_ratio']})")
            passes += 1
        else:
            checks.append(f"⚠️ Engagement ratio {ratio:.2f}× diameter exceeds {std['max_engagement_ratio']}× (consider larger bolt)")
    
    return {
        'standard': std['name'],
        'checks': checks,
        'passes': passes,
        'fails': fails,
        'compliant': fails == 0
    }


# ============================================================================
# PHASE 2: HIGH VALUE FEATURES
# ============================================================================

def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between metric and imperial units.
    """
    conversions = {
        ('N', 'lbf'): 0.224809,
        ('lbf', 'N'): 4.44822,
        ('mm', 'inch'): 0.0393701,
        ('inch', 'mm'): 25.4,
        ('MPa', 'ksi'): 0.145038,
        ('ksi', 'MPa'): 6.89476,
        ('Nm', 'ft-lbf'): 0.737562,
        ('ft-lbf', 'Nm'): 1.35582,
        ('Nm', 'in-lbf'): 8.85075,
        ('in-lbf', 'Nm'): 0.112985,
        ('kg', 'lb'): 2.20462,
        ('lb', 'kg'): 0.453592,
    }
    
    key = (from_unit, to_unit)
    if key in conversions:
        return value * conversions[key]
    else:
        return value  # No conversion available


class LoadCase:
    """Represents a single load case for analysis."""
    def __init__(self, name: str, F_axial: float, F_shear: float = 0, 
                 M_bending: float = 0, frequency: Optional[float] = None, 
                 probability: float = 1.0):
        self.name = name
        self.F_axial = F_axial
        self.F_shear = F_shear
        self.M_bending = M_bending
        self.frequency = frequency
        self.probability = probability


def analyze_load_cases(
    thread: MetricThread,
    load_cases: List[LoadCase],
    sigma_y_bolt_MPa: float,
    sigma_y_hole_MPa: float,
    n_bolt: float = 2.0,
    n_hole: float = 2.0,
    bolt_spacing: float = 100.0
) -> dict:
    """
    Analyze multiple load cases and find the critical one.
    """
    results_list = []
    
    for case in load_cases:
        # Calculate equivalent axial load
        F_equiv = case.F_axial
        
        # Add bending contribution (simplified)
        if case.M_bending > 0 and bolt_spacing > 0:
            F_bending = (2 * case.M_bending) / bolt_spacing
            F_equiv += F_bending
        
        # Add shear contribution (very simplified)
        if case.F_shear > 0:
            F_equiv += case.F_shear * 0.3  # Rough approximation
        
        # Calculate engagement
        L_e = required_engagement_for_design_load(
            thread,
            F_design_N=F_equiv,
            sigma_y_hole_MPa=sigma_y_hole_MPa,
            n_hole=n_hole
        )
        
        F_bolt_cap = bolt_tensile_capacity(thread, sigma_y_bolt_MPa, n_bolt)
        
        result = {
            'load_case': case.name,
            'F_equivalent_N': F_equiv,
            'F_axial_N': case.F_axial,
            'F_shear_N': case.F_shear,
            'M_bending_Nm': case.M_bending,
            'L_e_mm': L_e,
            'threads_engaged': L_e / thread.p,
            'bolt_capacity_N': F_bolt_cap,
            'margin': F_bolt_cap / F_equiv if F_equiv > 0 else 999,
            'probability': case.probability,
            'frequency_Hz': case.frequency
        }
        
        results_list.append(result)
    
    # Find critical case (highest engagement required)
    critical_case = max(results_list, key=lambda x: x['L_e_mm'])
    
    return {
        'all_cases': results_list,
        'critical_case': critical_case,
        'design_for': critical_case['load_case'],
        'design_engagement_mm': critical_case['L_e_mm'],
        'num_cases_analyzed': len(load_cases)
    }


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='ISO metric thread engagement calculator'
    )
    subparsers = parser.add_subparsers(dest='mode', required=True)
    
    # LIST-MATERIALS mode
    subparsers.add_parser(
        'list-materials',
        help='List all available materials in the database',
    )

    # DESIGN mode
    p_design = subparsers.add_parser(
        'design',
        help='Size engagement for a given design tensile load',
    )
    p_design.add_argument(
        'designation',
        help='Thread designation, e.g. M8, M8x1.25',
    )
    p_design.add_argument(
        '--load',
        type=float,
        required=True,
        help='Design tensile load on bolt, in N',
    )
    p_design.add_argument(
        '--sigma-y-hole',
        type=float,
        required=True,
        help='Yield strength of tapped material (hole), in MPa',
    )
    p_design.add_argument(
        '--n-hole',
        type=float,
        default=2.0,
        help='Safety factor on shear for hole material (default: 2.0)',
    )
    p_design.add_argument(
        '--sigma-y-bolt',
        type=float,
        help='Yield strength of bolt material, in MPa (optional, for bolt check)',
    )
    p_design.add_argument(
        '--n-bolt',
        type=float,
        default=2.0,
        help='Safety factor on bolt tension (default: 2.0)',
    )
    p_design.add_argument(
        '--show-stress',
        action='store_true',
        help='Show detailed stress analysis',
    )

    # EQUAL-STRENGTH mode
    p_equal = subparsers.add_parser(
        'equal',
        help='Choose engagement so threads are as strong as the bolt',
    )
    p_equal.add_argument(
        'designation',
        help='Thread designation, e.g. M8, M8x1.25',
    )
    p_equal.add_argument(
        '--sigma-y-bolt',
        type=float,
        required=True,
        help='Yield strength of bolt material, in MPa',
    )
    p_equal.add_argument(
        '--n-bolt',
        type=float,
        default=2.0,
        help='Safety factor on bolt tension (default: 2.0)',
    )
    p_equal.add_argument(
        '--sigma-y-hole',
        type=float,
        required=True,
        help='Yield strength of tapped material (hole), in MPa',
    )
    p_equal.add_argument(
        '--n-hole',
        type=float,
        default=2.0,
        help='Safety factor on shear for hole material (default: 2.0)',
    )

    return parser


def main() -> None:
    parser = build_cli_parser()
    args = parser.parse_args()

    if args.mode == 'list-materials':
        list_available_materials()
    elif args.mode == 'design':
        engagement_summary_design(
            designation=args.designation,
            F_design_N=args.load,
            sigma_y_hole_MPa=args.sigma_y_hole,
            n_hole=args.n_hole,
            sigma_y_bolt_MPa=args.sigma_y_bolt,
            n_bolt=args.n_bolt,
            show_stress=args.show_stress,
        )
    elif args.mode == 'equal':
        engagement_summary_equal(
            designation=args.designation,
            sigma_y_bolt_MPa=args.sigma_y_bolt,
            sigma_y_hole_MPa=args.sigma_y_hole,
            n_bolt=args.n_bolt,
            n_hole=args.n_hole,
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
