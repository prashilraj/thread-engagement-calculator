# Thread Engagement Calculator - Examples

Practical examples for common engineering scenarios.

## Example 1: Steel Bolt in Aluminum Housing

**Scenario**: M8 steel bolt (Grade 8.8) threaded into 6061-T6 aluminum housing

**CLI Command**:
```powershell
python thread_engagement.py design M8 `
  --load 10000 `
  --sigma-y-bolt 640 `
  --sigma-y-hole 275 `
  --n-bolt 2.0 `
  --n-hole 2.5 `
  --show-stress
```

**Expected Result**:
- Minimum engagement: ~28-32 mm
- ~22-26 threads engaged
- Aluminum threads are the weak point (lower strength)

**Design Notes**:
- Higher safety factor on aluminum (2.5 vs 2.0)
- Consider thread inserts (Helicoil) for better durability
- Minimum practical engagement: 1.5 × 8mm = 12mm

---

## Example 2: High-Strength Bolt in Steel

**Scenario**: M12 Grade 10.9 bolt in 4140 steel housing, equal strength design

**CLI Command**:
```powershell
python thread_engagement.py equal M12 `
  --sigma-y-bolt 900 `
  --sigma-y-hole 415 `
  --n-bolt 2.0 `
  --n-hole 2.0
```

**Expected Result**:
- Required engagement: ~35-40 mm
- Bolt capacity: ~40-45 kN
- Threads will fail at same load as bolt

**Design Notes**:
- Equal strength ensures balanced failure mode
- Good for critical applications
- May need longer engagement due to high bolt strength

---

## Example 3: Stainless Steel Assembly

**Scenario**: M10 SS316 bolt in SS304 housing, moderate load

**CLI Command**:
```powershell
python thread_engagement.py design M10 `
  --load 8000 `
  --sigma-y-bolt 205 `
  --sigma-y-hole 215 `
  --n-bolt 2.5 `
  --n-hole 2.5 `
  --show-stress
```

**Expected Result**:
- Minimum engagement: ~20-25 mm
- Both materials have similar strength
- Conservative safety factors for corrosive environment

**Design Notes**:
- Stainless has lower strength than carbon steel
- Higher safety factors recommended for marine/chemical environments
- Consider galling prevention (anti-seize lubricant)

---

## Example 4: Batch Comparison

**Scenario**: Compare M6, M8, M10, M12 for 12kN load

**Web Interface**:
1. Go to "Batch Analysis" tab
2. Enter threads: `M6, M8, M10, M12`
3. Load: 12000 N
4. Bolt: 800 MPa (Grade 8.8)
5. Hole: 275 MPa (Al 6061-T6)
6. Safety factors: 2.0 / 2.5

**Expected Results Table**:
```
Thread    Pitch   At(mm²)  L_e(mm)   Threads   Bolt Cap(N)  Margin
M6        1.000   20.10    48.55     48.6      8040         0.67   ⚠️
M8        1.250   36.61    32.32     25.9      14644        1.22   ✓
M10       1.500   57.99    25.09     16.7      23196        1.93   ✓
M12       1.750   84.30    20.31     11.6      33720        2.81   ✓
```

**Analysis**:
- M6 is insufficient (margin < 1.0)
- M8 is minimum acceptable size
- M10 provides good balance
- M12 is conservative choice

---

## Example 5: Critical Application

**Scenario**: M16 in aerospace structure, cyclic loading

**Parameters**:
- Thread: M16 fine pitch (M16x1.5)
- Bolt: 7075-T6 aluminum (σ_y = 505 MPa)
- Hole: 7075-T6 aluminum (σ_y = 505 MPa)
- Design load: 25 kN
- Safety factors: 4.0 (high for fatigue)

**CLI Command**:
```powershell
python thread_engagement.py design M16x1.5 `
  --load 25000 `
  --sigma-y-bolt 505 `
  --sigma-y-hole 505 `
  --n-bolt 4.0 `
  --n-hole 4.0 `
  --show-stress
```

**Expected Result**:
- Minimum engagement: ~30-35 mm
- High safety factors account for fatigue
- Both materials same strength (homogeneous)

**Design Notes**:
- Fine pitch provides better fatigue resistance
- Consider surface treatments (anodizing)
- Regular inspection schedule required

---

## Example 6: Cast Iron Application

**Scenario**: M20 bolt securing machinery to cast iron base

**CLI Command**:
```powershell
python thread_engagement.py design M20 `
  --load 35000 `
  --sigma-y-bolt 640 `
  --sigma-y-hole 275 `
  --n-bolt 2.0 `
  --n-hole 3.0 `
  --show-stress
```

**Expected Result**:
- Minimum engagement: ~38-45 mm
- Cast iron requires higher safety factor (3.0)
- Brittle material consideration

