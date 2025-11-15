# Thread Engagement Calculator - Professional Edition v2.0

A comprehensive ISO metric thread engagement analysis tool for mechanical engineers. Calculate minimum thread engagement lengths, analyze stress distributions, prevent thread stripping failures, and generate professional reports with advanced fatigue analysis and standards compliance checking.

## 🚀 Features

### Core Calculations
- **Design Load Mode**: Calculate minimum engagement length for a specified applied load
- **Equal Strength Mode**: Determine engagement where thread strength matches bolt tensile capacity
- **Stress Analysis**: Detailed stress calculations including tensile, shear, and bearing stresses
- **Safety Factors**: Configurable safety factors for bolt tension and thread shear

### 🎯 Phase 1 Features (Core Enhancements)
- **⚙️ Installation Torque Calculation**: Recommended torque values with preload analysis (T = K × d × F)
- **📄 PDF Report Export**: Professional PDF reports with complete calculation documentation
- **📊 Visual Thread Diagrams**: Cross-section diagrams showing bolt/hole engagement
- **🎯 Design Recommendations**: Intelligent warnings and optimization suggestions
- **📜 Calculation History**: Session-based storage of last 20 calculations

### 🔬 Phase 2 Features (Advanced Analysis)
- **🔄 Fatigue Life Analysis**: Goodman criterion for cyclic loading with infinite/finite life prediction
- **🔩 Thread Insert (Helicoil) Analysis**: Evaluate benefits of thread inserts in soft materials
- **📋 Standards Compliance**: Verify VDI 2230, ISO 898-1, ASME BPVC requirements
- **🔄 Multiple Load Case Analysis**: Analyze several loading scenarios simultaneously
- **🔧 Unit Conversion System**: Convert between metric and imperial units

### 🎨 Phase 3 Features (User Experience)
- **🌙 Dark Mode**: Eye-friendly dark theme with persistent preference
- **📱 Mobile Responsive Design**: Full functionality on phones and tablets

### Materials Database
- 15+ common engineering materials pre-loaded
- Steel grades: 1018, 4140, 4340, 8.8, 10.9, 12.9
- Stainless steel: 304, 316, 17-4 PH
- Aluminum alloys: 6061-T6, 7075-T6, 2024-T3
- Cast iron, brass, and bronze
- Custom material input supported

### Thread Support
- ISO metric coarse pitch: M3 to M64
- Fine pitch threads for precision applications
- Automatic pitch detection or manual specification
- Comprehensive thread database

### Professional Features
- **Batch Analysis**: Analyze multiple thread sizes simultaneously
- **Web Interface**: Modern, responsive UI with tabbed navigation and dark mode
- **CLI Tool**: Command-line interface for scripting and automation
- **Export Options**: PDF reports, print results, or copy to clipboard
- **Material Selection**: Dropdown menus with common materials organized by category
- **Utilization Ratios**: See how close to limits your design operates

## 📋 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the repository**
   ```powershell
   cd "D:\Thread Engagement"
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install flask
   ```

## 🎯 Usage

### Web Application (Recommended)

1. **Start the server**
   ```powershell
   .venv\Scripts\activate
   python app.py
   ```

2. **Open browser**
   Navigate to: `http://127.0.0.1:5000`

3. **Use the interface**
   - Select thread size (e.g., M8, M10x1.5)
   - Choose calculation mode
   - Select materials from database or enter custom values
   - Click "Calculate Engagement"

### Command Line Interface

#### List Available Materials
```powershell
python thread_engagement.py list-materials
```

#### Design Load Mode
```powershell
python thread_engagement.py design M8 `
  --load 15000 `
  --sigma-y-hole 275 `
  --n-hole 2.0 `
  --sigma-y-bolt 800 `
  --n-bolt 2.0 `
  --show-stress
```

#### Equal Strength Mode
```powershell
python thread_engagement.py equal M8 `
  --sigma-y-bolt 800 `
  --n-bolt 2.0 `
  --sigma-y-hole 275 `
  --n-hole 2.0
```

### Python API

