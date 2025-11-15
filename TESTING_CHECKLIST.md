# Testing Checklist - Thread Engagement Calculator v2.0

## 🧪 Comprehensive Testing Guide

This checklist ensures all features work correctly. Mark each test as you complete it.

---

## ✅ Phase 1 Features

### 1. Installation Torque Calculation
- [ ] **Test 1:** Basic torque calculation
  - Thread: M10
  - Load: 15,000 N
  - Bolt: Grade 10.9
  - Expected: ~22.5 Nm
  
- [ ] **Test 2:** Different thread sizes
  - M6: Should show lower torque
  - M16: Should show higher torque
  
- [ ] **Test 3:** Verify units
  - Check Nm to ft-lbf conversion
  - Verify torque range (±20%)

**Pass Criteria:** Torque values reasonable, range displayed, friction coefficient noted

---

### 2. PDF Export
- [ ] **Test 1:** Basic export
  - Complete calculation
  - Click "Export PDF"
  - Verify download starts
  
- [ ] **Test 2:** PDF content
  - Open generated PDF
  - Check all tables present
  - Verify formatting
  - Confirm date stamp
  
- [ ] **Test 3:** Different scenarios
  - Export with stress analysis
  - Export without stress analysis
  - Check file naming

**Pass Criteria:** PDF downloads, opens correctly, contains all data, professional formatting

---

### 3. Thread Diagrams
- [ ] **Test 1:** Diagram generation
  - Check "Generate Thread Diagram"
  - Run calculation
  - Verify image appears
  
- [ ] **Test 2:** Visual accuracy
  - Thread pitch proportional
  - Engagement length correct
  - Labels readable
  
- [ ] **Test 3:** Different threads
  - M6 vs M20 comparison
  - Fine vs coarse threads
  - Different engagement lengths

**Pass Criteria:** Diagram displays, scale accurate, professional appearance

---

### 4. Design Recommendations
- [ ] **Test 1:** Critical warnings
  - Use very high load (overstress)
  - Check for CRITICAL alerts
  - Red color coding
  
- [ ] **Test 2:** Normal warnings
  - Use 80% utilization
  - Check for WARNING alerts
  - Orange color coding
  
- [ ] **Test 3:** Good design
  - Use safe margins
  - Check for INFO messages
  - Blue color coding

**Pass Criteria:** Recommendations appear, color-coded correctly, actionable advice

---

### 5. Calculation History
- [ ] **Test 1:** History storage
  - Complete 3-5 calculations
  - Navigate to History tab
  - Verify all appear
  
- [ ] **Test 2:** History details
  - Check timestamps
  - Verify thread designations
  - Confirm load values
  
- [ ] **Test 3:** Clear history
  - Click "Clear History"
  - Verify list empties
  - Run new calc, verify it appears

**Pass Criteria:** History stores correctly, displays all data, clears properly

---

## 🔬 Phase 2 Features

### 6. Fatigue Analysis
- [ ] **Test 1:** Infinite life scenario
  - Thread: M10
  - Mean: 15,000 N
  - Amplitude: 3,000 N
  - Expected: INFINITE_LIFE
  
- [ ] **Test 2:** Finite life scenario
  - Use high amplitude (>50% mean)
  - Check for FINITE_LIFE status
  - Verify cycles estimate
  
- [ ] **Test 3:** Fatigue safety factor
  - Check FS > 1.5 for infinite
  - Verify mean/alt stress values
  - Confirm endurance limit

**Pass Criteria:** Fatigue status correct, safety factors calculated, cycles estimated when finite

---

### 7. Helicoil Analysis
- [ ] **Test 1:** Aluminum hole
  - Thread: M8
  - Hole: 6061-T6 Aluminum
  - Load: 10,000 N
  - Expected: HIGHLY RECOMMENDED
  
- [ ] **Test 2:** Steel hole
  - Thread: M8
  - Hole: Medium Carbon Steel
  - Load: 10,000 N
  - Expected: OPTIONAL or NOT NEEDED
  
- [ ] **Test 3:** Drill size verification
  - Check drill size ≈ D + 0.5mm
  - Verify engagement reduction
  - Confirm insert type

