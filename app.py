from flask import Flask, request, render_template_string, jsonify, send_file, session, make_response, redirect
from io import BytesIO
from datetime import datetime
import json
import base64
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from thread_engagement import (
    parse_metric_thread,
    required_engagement_for_design_load,
    required_engagement_for_equal_strength,
    bolt_tensile_capacity,
    calculate_stress_analysis,
    calculate_assembly_torque,
    generate_design_recommendations,
    fatigue_analysis,
    helicoil_design,
    check_standards_compliance,
    convert_units,
    LoadCase,
    analyze_load_cases,
    MATERIALS,
    COARSE_PITCH,
    FINE_PITCH,
)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_thread_diagram(d_nominal, L_e, pitch, designation):
    """Generate visual diagram of thread engagement."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Bolt body
    bolt_width = 40
    bolt_x = 50
    bolt_y_start = 30
    bolt_height = L_e * 2  # Scale for visibility
    
    # Draw bolt
    bolt = FancyBboxPatch((bolt_x, bolt_y_start), bolt_width, bolt_height,
                          boxstyle="round,pad=2", 
                          facecolor='#B0C4DE', edgecolor='#000080', linewidth=2)
    ax.add_patch(bolt)
    
    # Draw tapped hole
    hole_width = bolt_width + 10
    hole_x = bolt_x - 5
    hole = FancyBboxPatch((hole_x, bolt_y_start), hole_width, bolt_height,
                         boxstyle="round,pad=1",
                         facecolor='#F5DEB3', edgecolor='#8B4513', linewidth=2)
    ax.add_patch(hole)
    
    # Draw threads (stylized)
    num_threads = int(L_e / pitch)
    thread_spacing = bolt_height / max(num_threads, 1)
    
    for i in range(min(num_threads, 20)):  # Limit visual threads
        y = bolt_y_start + i * thread_spacing
        # Bolt threads
        ax.plot([bolt_x, bolt_x - 3], [y, y], 'b-', linewidth=1.5)
        ax.plot([bolt_x + bolt_width, bolt_x + bolt_width + 3], [y, y], 'b-', linewidth=1.5)
        
    # Dimension arrow
    arrow_x = bolt_x + bolt_width + 25
    ax.annotate('', xy=(arrow_x, bolt_y_start), xytext=(arrow_x, bolt_y_start + bolt_height),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(arrow_x + 5, bolt_y_start + bolt_height/2, 
            f'L_e = {L_e:.1f} mm\n({num_threads} threads)',
            verticalalignment='center', fontsize=11, color='red', weight='bold',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='red'))
    
    # Labels
    ax.text(bolt_x + bolt_width/2, bolt_y_start - 10, 'BOLT', 
            ha='center', fontsize=12, weight='bold', color='#000080')
    ax.text(hole_x - 15, bolt_y_start + bolt_height/2, 'TAPPED\nHOLE', 
            ha='center', fontsize=10, weight='bold', color='#8B4513')
    
    # Pitch indicator
    if num_threads > 1:
        y1 = bolt_y_start + thread_spacing
        y2 = bolt_y_start + 2 * thread_spacing
        ax.annotate('', xy=(bolt_x - 15, y1), xytext=(bolt_x - 15, y2),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
        ax.text(bolt_x - 20, (y1 + y2)/2, f'p={pitch}mm',
                verticalalignment='center', fontsize=9, color='green',
                rotation=90)
    
    ax.set_xlim(0, 150)
    ax.set_ylim(0, bolt_y_start + bolt_height + 30)
    ax.axis('off')
    ax.set_aspect('equal')
    
    plt.title(f'Thread Engagement Diagram: {designation}', fontsize=14, weight='bold', pad=20)
    
    # Convert to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return f"data:image/png;base64,{img_base64}"


def generate_pdf_report(data, results):
    """Generate detailed PDF calculation report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=20*mm, bottomMargin=20*mm)
    
    # Container for elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = styles['Title']
    elements.append(Paragraph("Thread Engagement Calculation Report", title_style))
    elements.append(Spacer(1, 10*mm))
    
    # Metadata
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Thread:</b> {data.get('designation', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Mode:</b> {data.get('mode', 'N/A').upper()}", styles['Normal']))
    elements.append(Spacer(1, 5*mm))
    
    # Input Parameters Table
    elements.append(Paragraph("<b>Input Parameters:</b>", styles['Heading2']))
    input_data = [
        ['Parameter', 'Value', 'Unit'],
        ['Thread Designation', data.get('designation', '-'), ''],
        ['Design Load', data.get('F_design', '-'), 'N'],
        ['Bolt Yield Strength', data.get('sigma_y_bolt', '-'), 'MPa'],
        ['Hole Yield Strength', data.get('sigma_y_hole', '-'), 'MPa'],
        ['Safety Factor (Bolt)', data.get('n_bolt', '-'), ''],
        ['Safety Factor (Hole)', data.get('n_hole', '-'), ''],
    ]
    
    input_table = Table(input_data, colWidths=[80*mm, 40*mm, 20*mm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 5*mm))
    
    # Results Table
    elements.append(Paragraph("<b>Calculation Results:</b>", styles['Heading2']))
    results_data = [
        ['Result', 'Value', 'Unit'],
        ['Required Engagement (L_e)', f"{results.get('L_e_mm', '-'):.2f}", 'mm'],
        ['Threads Engaged', f"{results.get('n_threads', '-'):.1f}", 'threads'],
    ]
    
    if 'F_bolt_allow_N' in results:
        results_data.append(['Bolt Capacity', f"{results['F_bolt_allow_N']:.0f}", 'N'])
        results_data.append(['Safety Margin', f"{results.get('margin', '-'):.2f}", 'x'])
    
    results_table = Table(results_data, colWidths=[80*mm, 40*mm, 20*mm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 5*mm))
    
    # Stress Analysis if available
    if 'stress_analysis' in results:
        stress = results['stress_analysis']
        elements.append(Paragraph("<b>Stress Analysis:</b>", styles['Heading2']))
        stress_data = [
            ['Stress Type', 'Value', 'Utilization'],
            ['Bolt Tensile', f"{stress['bolt_stress_MPa']:.1f} MPa", f"{stress['bolt_utilization']*100:.1f}%"],
            ['Thread Shear', f"{stress['thread_shear_stress_MPa']:.1f} MPa", f"{stress['thread_utilization']*100:.1f}%"],
            ['Bearing (approx)', f"{stress['bearing_stress_MPa']:.1f} MPa", '-'],
        ]
        
        stress_table = Table(stress_data, colWidths=[60*mm, 40*mm, 40*mm])
        stress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(stress_table)
        elements.append(Spacer(1, 5*mm))
    
    # Footer
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(
        "<i>Generated by Thread Engagement Calculator v2.0 - For engineering reference only. "
        "Verify with applicable standards and design codes.</i>",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def save_to_history(calc_data):
    """Save calculation to session history."""
    if 'calc_history' not in session:
        session['calc_history'] = []
    
    history = session['calc_history']
    history.append({
        'timestamp': datetime.now().isoformat(),
        'data': calc_data
    })
    
    # Keep only last 20 calculations
    session['calc_history'] = history[-20:]
    session.modified = True


TEMPLATE = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Thread Engagement Calculator - Professional Edition</title>
  <style>
    * { box-sizing: border-box; }
    body { 
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
      max-width: 1200px; 
      margin: 0 auto; 
      padding: 2rem;
      background: #f5f5f5;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 2rem;
      border-radius: 10px;
      margin-bottom: 2rem;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header h1 { margin: 0 0 0.5rem 0; }
    .header p { margin: 0; opacity: 0.9; }
    
    .tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 2rem;
    }
    .tab {
      padding: 1rem 2rem;
      background: white;
      border: none;
      border-radius: 8px 8px 0 0;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 500;
      transition: all 0.3s;
    }
    .tab:hover { background: #e0e0e0; }
    .tab.active { background: #667eea; color: white; }
    
    .tab-content {
      display: none;
      background: white;
      padding: 2rem;
      border-radius: 10px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .tab-content.active { display: block; }
    
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }
    .form-group {
      display: flex;
      flex-direction: column;
    }
    label { 
      font-weight: 600; 
      margin-bottom: 0.5rem;
      color: #333;
    }
    input, select { 
      padding: 0.75rem; 
      border: 2px solid #e0e0e0;
      border-radius: 5px;
      font-size: 1rem;
      transition: border-color 0.3s;
    }
    input:focus, select:focus { 
      outline: none;
      border-color: #667eea;
    }
    .radio-group {
      display: flex;
      gap: 1rem;
      margin-top: 0.5rem;
    }
    .radio-label {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: normal;
    }
    
    button { 
      padding: 1rem 2rem; 
      background: #667eea;
      color: white;
      border: none;
      border-radius: 5px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s;
    }
    button:hover { background: #5568d3; }
    button:active { transform: scale(0.98); }
    
    .result { 
      margin-top: 2rem; 
      padding: 1.5rem; 
      background: #f8f9fa;
      border-left: 4px solid #667eea;
      border-radius: 5px;
    }
    .result h3 { margin-top: 0; color: #667eea; }
    .result pre { 
      background: white;
      padding: 1rem;
      border-radius: 5px;
      overflow-x: auto;
      line-height: 1.6;
      font-family: 'Courier New', monospace;
      font-size: 0.95rem;
    }
    
    .result-section {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      margin-bottom: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .result-section h4 {
      margin-top: 0;
      margin-bottom: 1rem;
      color: #667eea;
      font-size: 1.1rem;
      border-bottom: 2px solid #e0e0e0;
      padding-bottom: 0.5rem;
    }
    
    .result-grid {
      display: grid;
      grid-template-columns: 200px 1fr;
      gap: 0.75rem;
      margin-bottom: 1rem;
    }
    
    .result-label {
      font-weight: 600;
      color: #555;
      display: flex;
      align-items: center;
    }
    
    .result-value {
      color: #333;
      font-family: 'Courier New', monospace;
      background: #f5f5f5;
      padding: 0.4rem 0.8rem;
      border-radius: 4px;
      display: flex;
      align-items: center;
    }
    
    .result-value.highlight {
      background: #e8f5e9;
      color: #2e7d32;
      font-weight: 600;
    }
    
    .result-value.warning {
      background: #fff3e0;
      color: #ef6c00;
      font-weight: 600;
    }
    
    .result-separator {
      grid-column: 1 / -1;
      border-top: 1px solid #e0e0e0;
      margin: 0.5rem 0;
    }
    .error { 
      background: #fff3cd;
      border-left: 4px solid #ffc107;
      padding: 1rem;
      border-radius: 5px;
      margin-top: 1rem;
    }
    .error h3 { color: #856404; margin-top: 0; }
    
    .info-box {
      background: #e3f2fd;
      padding: 1rem;
      border-radius: 5px;
      margin-bottom: 1.5rem;
      border-left: 4px solid #2196f3;
    }
    
    .material-helper {
      font-size: 0.9rem;
      color: #666;
      margin-top: 0.25rem;
    }
    
    .export-buttons {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
    }
    .export-btn {
      padding: 0.5rem 1rem;
      background: #28a745;
      font-size: 0.9rem;
    }
    .export-btn:hover { background: #218838; }
    
    /* Dark Mode Styles */
    body.dark-mode {
      background: #1a1a1a;
      color: #e0e0e0;
    }
    body.dark-mode .header {
      background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
    }
    body.dark-mode .tab {
      background: #2d2d30;
      color: #e0e0e0;
    }
    body.dark-mode .tab:hover {
      background: #3e3e42;
    }
    body.dark-mode .tab.active {
      background: #4a5568;
      color: white;
    }
    body.dark-mode .tab-content {
      background: #2d2d30;
      color: #e0e0e0;
    }
    body.dark-mode input,
    body.dark-mode select {
      background: #3c3c3c;
      color: #e0e0e0;
      border-color: #555;
    }
    body.dark-mode .info-box {
      background: #2d4a5e;
      border-left-color: #4a90e2;
    }
    body.dark-mode .result {
      background: #2a2a2a;
      border-left-color: #4a5568;
    }
    body.dark-mode .result pre {
      background: #1a1a1a;
      color: #e0e0e0;
    }
    body.dark-mode .result-section {
      background: #1e2a3a;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    body.dark-mode .result-section h4 {
      color: #b39ddb;
      border-bottom-color: #2d3e50;
    }
    body.dark-mode .result-label {
      color: #b0b0b0;
    }
    body.dark-mode .result-value {
      background: #0d1520;
      color: #e0e0e0;
    }
    body.dark-mode .result-value.highlight {
      background: #1b3a1b;
      color: #81c784;
    }
    body.dark-mode .result-value.warning {
      background: #3a2817;
      color: #ffb74d;
    }
    body.dark-mode .result-separator {
      border-top-color: #2d3e50;
    }
    body.dark-mode .material-helper {
      color: #999;
    }
    body.dark-mode label {
      color: #e0e0e0;
    }
    
    /* Recommendation boxes */
    .recommendations {
      margin-top: 1.5rem;
    }
    .recommendation-box {
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 5px;
      border-left: 4px solid;
    }
    .recommendation-box.critical {
      background: #ffebee;
      border-left-color: #c62828;
    }
    .recommendation-box.warning {
      background: #fff3e0;
      border-left-color: #ef6c00;
    }
    .recommendation-box.info {
      background: #e3f2fd;
      border-left-color: #1976d2;
    }
    body.dark-mode .recommendation-box.critical {
      background: #4a1f1f;
      color: #ffcdd2;
    }
    body.dark-mode .recommendation-box.warning {
      background: #4a3a1f;
      color: #ffe0b2;
    }
    body.dark-mode .recommendation-box.info {
      background: #1f3a4a;
      color: #bbdefb;
    }
    
    /* Diagram container */
    .diagram-container {
      margin: 1.5rem 0;
      text-align: center;
      background: white;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    body.dark-mode .diagram-container {
      background: #2a2a2a;
    }
    .diagram-container img {
      max-width: 100%;
      height: auto;
    }
    
    /* History panel */
    .history-item {
      padding: 0.75rem;
      margin: 0.5rem 0;
      background: #f8f9fa;
      border-left: 3px solid #667eea;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .history-item:hover {
      background: #e9ecef;
      transform: translateX(5px);
    }
    body.dark-mode .history-item {
      background: #2a2a2a;
      color: #e0e0e0;
    }
    body.dark-mode .history-item:hover {
      background: #3a3a3a;
    }
    
    /* Toggle switches */
    .toggle-container {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }
    .toggle-switch {
      position: relative;
      width: 60px;
      height: 30px;
    }
    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: .4s;
      border-radius: 30px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 22px;
      width: 22px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
    input:checked + .slider {
      background-color: #667eea;
    }
    input:checked + .slider:before {
      transform: translateX(30px);
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
      body { padding: 0.5rem; }
      .header { padding: 1rem; }
      .form-grid { grid-template-columns: 1fr; gap: 1rem; }
      .tabs { 
        flex-wrap: wrap;
        gap: 0.25rem;
      }
      .tab {
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        flex: 1 1 auto;
      }
      .tab-content { padding: 1rem; }
      .export-buttons {
        flex-direction: column;
      }
      .export-btn {
        width: 100%;
      }
      .radio-group {
        flex-direction: column;
        gap: 0.5rem;
      }
    }
    
    @media (max-width: 480px) {
      .header h1 {
        font-size: 1.5rem;
      }
      .header p {
        font-size: 0.9rem;
      }
      button {
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
      }
    }
  </style>
  <script>
    // Dark mode toggle
    function toggleDarkMode() {
      document.body.classList.toggle('dark-mode');
      const isDark = document.body.classList.contains('dark-mode');
      localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
      updateDarkModeIcon(isDark);
    }
    
    function updateDarkModeIcon(isDark) {
      const icon = document.getElementById('dark-mode-icon');
      if (icon) {
        icon.textContent = isDark ? '☀️' : '🌙';
      }
    }
    
    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
      document.body.classList.add('dark-mode');
      updateDarkModeIcon(true);
    }
    
    function showTab(tabId) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      document.getElementById('tab-' + tabId).classList.add('active');
      document.getElementById('content-' + tabId).classList.add('active');
      localStorage.setItem('activeTab', tabId);
    }
    
    // Restore active tab
    window.addEventListener('DOMContentLoaded', function() {
      const savedTab = localStorage.getItem('activeTab');
      if (savedTab && document.getElementById('tab-' + savedTab)) {
        showTab(savedTab);
      }
    });
    
    function updateMaterialValue(selectId, inputId) {
      const select = document.getElementById(selectId);
      const input = document.getElementById(inputId);
      if (select.value && select.value !== 'custom') {
        const materials = {{ materials_json|safe }};
        input.value = materials[select.value].sigma_y;
      }
    }
    
    function copyResults() {
      const resultText = document.querySelector('.result pre').innerText;
      navigator.clipboard.writeText(resultText).then(() => {
        showNotification('Results copied to clipboard!');
      });
    }
    
    function showNotification(message) {
      const notification = document.createElement('div');
      notification.textContent = message;
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
      `;
      document.body.appendChild(notification);
      setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
      }, 3000);
    }
    
    function convertUnits(value, fromUnit, toUnit) {
      const conversions = {
        'N-lbf': 0.224809,
        'lbf-N': 4.44822,
        'mm-inch': 0.0393701,
        'inch-mm': 25.4,
        'MPa-ksi': 0.145038,
        'ksi-MPa': 6.89476,
        'Nm-ftlbf': 0.737562,
        'ftlbf-Nm': 1.35582
      };
      const key = `${fromUnit}-${toUnit}`;
      return conversions[key] ? value * conversions[key] : value;
    }
    
    window.onload = function() {
      const modeRadios = document.getElementsByName('mode');
      const designLoadRow = document.getElementById('design-load-row');
      
      modeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
          designLoadRow.style.display = this.value === 'design' ? 'flex' : 'none';
        });
      });
      
      // Initial state
      const checkedMode = document.querySelector('input[name="mode"]:checked');
      if (checkedMode && checkedMode.value !== 'design') {
        designLoadRow.style.display = 'none';
      }
    };
  </script>
</head>
<body>
  <div class="header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1>🔩 Thread Engagement Calculator</h1>
        <p>Professional ISO Metric Thread Analysis Tool - v2.0 Professional Edition</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <button onclick="toggleDarkMode()" style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem;" title="Toggle Dark Mode">
          <span id="dark-mode-icon">🌙</span>
        </button>
      </div>
    </div>
  </div>
  
  <div class="tabs">
    <button class="tab active" id="tab-calculator" onclick="showTab('calculator')">📊 Calculator</button>
    <button class="tab" id="tab-batch" onclick="showTab('batch')">📋 Batch Analysis</button>
    <button class="tab" id="tab-history" onclick="showTab('history')">📜 History</button>
    <button class="tab" id="tab-materials" onclick="showTab('materials')">🔧 Materials</button>
    <button class="tab" id="tab-about" onclick="showTab('about')">ℹ️ About</button>
  </div>
  
  <!-- CALCULATOR TAB -->
  <div class="tab-content active" id="content-calculator">
    <div class="info-box">
      <strong>🚀 Quick Start:</strong> Select thread size, choose calculation mode, pick materials from database or enter custom values, then calculate!
    </div>

  <form method="post" action="/">
    <input type="hidden" name="tab" value="calculator">
    
    <div class="form-grid">
      <div class="form-group">
        <label>Thread Designation</label>
        <input name="designation" value="{{ request.form.get('designation', 'M8') }}" placeholder="e.g., M8, M10x1.5">
        <span class="material-helper">Available: M3 to M64 (coarse & fine pitch)</span>
      </div>
      
      <div class="form-group">
        <label>Calculation Mode</label>
        <div class="radio-group">
          <label class="radio-label">
            <input type="radio" name="mode" value="design"
              {% if request.form.get('mode', 'design') == 'design' %}checked{% endif %}>
            Design Load
          </label>
          <label class="radio-label">
            <input type="radio" name="mode" value="equal"
              {% if request.form.get('mode') == 'equal' %}checked{% endif %}>
            Equal Strength
          </label>
        </div>
      </div>
    </div>

    <h3 style="margin-top: 2rem; color: #667eea;">Material Selection</h3>
    <div class="form-grid">
      <div class="form-group">
        <label>Bolt Material</label>
        <select id="bolt-material-select" onchange="updateMaterialValue('bolt-material-select', 'sigma_y_bolt')">
          <option value="custom">Custom Value</option>
          {% for key, mat in materials.items() %}
            <option value="{{ key }}">{{ mat.name }} ({{ mat.sigma_y }} MPa)</option>
          {% endfor %}
        </select>
      </div>
      
      <div class="form-group">
        <label>Bolt Yield Strength σ_y (MPa)</label>
        <input type="number" id="sigma_y_bolt" name="sigma_y_bolt" step="0.1" 
               value="{{ request.form.get('sigma_y_bolt', '800') }}">
      </div>
      
      <div class="form-group">
        <label>Tapped Hole Material</label>
        <select id="hole-material-select" onchange="updateMaterialValue('hole-material-select', 'sigma_y_hole')">
          <option value="custom">Custom Value</option>
          {% for key, mat in materials.items() %}
            <option value="{{ key }}">{{ mat.name }} ({{ mat.sigma_y }} MPa)</option>
          {% endfor %}
        </select>
      </div>
      
      <div class="form-group">
        <label>Hole Yield Strength σ_y (MPa)</label>
        <input type="number" id="sigma_y_hole" name="sigma_y_hole" step="0.1"
               value="{{ request.form.get('sigma_y_hole', '275') }}">
      </div>
    </div>

    <h3 style="margin-top: 2rem; color: #667eea;">Safety Factors & Loading</h3>
    <div class="form-grid">
      <div class="form-group">
        <label>Safety Factor on Bolt (n_bolt)</label>
        <input type="number" name="n_bolt" step="0.1" value="{{ request.form.get('n_bolt', '2.0') }}">
        <span class="material-helper">Typical: 1.5-3.0</span>
      </div>
      
      <div class="form-group">
        <label>Safety Factor on Thread Shear (n_hole)</label>
        <input type="number" name="n_hole" step="0.1" value="{{ request.form.get('n_hole', '2.0') }}">
        <span class="material-helper">Typical: 2.0-3.0</span>
      </div>

      <div class="form-group" id="design-load-row">
        <label>Design Tensile Load (N)</label>
        <input type="number" name="F_design" step="1" value="{{ request.form.get('F_design', '15000') }}">
        <span class="material-helper">Applied axial force on bolt</span>
      </div>
    </div>

    <h3 style="margin-top: 2rem; color: #667eea;">⚙️ Advanced Options</h3>
    <div class="form-grid">
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="show_stress" {% if request.form.get('show_stress') %}checked{% endif %}>
          Show Detailed Stress Analysis
        </label>
      </div>
      
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="show_torque" {% if request.form.get('show_torque') %}checked{% endif %}>
          Calculate Installation Torque
        </label>
      </div>
      
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="show_recommendations" {% if request.form.get('show_recommendations') %}checked{% endif %}>
          Show Design Recommendations
        </label>
      </div>
      
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="show_diagram" {% if request.form.get('show_diagram') %}checked{% endif %}>
          Generate Thread Diagram
        </label>
      </div>
      
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="check_helicoil" {% if request.form.get('check_helicoil') %}checked{% endif %}>
          Evaluate Thread Insert (Helicoil)
        </label>
      </div>
      
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="check_standards" {% if request.form.get('check_standards') %}checked{% endif %}>
          Check Standards Compliance (VDI 2230)
        </label>
      </div>
      
      <div class="form-group">
        <label class="radio-label">
          <input type="checkbox" name="show_fatigue" {% if request.form.get('show_fatigue') %}checked{% endif %}>
          Perform Fatigue Analysis
        </label>
      </div>
      
      <div class="form-group" id="fatigue-params" style="display: {% if request.form.get('show_fatigue') %}flex{% else %}none{% endif %};">
        <label>Load Amplitude (N) for Fatigue</label>
        <input type="number" name="F_amplitude" step="1" value="{{ request.form.get('F_amplitude', '5000') }}">
        <span class="material-helper">Cyclic load variation (±amplitude)</span>
      </div>
    </div>

    <button type="submit">🔍 Calculate Engagement</button>
    <button type="submit" name="export_pdf" value="true" class="export-btn" style="margin-left: 1rem;">📄 Calculate & Export PDF</button>
  </form>

  {% if error %}
    <div class="error">
      <h3>⚠️ Error</h3>
      <p>{{ error }}</p>
    </div>
  {% endif %}

  {% if result %}
    <div class="result">
      <h3>✅ Calculation Results</h3>
      <div class="result-section">
        <pre>{{ result }}</pre>
      </div>
      
      {% if diagram %}
      <div class="diagram-container">
        <h4>Thread Engagement Diagram</h4>
        <img src="{{ diagram }}" alt="Thread Engagement Diagram">
      </div>
      {% endif %}
      
      {% if recommendations %}
      <div class="recommendations">
        <h4>🎯 Design Recommendations</h4>
        {% if recommendations.critical %}
        {% for msg in recommendations.critical %}
        <div class="recommendation-box critical">{{ msg }}</div>
        {% endfor %}
        {% endif %}
        
        {% if recommendations.warnings %}
        {% for msg in recommendations.warnings %}
        <div class="recommendation-box warning">{{ msg }}</div>
        {% endfor %}
        {% endif %}
        
        {% if recommendations.recommendations %}
        {% for msg in recommendations.recommendations %}
        <div class="recommendation-box info">{{ msg }}</div>
        {% endfor %}
        {% endif %}
      </div>
      {% endif %}
      
      {% if torque_specs %}
      <div style="margin-top: 1.5rem; padding: 1rem; background: #e8f5e9; border-radius: 5px;">
        <h4>🔧 Installation Torque Specifications</h4>
        <p><strong>Recommended Torque:</strong> {{ torque_specs.torque_recommended_Nm|round(1) }} Nm ({{ (torque_specs.torque_recommended_Nm * 0.737562)|round(1) }} ft-lbf)</p>
        <p><strong>Range:</strong> {{ torque_specs.torque_min_Nm|round(1) }} - {{ torque_specs.torque_max_Nm|round(1) }} Nm</p>
        <p><strong>Preload Force:</strong> {{ torque_specs.preload_force_N|round(0) }} N</p>
        <p style="font-size: 0.9rem; color: #666;">Note: Use calibrated torque wrench. Values for lubricated threads (friction coef = {{ torque_specs.friction_coefficient }}).</p>
      </div>
      {% endif %}
      
      {% if helicoil_info %}
      <div style="margin-top: 1.5rem; padding: 1rem; background: #fff3e0; border-radius: 5px;">
        <h4>🔩 Thread Insert (Helicoil) Analysis</h4>
        <p><strong>Insert Type:</strong> {{ helicoil_info.insert_type }} ({{ helicoil_info.insert_material }})</p>
        <p><strong>Engagement with Insert:</strong> {{ helicoil_info.engagement_with_insert_mm|round(2) }} mm ({{ helicoil_info.threads_engaged|round(1) }} threads)</p>
        <p><strong>Engagement Reduction:</strong> {{ helicoil_info.engagement_reduction_percent|round(1) }}% shorter</p>
        <p><strong>Drill Size:</strong> Ø{{ helicoil_info.drill_size_mm|round(2) }} mm</p>
        <p><strong>Recommendation:</strong> <span style="color: {% if helicoil_info.recommendation == 'HIGHLY RECOMMENDED' %}#d32f2f{% else %}#1976d2{% endif %}; font-weight: bold;">{{ helicoil_info.recommendation }}</span></p>
      </div>
      {% endif %}
      
      {% if standards_check %}
      <div style="margin-top: 1.5rem; padding: 1rem; background: #e3f2fd; border-radius: 5px;">
        <h4>📋 Standards Compliance: {{ standards_check.standard }}</h4>
        {% for check in standards_check.checks %}
        <p>{{ check }}</p>
        {% endfor %}
        <p style="margin-top: 0.5rem;"><strong>Overall:</strong> 
          <span style="color: {% if standards_check.compliant %}#4caf50{% else %}#f44336{% endif %}; font-weight: bold;">
            {% if standards_check.compliant %}✓ COMPLIANT{% else %}✗ NON-COMPLIANT{% endif %}
          </span>
        </p>
      </div>
      {% endif %}
      
      {% if fatigue_info %}
      <div style="margin-top: 1.5rem; padding: 1rem; background: #fce4ec; border-radius: 5px;">
        <h4>🔄 Fatigue Analysis</h4>
        <p><strong>Endurance Limit:</strong> {{ fatigue_info.endurance_limit_MPa|round(1) }} MPa</p>
        <p><strong>Mean Stress:</strong> {{ fatigue_info.mean_stress_MPa|round(1) }} MPa</p>
        <p><strong>Alternating Stress:</strong> {{ fatigue_info.alternating_stress_MPa|round(1) }} MPa</p>
        <p><strong>Fatigue Safety Factor:</strong> {{ fatigue_info.fatigue_safety_factor|round(2) }}</p>
        <p><strong>Status:</strong> <span style="color: {% if fatigue_info.status == 'INFINITE_LIFE' %}#4caf50{% else %}#ff9800{% endif %}; font-weight: bold;">{{ fatigue_info.status }}</span></p>
        {% if fatigue_info.status == 'FINITE_LIFE' %}
        <p><strong>Estimated Cycles to Failure:</strong> {{ "%.2e"|format(fatigue_info.estimated_cycles) }}</p>
        {% endif %}
      </div>
      {% endif %}
      
      <div class="export-buttons">
        <button class="export-btn" onclick="window.print()">🖨️ Print Results</button>
        <button class="export-btn" onclick="copyResults()">📋 Copy to Clipboard</button>
        <form method="post" action="/export-pdf" style="display: inline;">
          <input type="hidden" name="calc_data" value="{{ calc_data_json }}">
          <button type="submit" class="export-btn">📄 Export PDF</button>
        </form>
      </div>
    </div>
  {% endif %}
  </div>
  
  <!-- HISTORY TAB -->
  <div class="tab-content" id="content-history">
    <h2>📜 Calculation History</h2>
    <p>Recent calculations are stored in your session:</p>
    
    {% if history and history|length > 0 %}
    <div class="history-list">
      {% for item in history|reverse %}
      <div class="history-item">
        <strong>{{ item.timestamp|slice(0, 19) }}</strong><br>
        <span style="font-size: 0.9rem; color: #666;">
          Thread: {{ item.data.get('thread', 'N/A') }} | 
          Load: {{ item.data.get('load', 'N/A') }} N |
          Mode: {{ item.data.get('mode', 'N/A') }}
        </span>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="info-box">
      <p>No calculations yet. Complete a calculation to see it here!</p>
    </div>
    {% endif %}
    
    <button onclick="if(confirm('Clear all history?')) { window.location.href='/clear-history'; }" 
            style="margin-top: 1rem; background: #f44336;">
      🗑️ Clear History
    </button>
  </div>
  
  <!-- BATCH ANALYSIS TAB -->
  <div class="tab-content" id="content-batch">
    <div class="info-box">
      <strong>📊 Batch Mode:</strong> Analyze multiple thread sizes at once. Enter thread designations separated by commas.
    </div>
    
    <form method="post" action="/">
      <input type="hidden" name="tab" value="batch">
      
      <div class="form-group">
        <label>Thread Designations (comma-separated)</label>
        <input name="batch_threads" value="{{ request.form.get('batch_threads', 'M6, M8, M10, M12') }}" 
               placeholder="e.g., M6, M8, M10, M12">
      </div>
      
      <div class="form-grid" style="margin-top: 1.5rem;">
        <div class="form-group">
          <label>Design Load (N)</label>
          <input type="number" name="batch_load" step="1" value="{{ request.form.get('batch_load', '10000') }}">
        </div>
        
        <div class="form-group">
          <label>Bolt Material σ_y (MPa)</label>
          <input type="number" name="batch_sigma_bolt" step="0.1" value="{{ request.form.get('batch_sigma_bolt', '800') }}">
        </div>
        
        <div class="form-group">
          <label>Hole Material σ_y (MPa)</label>
          <input type="number" name="batch_sigma_hole" step="0.1" value="{{ request.form.get('batch_sigma_hole', '275') }}">
        </div>
        
        <div class="form-group">
          <label>Safety Factors (n_bolt / n_hole)</label>
          <div style="display: flex; gap: 0.5rem;">
            <input type="number" name="batch_n_bolt" step="0.1" value="{{ request.form.get('batch_n_bolt', '2.0') }}" style="width: 50%;">
            <input type="number" name="batch_n_hole" step="0.1" value="{{ request.form.get('batch_n_hole', '2.0') }}" style="width: 50%;">
          </div>
        </div>
      </div>
      
      <button type="submit" style="margin-top: 1rem;">📊 Run Batch Analysis</button>
    </form>
    
    {% if batch_result %}
    <div class="result">
      <h3>📊 Batch Analysis Results</h3>
      <pre>{{ batch_result }}</pre>
    </div>
    {% endif %}
  </div>
  
  <!-- MATERIALS DATABASE TAB -->
  <div class="tab-content" id="content-materials">
    <h2>Materials Database</h2>
    <p>Reference values for common engineering materials. Click material name to use in calculator.</p>
    
    {% for category in material_categories %}
      <h3 style="color: #667eea; margin-top: 2rem;">{{ category.name }}</h3>
      <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
        <thead>
          <tr style="background: #f0f0f0;">
            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Material</th>
            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Key</th>
            <th style="padding: 0.75rem; text-align: center; border: 1px solid #ddd;">Yield Strength (MPa)</th>
          </tr>
        </thead>
        <tbody>
          {% for mat in category.materials %}
          <tr>
            <td style="padding: 0.75rem; border: 1px solid #ddd;">{{ mat.name }}</td>
            <td style="padding: 0.75rem; border: 1px solid #ddd; font-family: monospace;">{{ mat.key }}</td>
            <td style="padding: 0.75rem; border: 1px solid #ddd; text-align: center; font-weight: 600;">{{ mat.sigma_y }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endfor %}
  </div>
  
  <!-- ABOUT TAB -->
  <div class="tab-content" id="content-about">
    <h2>About This Tool</h2>
    
    <h3 style="color: #667eea;">Purpose</h3>
    <p>This calculator determines the minimum thread engagement length required to prevent thread stripping in threaded connections. It's based on ISO metric thread standards and classical thread mechanics.</p>
    
    <h3 style="color: #667eea;">Calculation Modes</h3>
    <ul style="line-height: 1.8;">
      <li><strong>Design Load Mode:</strong> Calculate minimum engagement length for a specific applied load</li>
      <li><strong>Equal Strength Mode:</strong> Calculate engagement length where thread strength matches bolt tensile strength</li>
    </ul>
    
    <h3 style="color: #667eea;">Key Formulas</h3>
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
      <p><strong>Tensile Stress Area:</strong> A<sub>t</sub> = 0.7854 × (D - 0.9382p)²</p>
      <p><strong>Thread Shear Area:</strong> A<sub>s</sub> = 0.5625 × p × (D - 0.54127p) × L<sub>e</sub></p>
      <p><strong>Allowable Shear Stress:</strong> τ<sub>allow</sub> = 0.62 × σ<sub>y,hole</sub> / n<sub>hole</sub></p>
    </div>
    
    <h3 style="color: #667eea;">Safety Factors</h3>
    <p>Recommended safety factors depend on application:</p>
    <ul style="line-height: 1.8;">
      <li><strong>Static loading:</strong> n = 1.5 to 2.5</li>
      <li><strong>Dynamic/cyclic loading:</strong> n = 2.5 to 4.0</li>
      <li><strong>Critical applications:</strong> n = 3.0 to 5.0</li>
    </ul>
    
    <h3 style="color: #667eea;">Limitations</h3>
    <ul style="line-height: 1.8;">
      <li>Valid for ISO metric coarse and fine pitch threads</li>
      <li>Assumes properly tapped holes and good thread fit</li>
      <li>Does not account for preload, fatigue, or temperature effects</li>
      <li>Thread engagement should typically be at least 1.5× bolt diameter</li>
    </ul>
    
    <div class="info-box" style="margin-top: 2rem;">
      <strong>Version:</strong> 2.0 Professional Edition<br>
      <strong>Last Updated:</strong> {{ current_date }}<br>
      <strong>Thread Standards:</strong> ISO 68-1, ISO 898-1
    </div>
  </div>
  
  <script>
    function copyResults() {
      const resultText = document.querySelector('.result pre').innerText;
      navigator.clipboard.writeText(resultText).then(() => {
        showNotification('Results copied to clipboard!', 'success');
      });
    }
    
    function showNotification(message, type = 'info') {
      const notification = document.createElement('div');
      notification.className = `notification ${type}`;
      notification.textContent = message;
      notification.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 15px 25px; background: #4caf50; color: white; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); z-index: 10000; animation: slideIn 0.3s ease-out;';
      
      if (type === 'error') notification.style.background = '#f44336';
      if (type === 'warning') notification.style.background = '#ff9800';
      
      document.body.appendChild(notification);
      setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
      }, 3000);
    }
    
    // Dark mode toggle
    function toggleDarkMode() {
      document.body.classList.toggle('dark-mode');
      const isDark = document.body.classList.contains('dark-mode');
      localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
      
      const icon = document.querySelector('.dark-mode-toggle');
      icon.textContent = isDark ? '☀️' : '🌙';
    }
    
    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
      document.body.classList.add('dark-mode');
      const icon = document.querySelector('.dark-mode-toggle');
      if (icon) icon.textContent = '☀️';
    }
    
    // Fatigue analysis toggle
    const fatigueCheckbox = document.querySelector('input[name="show_fatigue"]');
    const fatigueParams = document.getElementById('fatigue-params');
    
    if (fatigueCheckbox && fatigueParams) {
      fatigueCheckbox.addEventListener('change', function() {
        fatigueParams.style.display = this.checked ? 'flex' : 'none';
      });
    }
    
    // Auto-select active tab based on form submission
    {% if request.form.get('tab') %}
    window.onload = function() {
      showTab('{{ request.form.get("tab") }}');
    };
    {% endif %}
  </script>
</body>
</html>
'''


@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """Export calculation as PDF."""
    try:
        calc_data = json.loads(request.form.get('calc_data', '{}'))
        
        # Create PDF buffer
        pdf_buffer = generate_pdf_report(calc_data, {
            'L_e_mm': calc_data.get('L_e'),
            'n_threads': calc_data.get('L_e', 0) / 1.25,  # Approximate
            'F_bolt_allow_N': calc_data.get('bolt_capacity'),
            'margin': calc_data.get('margin')
        })
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'thread_calc_{calc_data.get("thread", "report")}.pdf'
        )
    except Exception as e:
        return f"PDF generation error: {str(e)}", 500


@app.route('/clear-history')
def clear_history():
    """Clear calculation history."""
    session['calc_history'] = []
    session.modified = True
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    batch_result = None
    error = None
    
    # Organize materials by category
    material_categories = []
    categories = {}
    for key, data in MATERIALS.items():
        mat_type = data['type']
        if mat_type not in categories:
            categories[mat_type] = []
        categories[mat_type].append({'key': key, 'name': data['name'], 'sigma_y': data['sigma_y']})
    
    for cat_name, items in sorted(categories.items()):
        material_categories.append({
            'name': cat_name.replace('_', ' ').title(),
            'materials': items
        })

    # Initialize all template variables
    torque_specs = None
    recommendations = None
    diagram = None
    helicoil_info = None
    standards_check = None
    fatigue_info = None
    calc_data_json = '{}'
    
    if request.method == 'POST':
        tab = request.form.get('tab', 'calculator')
        
        # Handle batch analysis
        if tab == 'batch':
            try:
                threads_str = request.form.get('batch_threads', '')
                threads = [t.strip() for t in threads_str.split(',') if t.strip()]
                
                F_design = float(request.form.get('batch_load', '0') or '0')
                sigma_y_bolt = float(request.form.get('batch_sigma_bolt', '0') or '0')
                sigma_y_hole = float(request.form.get('batch_sigma_hole', '0') or '0')
                n_bolt = float(request.form.get('batch_n_bolt', '2.0') or '2.0')
                n_hole = float(request.form.get('batch_n_hole', '2.0') or '2.0')
                
                lines = []
                lines.append('=== BATCH ANALYSIS RESULTS ===')
                lines.append(f'Design Load: {F_design:.0f} N')
                lines.append(f'Bolt Material: σ_y = {sigma_y_bolt:.0f} MPa, n = {n_bolt:.2f}')
                lines.append(f'Hole Material: σ_y = {sigma_y_hole:.0f} MPa, n = {n_hole:.2f}')
                lines.append('')
                lines.append(f'{"Thread":<12} {"Pitch":<8} {"At(mm²)":<10} {"L_e(mm)":<10} {"Threads":<10} {"Bolt Cap(N)":<12} {"Margin":<8}')
                lines.append('-' * 90)
                
                for designation in threads:
                    try:
                        thread = parse_metric_thread(designation)
                        Le = required_engagement_for_design_load(
                            thread, F_design, sigma_y_hole, n_hole
                        )
                        F_bolt = bolt_tensile_capacity(thread, sigma_y_bolt, n_bolt)
                        margin = F_bolt / F_design if F_design > 0 else float('inf')
                        n_threads = Le / thread.p
                        
                        lines.append(
                            f'{thread.designation:<12} {thread.p:<8.3f} {thread.At:<10.2f} '
                            f'{Le:<10.2f} {n_threads:<10.1f} {F_bolt:<12.0f} {margin:<8.2f}'
                        )
                    except Exception as e:
                        lines.append(f'{designation:<12} ERROR: {str(e)}')
                
                batch_result = '\n'.join(lines)
                
            except Exception as e:
                error = f'Batch analysis error: {str(e)}'
        
        # Handle single calculation
        else:
            try:
                designation = request.form.get('designation', 'M8')
                mode = request.form.get('mode', 'design')
                show_stress = request.form.get('show_stress') == 'on'
                show_torque = request.form.get('show_torque') == 'on'
                show_recommendations = request.form.get('show_recommendations') == 'on'
                show_diagram = request.form.get('show_diagram') == 'on'
                check_helicoil = request.form.get('check_helicoil') == 'on'
                check_standards = request.form.get('check_standards') == 'on'
                show_fatigue = request.form.get('show_fatigue') == 'on'

                sigma_y_bolt = float(request.form.get('sigma_y_bolt', '0') or '0')
                sigma_y_hole = float(request.form.get('sigma_y_hole', '0') or '0')
                n_bolt = float(request.form.get('n_bolt', '2.0') or '2.0')
                n_hole = float(request.form.get('n_hole', '2.0') or '2.0')

                thread = parse_metric_thread(designation)

                if mode == 'design':
                    F_design = float(request.form.get('F_design', '0') or '0')
                    Le = required_engagement_for_design_load(
                        thread, F_design, sigma_y_hole, n_hole
                    )
                    F_bolt = bolt_tensile_capacity(thread, sigma_y_bolt, n_bolt) if sigma_y_bolt > 0 else None
                    
                    lines = []
                    lines.append(f'Thread: {thread.designation}')
                    lines.append(f'D = {thread.D:.3f} mm, p = {thread.p:.3f} mm, At = {thread.At:.2f} mm²')
                    lines.append('')
                    lines.append(f'Mode: DESIGN-LOAD')
                    lines.append(f'F_design = {F_design:.0f} N')
                    lines.append(f'σ_y,hole = {sigma_y_hole:.0f} MPa, n_hole = {n_hole:.2f}')
                    lines.append(f'→ L_e ≈ {Le:.2f} mm ({Le / thread.p:.1f} threads engaged)')
                    
                    if F_bolt is not None:
                        margin = F_bolt / F_design if F_design > 0 else float("inf")
                        lines.append('')
                        lines.append(f'Bolt: σ_y,bolt = {sigma_y_bolt:.0f} MPa, n_bolt = {n_bolt:.2f}')
                        lines.append(f'Bolt capacity F_allow ≈ {F_bolt:.0f} N')
                        lines.append(f'Margin bolt/design ≈ {margin:.2f}×')
                        
                        stress = None
                        if show_stress and F_design > 0:
                            stress = calculate_stress_analysis(thread, F_design, Le, sigma_y_bolt, sigma_y_hole)
                            lines.append('')
                            lines.append('=== DETAILED STRESS ANALYSIS ===')
                            lines.append(f'Bolt tensile stress:     {stress["bolt_stress_MPa"]:.1f} MPa ({stress["bolt_utilization"]*100:.1f}% of yield)')
                            lines.append(f'Thread shear stress:     {stress["thread_shear_stress_MPa"]:.1f} MPa ({stress["thread_utilization"]*100:.1f}% of allowable)')
                            lines.append(f'Bearing stress (approx): {stress["bearing_stress_MPa"]:.1f} MPa')
                            lines.append(f'Thread shear area:       {stress["shear_area_mm2"]:.2f} mm²')
                            
                            status = '✓ SAFE' if stress["bolt_utilization"] < 1.0 and stress["thread_utilization"] < 1.0 else '⚠ OVERSTRESSED'
                            lines.append(f'\nStatus: {status}')
                        
                        # Torque calculation
                        if show_torque and F_design > 0:
                            torque_specs = calculate_assembly_torque(thread, sigma_y_bolt, n_bolt, friction_coef=0.15)
                        
                        # Recommendations
                        if show_recommendations:
                            # Calculate stress if not already done
                            if stress is None and F_design > 0:
                                stress = calculate_stress_analysis(thread, F_design, Le, sigma_y_bolt, sigma_y_hole)
                            if stress:
                                # Build results dict for recommendations
                                results_dict = {
                                    'stress_analysis': stress,
                                    'L_e_mm': Le,
                                    'n_threads': Le / thread.p,
                                    'margin': margin,
                                    'F_design_N': F_design
                                }
                                recommendations = generate_design_recommendations(
                                    results_dict,
                                    thread,
                                    sigma_y_bolt,
                                    sigma_y_hole
                                )
                        
                        # Diagram
                        if show_diagram:
                            diagram = generate_thread_diagram(thread.D, Le, thread.p, thread.designation)
                        
                        # Helicoil analysis
                        if check_helicoil:
                            helicoil_info = helicoil_design(thread, sigma_y_hole, F_design, n_hole)
                        
                        # Standards compliance
                        if check_standards:
                            # Build results dict for standards check
                            if stress is None and F_design > 0:
                                stress = calculate_stress_analysis(thread, F_design, Le, sigma_y_bolt, sigma_y_hole)
                            results_dict = {
                                'stress_analysis': stress if stress else {},
                                'L_e_mm': Le,
                                'n_threads': Le / thread.p,
                                'margin': margin
                            }
                            standards_check = check_standards_compliance(
                                results_dict,
                                thread,
                                standard='VDI2230'
                            )
                        
                        # Fatigue analysis
                        if show_fatigue:
                            F_amplitude = float(request.form.get('F_amplitude', '0') or '0')
                            F_mean = F_design  # Use design load as mean
                            fatigue_info = fatigue_analysis(
                                thread, F_mean, F_amplitude, sigma_y_bolt,
                                cycles_expected=1e7,
                                surface_finish='machined'
                            )
                        
                        # Save to history
                        calc_data = {
                            'thread': designation,
                            'load': F_design,
                            'mode': 'design',
                            'L_e': Le,
                            'bolt_capacity': F_bolt,
                            'margin': margin
                        }
                        save_to_history(calc_data)
                        calc_data_json = json.dumps(calc_data)
                    
                    result = '\n'.join(lines)

                elif mode == 'equal':
                    Le, F_bolt = required_engagement_for_equal_strength(
                        thread, sigma_y_bolt, sigma_y_hole, n_bolt, n_hole
                    )
                    lines = []
                    lines.append(f'Thread: {thread.designation}')
                    lines.append(f'D = {thread.D:.3f} mm, p = {thread.p:.3f} mm, At = {thread.At:.2f} mm²')
                    lines.append('')
                    lines.append(f'Mode: EQUAL-STRENGTH (threads as strong as bolt)')
                    lines.append(f'Bolt: σ_y,bolt = {sigma_y_bolt:.0f} MPa, n_bolt = {n_bolt:.2f}')
                    lines.append(f'Hole: σ_y,hole = {sigma_y_hole:.0f} MPa, n_hole = {n_hole:.2f}')
                    lines.append(f'Bolt capacity F_allow ≈ {F_bolt:.0f} N')
                    lines.append(f'→ Required L_e ≈ {Le:.2f} mm ({Le / thread.p:.1f} threads engaged)')
                    
                    # Save to history
                    calc_data = {
                        'thread': designation,
                        'load': F_bolt,
                        'mode': 'equal',
                        'L_e': Le,
                        'bolt_capacity': F_bolt
                    }
                    save_to_history(calc_data)
                    calc_data_json = json.dumps(calc_data)
                    
                    result = '\n'.join(lines)

                else:
                    error = 'Unknown mode.'

            except Exception as e:
                error = str(e)
    
    # Get history from session
    history = session.get('calc_history', [])
    
    return render_template_string(
        TEMPLATE, 
        result=result, 
        batch_result=batch_result,
        error=error, 
        request=request,
        materials=MATERIALS,
        materials_json=json.dumps(MATERIALS),
        material_categories=material_categories,
        current_date=datetime.now().strftime('%Y-%m-%d'),
        history=history,
        torque_specs=torque_specs,
        recommendations=recommendations,
        diagram=diagram,
        helicoil_info=helicoil_info,
        standards_check=standards_check,
        fatigue_info=fatigue_info,
        calc_data_json=calc_data_json
    )


if __name__ == '__main__':
    app.run(debug=True)