```python
from thread_engagement import (
    parse_metric_thread,
    required_engagement_for_design_load,
    bolt_tensile_capacity,
    calculate_stress_analysis
)

# Parse thread
thread = parse_metric_thread('M8')

# Calculate engagement
L_e = required_engagement_for_design_load(
    thread,
    F_design_N=15000,
    sigma_y_hole_MPa=275,
    n_hole=2.0
)

# Get stress analysis
stress = calculate_stress_analysis(
    thread,
    F_applied_N=15000,
    L_e_mm=L_e,
    sigma_y_bolt_MPa=800,
    sigma_y_hole_MPa=275
)

print(f"Required engagement: {L_e:.2f} mm")
print(f"Bolt utilization: {stress['bolt_utilization']*100:.1f}%")
```

## 📊 Batch Analysis

Analyze multiple thread sizes at once using the web interface:

1. Go to **Batch Analysis** tab
2. Enter thread sizes: `M6, M8, M10, M12, M16`
3. Set common parameters (load, materials, safety factors)
4. Click "Run Batch Analysis"
5. Compare results in a formatted table

## 🔧 VS Code Integration

### Debug Configurations

The project includes `.vscode/launch.json` with pre-configured debug profiles:

1. **Python: thread_engagement design M8** - Debug CLI in design mode
2. **Python: thread_engagement equal M8** - Debug CLI in equal strength mode
3. **Python: Flask app.py** - Debug web application

**To use:**
- Press `F5` or `Ctrl+Shift+D`
- Select a configuration
- Set breakpoints as needed

## 📐 Engineering Background

### Thread Engagement Formula

Minimum engagement length to prevent thread stripping:

```
L_e = F_design / (τ_allow × A_s_factor)
```

Where:
- `A_s_factor = 0.5625 × p × (D - 0.54127 × p)` (shear area per mm)
- `τ_allow = 0.62 × σ_y_hole / n_hole` (allowable shear stress)

### Tensile Stress Area

ISO metric bolt tensile stress area:

```
A_t = 0.7854 × (D - 0.9382 × p)²
```

### Safety Factor Guidelines

| Application | Recommended SF |
|-------------|----------------|
| Static loads, well-defined | 1.5 - 2.5 |
| Dynamic/cyclic loads | 2.5 - 4.0 |
| Critical applications | 3.0 - 5.0 |
| Shock/impact loads | 4.0 - 6.0 |

## ⚠️ Design Considerations

1. **Minimum Engagement**: Typically 1.5× bolt diameter
2. **Maximum Engagement**: Beyond 2.5× diameter, additional threads don't contribute proportionally
3. **Thread Quality**: Calculations assume properly manufactured threads (class 6g/6H or better)
4. **Material Ductility**: Formulas assume ductile materials; adjust for brittle materials
5. **Temperature**: Yield strengths are at room temperature; derate for elevated temperatures
6. **Coating Effects**: Thread coatings can affect effective engagement

## 📚 Standards Reference

- **ISO 68-1**: ISO general purpose metric screw threads
- **ISO 898-1**: Mechanical properties of fasteners - Bolts, screws and studs
- **ISO 965-1**: ISO general purpose metric screw threads - Tolerances
- **VDI 2230**: Systematic calculation of highly stressed bolted joints

## 🛠️ Advanced Features

### Custom Material Database

Add your own materials by editing `thread_engagement.py`:

```python
MATERIALS = {
    'My_Material': {
        'name': 'Custom Alloy',
        'sigma_y': 450,  # MPa
        'type': 'custom'
    },
    # ... existing materials
}
```

### Export Results

- **Print**: Use browser print function (Ctrl+P)
- **Copy**: Click "Copy to Clipboard" button
- **Programmatic**: Access return values from calculation functions

## 🐛 Troubleshooting

### Flask won't start
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill the process or use different port
# In app.py, change: app.run(debug=True, port=5001)
```

### Import errors
```powershell
# Ensure virtual environment is activated
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Calculation errors
- Verify thread designation format (e.g., M8 or M8x1.25)
- Check that material strengths are positive
- Ensure safety factors are > 1.0
- Verify applied loads are reasonable for thread size

## 🎓 Advanced Features Guide

### Installation Torque Calculation
Enable to calculate recommended installation torque based on desired preload:
- Uses formula: T = K × d × F (K = 0.15 for lubricated threads)
- Provides torque range (±20%)
- Converts to both Nm and ft-lbf
- Critical for proper bolt tensioning