**Pass Criteria:** Recommendations appropriate for material, drill sizes correct, reduction % calculated

---

### 8. Standards Compliance
- [ ] **Test 1:** VDI 2230 check
  - Run typical calculation
  - Check compliance
  - Verify all criteria listed
  
- [ ] **Test 2:** Non-compliant design
  - Use very short engagement
  - Low safety factors
  - Check for violations
  
- [ ] **Test 3:** Overall status
  - Verify ✓ COMPLIANT or ✗ NON-COMPLIANT
  - Check individual checks
  - Confirm color coding

**Pass Criteria:** Standards checked correctly, violations flagged, overall status accurate

---

### 9. Multiple Load Cases
**(Python API only - test via command line)**

```python
# Test script
from thread_engagement import *

thread = parse_metric_thread("M10")
cases = [
    LoadCase("Preload", 5000, 0.5),
    LoadCase("Operating", 15000, 1.0),
    LoadCase("Peak", 22000, 0.8)
]

results = analyze_load_cases(thread, cases, 900, 400, 2.5, 2.0)
print(results)
```

- [ ] **Test 1:** Run script
- [ ] **Test 2:** Verify results for each case
- [ ] **Test 3:** Check critical load identification

**Pass Criteria:** All cases analyzed, critical case identified, combined results accurate

---

### 10. Unit Conversion
**(Python API only)**

```python
from thread_engagement import convert_units

# Test conversions
force_lbf = convert_units(15000, 'N', 'lbf')
length_in = convert_units(10, 'mm', 'inch')
stress_ksi = convert_units(400, 'MPa', 'ksi')
torque_ftlb = convert_units(22.5, 'Nm', 'ft-lbf')

print(f"Force: {force_lbf:.1f} lbf")
print(f"Length: {length_in:.3f} inch")
print(f"Stress: {stress_ksi:.1f} ksi")
print(f"Torque: {torque_ftlb:.1f} ft-lbf")
```

- [ ] **Test 1:** Run conversion script
- [ ] **Test 2:** Verify values (use online converter)
- [ ] **Test 3:** Test reverse conversions

**Pass Criteria:** All conversions accurate to ±0.1%, bidirectional works

---

## 🎨 Phase 3 Features

### 11. Dark Mode
- [ ] **Test 1:** Toggle functionality
  - Click dark mode button
  - Verify theme switches
  - Icon changes to sun
  
- [ ] **Test 2:** Persistence
  - Enable dark mode
  - Refresh page
  - Verify still dark
  
- [ ] **Test 3:** All elements
  - Check tabs
  - Check forms
  - Check results
  - Check buttons
  - All should be themed

**Pass Criteria:** Toggle works, preference saved, all UI elements themed properly

---

### 12. Mobile Responsive
- [ ] **Test 1:** Phone view (≤480px)
  - Open DevTools
  - Set to iPhone size
  - Check layout (single column)
  - Test all features
  
- [ ] **Test 2:** Tablet view (481-768px)
  - Set to iPad size
  - Check adjusted grid
  - Test navigation
  
- [ ] **Test 3:** Touch interactions
  - Buttons large enough
  - Forms usable
  - No horizontal scroll

**Pass Criteria:** All layouts work, no overflow, all features accessible on mobile

---

## 🔧 Core Functionality

### Basic Calculations
- [ ] **Test 1:** Design load mode
  - M8, 10,000 N, Steel/Aluminum
  - Verify engagement length
  - Check thread count
  
- [ ] **Test 2:** Equal strength mode
  - M10, Grade 8.8/Mild Steel
  - Verify calculated engagement
  - Check bolt capacity
  
- [ ] **Test 3:** Material selection
  - Test all 15+ materials
  - Verify dropdown works
  - Check σ_y updates

**Pass Criteria:** Calculations accurate, modes work, materials load correctly

---

### Batch Analysis
- [ ] **Test 1:** Multiple threads
  - Input: M6, M8, M10, M12
  - Load: 10,000 N
  - Verify table format
  
- [ ] **Test 2:** Error handling
  - Invalid thread (M999)
  - Check error message
  
- [ ] **Test 3:** Large batch
  - 10+ threads
  - Verify all processed
  - Check performance

