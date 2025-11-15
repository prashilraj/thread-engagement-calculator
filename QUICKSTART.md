# Quick Start Guide - Thread Engagement Calculator

## 🚀 5-Minute Setup

### Step 1: Open Terminal in VS Code
Press `` Ctrl+` `` or go to `Terminal → New Terminal`

### Step 2: Activate Virtual Environment
```powershell
.venv\Scripts\activate
```
You should see `(.venv)` in your terminal prompt.

### Step 3: Start the Web App
```powershell
python app.py
```

### Step 4: Open in Browser
The browser should open automatically, or go to: **http://127.0.0.1:5000**

---

## 📱 Using the Web Interface

### Calculator Tab (Main Feature)

1. **Thread Designation**: Enter thread size
   - Examples: `M8`, `M10x1.5`, `M12`
   - Coarse pitch auto-detected: `M8` → M8×1.25
   - Fine pitch explicit: `M10x1.25`

2. **Calculation Mode**:
   - **Design Load**: I have a load, need engagement length
   - **Equal Strength**: Make threads as strong as bolt

3. **Material Selection**:
   - Use dropdown for common materials
   - Or enter custom yield strength values
   - Bolt material: typically steel
   - Hole material: aluminum, steel, cast iron, etc.

4. **Safety Factors**:
   - **n_bolt = 2.0**: Standard for static loads
   - **n_hole = 2.5**: Higher for softer materials
   - Increase for critical/dynamic applications

5. **Design Load** (Design Mode only):
   - Enter applied axial force in Newtons
   - Example: 15000 N = 15 kN = 1.5 metric tons

6. **Show Stress Analysis**:
   - Check this box for detailed stress report
   - Shows bolt utilization percentage
   - Indicates if design is overstressed

7. **Click Calculate** 🔍

### Batch Analysis Tab

Perfect for comparing multiple sizes:

1. Enter threads: `M6, M8, M10, M12`
2. Set common parameters
3. Click "Run Batch Analysis"
4. Get comparison table instantly

**Use Cases**:
- Selecting optimal thread size
- Design trade studies
- Creating design tables

### Materials Database Tab

Reference for 15+ materials:
- Steel grades (1018, 4140, 8.8, 10.9, 12.9)
- Stainless steel (304, 316)
- Aluminum alloys (6061-T6, 7075-T6, 2024-T3)
- Cast iron, brass, bronze

### About Tab

Engineering background, formulas, and limitations.

---

## 🖥️ Command Line Interface

### Basic Commands

**List materials:**
```powershell
python thread_engagement.py list-materials
```

**Design mode:**
```powershell
python thread_engagement.py design M8 --load 15000 --sigma-y-hole 275 --sigma-y-bolt 800
```

**Equal strength mode:**
```powershell
python thread_engagement.py equal M10 --sigma-y-bolt 800 --sigma-y-hole 275
```

**With stress analysis:**
```powershell
python thread_engagement.py design M12 --load 20000 --sigma-y-hole 275 --sigma-y-bolt 800 --show-stress
```

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--load` | Design load in Newtons | Required |
| `--sigma-y-bolt` | Bolt yield strength (MPa) | Optional |
| `--sigma-y-hole` | Hole yield strength (MPa) | Required |
| `--n-bolt` | Safety factor for bolt | 2.0 |
| `--n-hole` | Safety factor for threads | 2.0 |
| `--show-stress` | Show stress analysis | Off |

---

## 💡 Common Scenarios

### Scenario 1: "I have a bolt and a load, how deep do I tap?"

**Use**: Design Load Mode

**Example**: M8 bolt, 12 kN load, aluminum housing
1. Select `M8`
2. Choose "Design Load"
3. Bolt material: `Grade 8.8 Bolt Steel` (640 MPa)
4. Hole material: `Aluminum 6061-T6` (275 MPa)
5. Design Load: `12000` N
6. Calculate → **Result**: ~27mm engagement needed

### Scenario 2: "What's the strongest way to use this thread?"

**Use**: Equal Strength Mode

**Example**: M10 bolt, want maximum capacity
1. Select `M10`
2. Choose "Equal Strength"
3. Select both materials
4. Calculate → **Result**: Required engagement and max load capacity

### Scenario 3: "Is my existing design safe?"

**Use**: Design Load Mode + Stress Analysis

**Steps**:
1. Enter your thread size
2. Enter actual applied load
3. Enter materials
4. ✅ Check "Show Detailed Stress Analysis"
5. Calculate