### Fatigue Analysis
For cyclic loading applications:
1. Enable "Perform Fatigue Analysis"
2. Enter load amplitude (±variation from mean)
3. System applies Goodman criterion
4. Results show: INFINITE_LIFE or FINITE_LIFE
5. Fatigue safety factor provided

**When to use:** Vibration, repeated assembly, thermal cycling

### Helicoil Analysis
For soft hole materials (aluminum, brass):
- Analyzes thread insert benefits
- Calculates engagement reduction (typically 40-50%)
- Provides drill size requirements
- Recommends when highly beneficial

**Typical use:** Aluminum housings, repair applications

### Standards Compliance
Checks design against:
- **VDI 2230**: German standard for bolted joints
- **ISO 898-1**: Bolt property classes
- **ASME BPVC**: Pressure vessel code

Provides detailed compliance report with pass/fail for each criterion.

### PDF Export
Professional reports include:
- Input parameters table
- Calculation results
- Stress analysis breakdown
- Recommendations
- Date/time stamped

Perfect for design documentation and regulatory submissions.

## 📱 User Interface Features

### Dark Mode
- Click moon icon (🌙) in header to toggle
- Preference saved automatically
- Eye-friendly for extended use
- All UI elements fully themed

### Mobile Support
Fully responsive design works on:
- Smartphones (≤480px): Single column layout
- Tablets (481-768px): Adjusted grid
- Desktop (>768px): Full layout

Touch-optimized with appropriately sized buttons and inputs.

### Calculation History
- Automatically saves last 20 calculations
- View in History tab
- Shows timestamp, thread, load, mode
- Clear history option available
- Session-based (cleared on browser close)

## 📝 Version History

### v2.0 - Professional Edition (Current) - 2024
**Phase 1 - Core Enhancements:**
- Installation torque calculation with preload analysis
- PDF report export with professional formatting
- Visual thread engagement diagrams
- Intelligent design recommendations system
- Calculation history (last 20)

**Phase 2 - Advanced Analysis:**
- Fatigue life analysis (Goodman criterion)
- Thread insert (Helicoil) design analysis
- Standards compliance checking (VDI 2230, ISO 898-1, ASME BPVC)
- Multiple load case analysis API
- Metric/Imperial unit conversion system

**Phase 3 - User Experience:**
- Dark mode with persistent preference
- Mobile responsive design (phone/tablet support)
- Enhanced notifications and UI feedback
- Touch-optimized controls

**Dependencies:**
- Flask 3.0+ (web framework)
- ReportLab 4.0+ (PDF generation)
- Matplotlib 3.8+ (diagram visualization)
- Pillow 10.0+ (image processing)

### v1.5 - Enhanced Edition
- Added materials database with 15+ materials
- Implemented batch analysis mode
- Added detailed stress analysis
- Professional web UI with tabs
- Fine pitch thread support
- Export and print functionality
- Enhanced CLI with material listing

### v1.0 - Initial Release
- Basic design load and equal strength modes
- Simple web interface
- CLI tool
- ISO metric coarse threads

## 📚 Additional Documentation

- **FEATURES.md**: Complete feature guide with examples and formulas
- **EXAMPLES.md**: 10+ real-world engineering scenarios
- **QUICKSTART.md**: 5-minute setup and first calculation
- **TESTING_CHECKLIST.md**: Comprehensive testing guide for all features

## 📄 License

This tool is provided for engineering education and professional use. Always verify critical calculations with appropriate engineering references and standards.

**Disclaimer:** This calculator provides guidance based on standard engineering formulas and practices. For critical applications (safety, pressure vessels, aerospace), always have designs reviewed by a qualified professional engineer and validated against applicable codes.

## 👥 Contributing

Suggestions for improvements:
- Additional thread standards (UNC, UNF, BSW, etc.)
- Fatigue analysis capability
- Temperature derating factors
- PDF report generation
- Database import/export

## 📞 Support

For questions or issues:
1. Check this README
2. Review example calculations
3. Verify input parameters
4. Consult relevant engineering standards

---

**Developed for Mechanical Engineering Teams**  
*Ensuring safe and reliable threaded connections*