**Pass Criteria:** Batch processes correctly, errors handled gracefully, table readable

---

### Stress Analysis
- [ ] **Test 1:** Detailed output
  - Enable stress analysis
  - Check all stress types
  - Verify utilization %
  
- [ ] **Test 2:** Safe design
  - Low load
  - Verify ✓ SAFE status
  
- [ ] **Test 3:** Overstressed
  - Very high load
  - Verify ⚠ OVERSTRESSED
  - Check which fails first

**Pass Criteria:** All stresses calculated, utilization accurate, status correct

---

## 🎯 Integration Tests

### Complete Workflow Test
- [ ] **Scenario:** High-performance assembly
  1. Thread: M12×1.75
  2. Bolt: Grade 12.9 (1080 MPa), n=2.5
  3. Hole: 7075-T6 Aluminum (503 MPa), n=2.0
  4. Load: 25,000 N
  5. Enable ALL options:
     - ✓ Stress analysis
     - ✓ Torque calculation
     - ✓ Recommendations
     - ✓ Diagram
     - ✓ Helicoil analysis
     - ✓ Standards check
     - ✓ Fatigue (amplitude: 8,000 N)
  
  **Expected Results:**
  - Engagement: ~18-20 mm
  - Bolt capacity: ~70,000 N
  - Margin: ~2.8×
  - Torque: ~65 Nm
  - Helicoil: HIGHLY RECOMMENDED
  - Fatigue: INFINITE_LIFE (FS > 1.5)
  - Standards: COMPLIANT
  - Recommendations: INFO level (good design)
  
  **Verification:**
  - [ ] All sections display
  - [ ] PDF export works
  - [ ] History saves
  - [ ] Diagram renders
  - [ ] No errors or warnings

---

### Edge Case Testing
- [ ] **Test 1:** Minimum values
  - Smallest thread (M3)
  - Minimum load (100 N)
  - Check calculations
  
- [ ] **Test 2:** Maximum values
  - Largest thread (M64)
  - High load (100,000 N)
  - Check performance
  
- [ ] **Test 3:** Invalid inputs
  - Negative load
  - Zero safety factor
  - Invalid thread designation
  - Verify error messages

**Pass Criteria:** Edge cases handled, errors graceful, no crashes

---

## 🌐 Browser Testing

### Chrome
- [ ] All features work
- [ ] Dark mode toggle
- [ ] PDF download
- [ ] Mobile view

### Firefox
- [ ] All features work
- [ ] Dark mode toggle
- [ ] PDF download
- [ ] Mobile view

### Safari (if available)
- [ ] All features work
- [ ] Dark mode toggle
- [ ] PDF download
- [ ] Mobile view

### Edge
- [ ] All features work
- [ ] Dark mode toggle
- [ ] PDF download
- [ ] Mobile view

---

## 📊 Performance Testing

### Load Testing
- [ ] 10 rapid calculations
- [ ] Large batch (20+ threads)
- [ ] PDF generation speed
- [ ] Page load time < 2s

### Memory Testing
- [ ] 50+ calculations (history limit)
- [ ] Multiple PDFs generated
- [ ] No memory leaks
- [ ] Session storage works

---

## 🐛 Bug Tracking

### Known Issues
*Document any bugs found during testing*

| # | Description | Severity | Status | Fix Date |
|---|-------------|----------|--------|----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## ✅ Final Checklist

Before marking complete:
- [ ] All Phase 1 features tested
- [ ] All Phase 2 features tested
- [ ] All Phase 3 features tested
- [ ] Core functionality verified
- [ ] Integration tests passed
- [ ] Edge cases handled
- [ ] Browser compatibility confirmed
- [ ] Performance acceptable
- [ ] No critical bugs
- [ ] Documentation reviewed

---

## 📝 Testing Notes

*Use this section for additional observations, suggestions, or issues*

```
Date: _______________
Tester: _______________

Notes:







```

---

**Testing Status:** ⏳ In Progress / ✅ Complete / ❌ Failed

**Overall Result:** ____________

**Tested by:** ____________  
**Date:** ____________  
**Version:** 2.0 Professional Edition