**Look for**:
- Bolt utilization < 100% ✓ Safe
- Thread utilization < 100% ✓ Safe
- Margin > 1.0 ✓ Adequate
- If any > 100% → ⚠️ Overstressed!

### Scenario 4: "Which thread size should I use?"

**Use**: Batch Analysis

**Steps**:
1. Go to "Batch Analysis" tab
2. Enter: `M6, M8, M10, M12, M16`
3. Enter your design load
4. Select materials
5. Compare results table
6. Pick size with margin > 1.5

---

## 🎯 Pro Tips

### 1. Material Selection
- **Steel bolt in aluminum**: Very common, use n_hole ≥ 2.5
- **Steel in steel**: Use equal strength mode
- **Stainless steel**: Lower strength than carbon steel
- **Cast iron**: Brittle, use higher safety factor

### 2. Safety Factors
```
Static, well-understood load:     n = 1.5 - 2.0
Standard engineering practice:    n = 2.0 - 2.5
Dynamic/cyclic loads:             n = 2.5 - 4.0
Critical applications:            n = 3.0 - 5.0
```

### 3. Practical Checks
- ✓ Engagement ≥ 1.5 × bolt diameter
- ✓ Engagement ≤ 2.5 × diameter (diminishing returns)
- ✓ Minimum 6-8 threads engaged
- ✓ Leave some threads visible for inspection

### 4. When to Use Fine Pitch
- Thin-walled parts
- Vibration/fatigue environments
- Adjustment mechanisms
- More threads = better fatigue life

### 5. Aluminum Considerations
- Always use thread inserts (Helicoil) for production
- Higher safety factors (2.5-3.0)
- Consider galling (use anti-seize)
- Torque values are lower than steel

---

## ⚠️ Important Notes

### What This Tool DOES:
✓ Calculate minimum thread engagement
✓ Compare thread sizes
✓ Analyze stress distribution
✓ Provide material database
✓ Apply safety factors

### What This Tool DOES NOT:
✗ Account for fatigue/cyclic loading
✗ Consider preload effects
✗ Model temperature effects
✗ Calculate torque requirements
✗ Replace engineering judgment

### Always Remember:
1. Verify critical calculations independently
2. Consult relevant standards (ISO 898, VDI 2230)
3. Consider manufacturing tolerances
4. Account for environmental factors
5. Document your assumptions

---

## 🐛 Troubleshooting

### "Thread designation not recognized"
- Use format: `M8` or `M8x1.25`
- Capital 'M' required
- Check pitch is valid for size

### "Invalid geometry or material properties"
- Ensure yield strengths > 0
- Check safety factors > 1.0
- Verify thread size is reasonable

### "Margin < 1.0" warning
- Your design is inadequate
- Increase thread size
- Use longer engagement
- Reduce applied load
- Check material selection

### Web app won't start
- Check port 5000 isn't in use
- Verify Flask is installed: `pip list | Select-String flask`
- Restart VS Code
- Reactivate virtual environment

---

## 📚 Next Steps

### Learn More:
- Read **README.md** for complete documentation
- Check **EXAMPLES.md** for 10+ real-world scenarios
- Review engineering standards (ISO 68-1, ISO 898-1)

### Extend the Tool:
- Add your materials to database
- Create custom reports
- Script batch analyses
- Integrate with CAD systems

### Share with Team:
- Export results (print or copy)
- Document calculation assumptions
- Create project-specific guidelines
- Establish standard safety factors

---

## 🎓 Training Checklist

Before using for production designs:

- [ ] Completed Example 1-3 from EXAMPLES.md
- [ ] Understand safety factor selection
- [ ] Can interpret stress analysis results
- [ ] Know when to use design vs equal strength mode
- [ ] Familiar with material database
- [ ] Understand tool limitations
- [ ] Know relevant standards for your industry
- [ ] Have validated against hand calculations

---

## 📞 Getting Help

1. **Check documentation**: README.md, EXAMPLES.md
2. **Review examples**: Try similar scenario
3. **Verify inputs**: Material properties, loads, thread designation
4. **Compare**: Hand calculations vs tool results
5. **Consult standards**: ISO 68-1, ISO 898-1, VDI 2230

---

**Ready to Start?**

```powershell
# Activate environment
.venv\Scripts\activate

# Start app
python app.py

# Open browser: http://127.0.0.1:5000
```

**First Calculation Suggestion:**
- Thread: `M8`
- Mode: Design Load
- Load: `10000` N
- Bolt: Grade 8.8 (640 MPa)
- Hole: Aluminum 6061-T6 (275 MPa)
- Click Calculate!

---

*Happy calculating! Build safe, reliable threaded connections.* 🔩✨