**Design Notes**:
- Cast iron is brittle, avoid stress concentrations
- Use washers to distribute loads
- Through-bolts preferred over blind tapped holes
- Consider larger thread for cast iron

---

## Example 7: Minimum Engagement Check

**Scenario**: Quick check if existing M10 design is adequate

**Given**:
- Thread: M10 (coarse pitch 1.5mm)
- Existing engagement: 15mm (10 threads)
- Load: 15 kN
- Materials: Steel bolt in aluminum

**CLI Command**:
```powershell
python thread_engagement.py design M10 `
  --load 15000 `
  --sigma-y-bolt 800 `
  --sigma-y-hole 275 `
  --n-bolt 2.0 `
  --n-hole 2.5 `
  --show-stress
```

**If calculated L_e > 15mm**: ❌ Design is inadequate
**If calculated L_e ≤ 15mm**: ✓ Design is acceptable

---

## Example 8: Material Selection Impact

**Scenario**: Compare different hole materials for M8 bolt

**Batch Analysis Setup** (via web interface):
Run three separate calculations with same parameters except hole material:

1. **Aluminum 6061-T6**: σ_y = 275 MPa
2. **Cast Iron**: σ_y = 275 MPa  
3. **Steel 4140**: σ_y = 415 MPa

**Parameters**:
- Load: 10 kN
- Bolt: 800 MPa
- Safety factors: 2.0 / 2.5

**Expected Results**:
```
Material         L_e(mm)   Notes
6061-T6 Al       28.5      Standard aluminum
Cast Iron        28.5      Same strength but brittle
Steel 4140       18.9      33% shorter engagement
```

**Conclusion**: Higher strength hole material allows shorter engagement

---

## Example 9: Safety Factor Sensitivity

**Scenario**: See effect of safety factor on M12 design

**Test different n_hole values**:

```powershell
# Conservative (n=3.0)
python thread_engagement.py design M12 --load 20000 --sigma-y-hole 275 --n-hole 3.0

# Standard (n=2.0)  
python thread_engagement.py design M12 --load 20000 --sigma-y-hole 275 --n-hole 2.0

# Minimal (n=1.5)
python thread_engagement.py design M12 --load 20000 --sigma-y-hole 275 --n-hole 1.5
```

**Expected Results**:
```
Safety Factor    L_e(mm)   Change
3.0              45.2      +50%
2.0              30.1      baseline
1.5              22.6      -25%
```

**Note**: Engagement length is proportional to safety factor

---

## Example 10: Fine Pitch Advantage

**Scenario**: Compare coarse vs fine pitch M10

**Coarse Pitch (M10x1.5)**:
```powershell
python thread_engagement.py design M10 --load 15000 --sigma-y-hole 275 --n-hole 2.0
```

**Fine Pitch (M10x1.25)**:
```powershell
python thread_engagement.py design M10x1.25 --load 15000 --sigma-y-hole 275 --n-hole 2.0
```

**Expected Comparison**:
```
Pitch    L_e(mm)   Threads   Advantage
1.5      25.1      16.7      Standard, easier to tap
1.25     28.6      22.9      More threads, better fatigue
```

**When to use fine pitch**:
- Thin-walled parts
- Vibration/fatigue environments  
- Adjustment mechanisms
- When space allows extra length

---

## Quick Reference Table

Common bolt sizes with typical requirements (Steel in Aluminum, SF=2.0/2.5):

| Thread | Load (kN) | Min L_e (mm) | Min Threads |
|--------|-----------|--------------|-------------|
| M4     | 2         | 15           | 21          |
| M5     | 3         | 18           | 23          |
| M6     | 5         | 24           | 24          |
| M8     | 10        | 29           | 23          |
| M10    | 15        | 25           | 17          |
| M12    | 20        | 30           | 17          |
| M16    | 35        | 32           | 16          |
| M20    | 50        | 36           | 14          |

**Note**: Actual values depend on specific materials and safety factors. Always calculate for your specific application.

---

## Best Practices

1. **Always verify** calculations with hand calculations for critical applications
2. **Consider manufacturing** tolerances (Class 6H/6g minimum)
3. **Check minimum engagement** against 1.5× diameter rule
4. **Use thread inserts** for soft materials (aluminum, magnesium, plastics)
5. **Account for temperature** if above 200°C (derate material strength)
6. **Add margin** for shock/impact loading (increase safety factor)
7. **Document assumptions** in your design records
8. **Perform stress analysis** for loads near capacity
9. **Consider assembly** requirements (wrench clearance, etc.)
10. **Plan for inspection** - some engagement should be visible

---

*These examples are for educational purposes. Always consult relevant engineering standards and perform appropriate analysis for your specific application.*
