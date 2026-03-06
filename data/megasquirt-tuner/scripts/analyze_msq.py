#!/usr/bin/env python3
"""
MSQ Tune Analyzer for Megasquirt
Parses .msq files and provides critique, safety checks, and optimization suggestions.
"""

import sys
import re
import os
from pathlib import Path


def validate_filepath(filepath):
    """
    Validate file path for security.
    Prevents Local File Disclosure (LFD) vulnerabilities.
    """
    # Convert to Path object and get absolute path
    path = Path(filepath).resolve()
    
    # Check for path traversal attempts
    # The resolved path should not contain '..' components
    path_str = str(path)
    if '..' in filepath:
        return False, "Path contains directory traversal sequence ('..') - not allowed for security"
    
    # Enforce .msq extension only
    if not path_str.lower().endswith('.msq'):
        return False, f"File must have .msq extension. Got: {path.suffix if path.suffix else 'no extension'}"
    
    # Check if file exists
    if not path.exists():
        return False, f"File not found: {filepath}"
    
    # Ensure it's a regular file (not a directory, symlink, or special file)
    if not path.is_file():
        return False, f"Path is not a regular file: {filepath}"
    
    # Check for symlinks (prevent symlink attacks)
    if path.is_symlink():
        return False, "Symbolic links are not allowed for security reasons"
    
    # Verify we can read the file
    try:
        with open(path, 'r') as f:
            # Read first few bytes to verify it's text, not binary
            sample = f.read(1024)
            # Check for null bytes (indicates binary file)
            if '\x00' in sample:
                return False, "File appears to be binary, not a valid MSQ text file"
    except PermissionError:
        return False, f"Permission denied: cannot read {filepath}"
    except Exception as e:
        return False, f"Cannot read file: {e}"
    
    return True, str(path)


def parse_msq(filepath):
    """Parse MSQ file into sections and key-value pairs."""
    config = {}
    current_section = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                config[current_section] = {}
                continue
            
            # Key-value pair
            if '=' in line and current_section:
                key, value = line.split('=', 1)
                config[current_section][key.strip()] = value.strip()
    
    return config


def parse_table(data_str, expected_rows=None, expected_cols=None):
    """Parse a table from MSQ format (space-separated values, one row per line)."""
    rows = []
    for line in data_str.strip().split('\n'):
        values = [float(v) for v in line.strip().split() if v]
        if values:
            rows.append(values)
    return rows


def analyze_required_fuel(config):
    """Check required fuel settings."""
    issues = []
    suggestions = []
    
    req_fuel = config.get('req_fuel', {})
    
    # Get engine parameters
    nCylinders = int(req_fuel.get('nCylinders', '4'))
    
    # Look for required fuel in different possible locations
    req_fuel_ms = None
    for key in ['reqFuel', 'req_fuel', ' ReqFuel']:
        if key in req_fuel:
            try:
                req_fuel_ms = float(req_fuel[key])
                break
            except:
                pass
    
    if req_fuel_ms:
        # Rough sanity check: 1.5-15ms is typical range
        if req_fuel_ms < 1.0:
            issues.append(f"⚠️ Required fuel ({req_fuel_ms}ms) seems very low - verify injector size and displacement")
        elif req_fuel_ms > 20.0:
            issues.append(f"⚠️ Required fuel ({req_fuel_ms}ms) seems very high - verify injector size and displacement")
        else:
            suggestions.append(f"✓ Required fuel ({req_fuel_ms}ms) appears reasonable")
    
    return issues, suggestions


def analyze_ve_table(config):
    """Analyze VE table for anomalies."""
    issues = []
    suggestions = []
    
    ve_table = None
    ve_rpm = None
    ve_map = None
    
    # Try different section names where VE might be stored
    for section_name in config:
        if 'veTable' in section_name or 've table' in section_name.lower():
            section = config[section_name]
            if 'table' in section:
                ve_table = parse_table(section['table'])
            if 'rpmBins' in section:
                ve_rpm = [float(v) for v in section['rpmBins'].split()]
            if 'mapBins' in section or 'loadBins' in section:
                bins_key = 'mapBins' if 'mapBins' in section else 'loadBins'
                ve_map = [float(v) for v in section[bins_key].split()]
    
    if not ve_table:
        # Try alternate location
        if 'veTable1' in config:
            section = config['veTable1']
            if 'table' in section:
                ve_table = parse_table(section['table'])
    
    if ve_table:
        all_values = [v for row in ve_table for v in row]
        min_ve = min(all_values)
        max_ve = max(all_values)
        avg_ve = sum(all_values) / len(all_values)
        
        # Check for suspicious values
        if min_ve < 20:
            issues.append(f"⚠️ VE table has very low values ({min_ve:.1f}) - check for empty/untuned cells")
        if max_ve > 120:
            issues.append(f"⚠️ VE table has very high values ({max_ve:.1f}) - may be masking other issues")
        if min_ve > 80:
            issues.append(f"⚠️ Minimum VE ({min_ve:.1f}) seems high - verify engine efficiency assumptions")
        
        # Check for suspicious patterns
        suspicious_cells = 0
        for i, row in enumerate(ve_table):
            for j, val in enumerate(row):
                # Check for cliffs (big jumps between adjacent cells)
                if j > 0:
                    left = row[j-1]
                    if left > 0 and abs(val - left) / left > 0.3:  # 30% jump
                        suspicious_cells += 1
                if i > 0 and j < len(ve_table[i-1]):
                    above = ve_table[i-1][j]
                    if above > 0 and abs(val - above) / above > 0.3:
                        suspicious_cells += 1
        
        if suspicious_cells > 5:
            suggestions.append(f"📊 {suspicious_cells} cells have >30% jumps from neighbors - consider smoothing VE table")
        
        suggestions.append(f"✓ VE table range: {min_ve:.1f} - {max_ve:.1f} (avg: {avg_ve:.1f})")
    else:
        issues.append("⚠️ Could not find VE table - verify tune file format")
    
    return issues, suggestions


def analyze_afr_targets(config):
    """Check AFR target table for safety."""
    issues = []
    suggestions = []
    
    afr_table = None
    
    for section_name in config:
        if 'afrTable' in section_name or 'afrTarget' in section_name.lower():
            section = config[section_name]
            if 'table' in section:
                afr_table = parse_table(section['table'])
    
    if afr_table:
        all_values = [v for row in afr_table for v in row]
        min_afr = min(all_values)
        max_afr = max(all_values)
        
        # Safety checks
        if min_afr < 10.0:
            issues.append(f"🚨 DANGER: AFR target goes as lean as {min_afr:.1f}:1 - risk of engine damage!")
        elif min_afr < 11.0:
            issues.append(f"⚠️ Very lean AFR target ({min_afr:.1f}:1) at high load - engine damage risk")
        
        if max_afr > 16.0:
            suggestions.append(f"ℹ️ AFR target reaches {max_afr:.1f}:1 - verify this is intentional (may be for decel)")
        
        # Check WOT area (typically high load, higher RPM)
        if len(afr_table) > 0 and len(afr_table[0]) > 0:
            # Approximate WOT as rightmost columns, bottom rows
            wot_samples = []
            for i in range(max(0, len(afr_table)-3), len(afr_table)):
                for j in range(max(0, len(afr_table[i])-3), len(afr_table[i])):
                    wot_samples.append(afr_table[i][j])
            
            if wot_samples:
                avg_wot_afr = sum(wot_samples) / len(wot_samples)
                if avg_wot_afr > 13.5:
                    issues.append(f"⚠️ WOT AFR targets average {avg_wot_afr:.1f}:1 - consider enriching to 12.5-13.0 for safety")
                elif 12.0 <= avg_wot_afr <= 13.0:
                    suggestions.append(f"✓ WOT AFR targets look appropriate ({avg_wot_afr:.1f}:1 average)")
        
        suggestions.append(f"✓ AFR target range: {min_afr:.1f} - {max_afr:.1f}:1")
    
    return issues, suggestions


def analyze_spark_table(config):
    """Analyze ignition timing for safety."""
    issues = []
    suggestions = []
    
    spark_table = None
    
    for section_name in config:
        if 'sparkTable' in section_name or 'ignition' in section_name.lower():
            section = config[section_name]
            if 'table' in section:
                spark_table = parse_table(section['table'])
    
    if spark_table:
        all_values = [v for row in spark_table for v in row]
        min_adv = min(all_values)
        max_adv = max(all_values)
        
        # Safety checks
        if max_adv > 50:
            issues.append(f"🚨 Very high ignition advance ({max_adv:.1f}°) - severe knock risk!")
        elif max_adv > 45:
            issues.append(f"⚠️ High ignition advance ({max_adv:.1f}°) - verify on dyno with knock detection")
        
        if min_adv < -10:
            issues.append(f"⚠️ Very retarded timing ({min_adv:.1f}°) - may cause overheating")
        
        # Check for high load/high RPM area
        if len(spark_table) > 0 and len(spark_table[0]) > 0:
            high_load_samples = []
            for i in range(max(0, len(spark_table)-4), len(spark_table)):
                for j in range(max(0, len(spark_table[i])-4), len(spark_table[i])):
                    high_load_samples.append(spark_table[i][j])
            
            if high_load_samples:
                avg_high_load = sum(high_load_samples) / len(high_load_samples)
                if avg_high_load > 40:
                    issues.append(f"⚠️ High load timing averages {avg_high_load:.1f}° - aggressive, monitor for knock")
                elif avg_high_load < 15:
                    suggestions.append(f"ℹ️ Conservative high-load timing ({avg_high_load:.1f}°) - may be leaving power on table")
        
        suggestions.append(f"✓ Spark advance range: {min_adv:.1f}° - {max_adv:.1f}° BTDC")
    
    return issues, suggestions


def analyze_safety_limits(config):
    """Check rev limiter and overboost protection."""
    issues = []
    suggestions = []
    
    limits = config.get('revLimiter', {})
    
    # Rev limiter
    soft_limit = limits.get('softLimit', limits.get('SoftLimit', '0'))
    hard_limit = limits.get('hardLimit', limits.get('HardLimit', '0'))
    
    try:
        soft = int(soft_limit)
        hard = int(hard_limit)
        
        if soft == 0 and hard == 0:
            issues.append("🚨 NO REV LIMITER CONFIGURED - engine damage risk!")
        elif hard > 8000:
            issues.append(f"⚠️ High rev limit ({hard} RPM) - verify engine can safely rev this high")
        elif hard > 0 and soft > 0:
            if hard - soft < 200:
                suggestions.append("ℹ️ Soft and hard limit are close together - consider wider gap for smoother limiter")
            suggestions.append(f"✓ Rev limiter: soft {soft} RPM, hard {hard} RPM")
    except:
        pass
    
    # Overboost
    boost = config.get('boostControl', {})
    overboost = boost.get('overboost', boost.get('Overboost', '0'))
    try:
        ob = int(overboost)
        if ob == 0:
            suggestions.append("ℹ️ No overboost protection configured - consider adding for turbo setups")
        else:
            suggestions.append(f"✓ Overboost protection at {ob} kPa")
    except:
        pass
    
    return issues, suggestions


def analyze_cranking(config):
    """Check cranking pulse widths."""
    issues = []
    suggestions = []
    
    cranking = config.get('cranking', {})
    
    # Look for cranking pulse widths at different temps
    cold_pw = cranking.get('crankingPulseWidthCold', cranking.get('CrankingPulseWidthCold', '0'))
    hot_pw = cranking.get('crankingPulseWidthHot', cranking.get('CrankingPulseWidthHot', '0'))
    
    try:
        cold = float(cold_pw)
        hot = float(hot_pw)
        
        if cold == 0 and hot == 0:
            # Try alternate key names
            for key in cranking:
                if 'cranking' in key.lower() and 'pulse' in key.lower():
                    val = float(cranking[key])
                    if val > 20:
                        issues.append(f"⚠️ Cranking pulse width ({val}ms) seems very high")
                    elif val < 1:
                        issues.append(f"⚠️ Cranking pulse width ({val}ms) seems very low")
        else:
            if cold > 20:
                issues.append(f"⚠️ Cold cranking PW ({cold}ms) is high - may flood engine")
            elif cold < 3:
                issues.append(f"⚠️ Cold cranking PW ({cold}ms) is low - may not start in cold weather")
            
            if hot > 10:
                issues.append(f"⚠️ Hot cranking PW ({hot}ms) is high - risk of flooding")
            elif hot < 1:
                issues.append(f"⚠️ Hot cranking PW ({hot}ms) is very low")
            
            if cold > 0 and hot > 0:
                suggestions.append(f"✓ Cranking PW: {cold}ms cold, {hot}ms hot")
    except:
        pass
    
    return issues, suggestions


def analyze_injector_duty(config):
    """Estimate injector duty cycle headroom."""
    issues = []
    suggestions = []
    
    # This is a rough estimate based on required fuel and VE
    req_fuel = config.get('req_fuel', {})
    
    try:
        req_fuel_ms = None
        for key in req_fuel:
            if 'fuel' in key.lower() or 'reqfuel' in key.lower():
                try:
                    req_fuel_ms = float(req_fuel[key])
                    break
                except:
                    continue
        
        if req_fuel_ms:
            # Rough duty cycle at 100% VE, 100kPa
            # At 6000 RPM, injection period = 20ms (2 revs = 1 cycle)
            injection_period_6k = 20.0  # ms
            max_pw = req_fuel_ms * 1.2  # Rough max with some enrichment
            duty_at_6k = (max_pw / injection_period_6k) * 100
            
            if duty_at_6k > 90:
                issues.append(f"🚨 Estimated duty cycle ~{duty_at_6k:.0f}% - injectors may max out!")
            elif duty_at_6k > 80:
                issues.append(f"⚠️ Estimated duty cycle ~{duty_at_6k:.0f}% - limited headroom")
            elif duty_at_6k > 60:
                suggestions.append(f"✓ Estimated duty cycle ~{duty_at_6k:.0f}% - reasonable headroom")
            else:
                suggestions.append(f"✓ Estimated duty cycle ~{duty_at_6k:.0f}% - plenty of headroom")
    except:
        pass
    
    return issues, suggestions


def analyze_warmup(config):
    """Check warmup enrichment curve."""
    issues = []
    suggestions = []
    
    warmup = config.get('warmup', {})
    
    # Look for warmup bins
    wue_bins = None
    for key in warmup:
        if 'wue' in key.lower() or 'warmup' in key.lower() or 'enrich' in key.lower():
            if 'bins' in key.lower() or 'curve' in key.lower():
                try:
                    values = [float(v) for v in warmup[key].split()]
                    if len(values) > 5:
                        wue_bins = values
                        break
                except:
                    continue
    
    if wue_bins:
        max_wue = max(wue_bins)
        min_wue = min(wue_bins)
        
        if max_wue > 250:
            issues.append(f"⚠️ Max warmup enrichment ({max_wue:.0f}%) is very high - may flood on cold start")
        elif max_wue < 120:
            issues.append(f"⚠️ Max warmup enrichment ({max_wue:.0f}%) seems low - may run lean when cold")
        
        if min_wue > 105:
            issues.append(f"⚠️ Warmup doesn't taper to 100% (lowest is {min_wue:.0f}%) - may run rich when hot")
        
        suggestions.append(f"✓ Warmup enrichment range: {min_wue:.0f}% - {max_wue:.0f}%")
    
    return issues, suggestions


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_msq.py <tune_file.msq>")
        print("\nSecurity note: Only .msq files are accepted.")
        print("Path traversal sequences (../) are not allowed.")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Security validation
    is_valid, result = validate_filepath(filepath)
    if not is_valid:
        print(f"Error: {result}")
        sys.exit(1)
    
    # Use the validated, resolved path
    filepath = result
    
    print(f"\n{'='*60}")
    print(f"Megasquirt Tune Analysis: {filepath}")
    print(f"{'='*60}\n")
    
    config = parse_msq(filepath)
    
    all_issues = []
    all_suggestions = []
    
    # Run all analyses
    analyzers = [
        ("Required Fuel", analyze_required_fuel),
        ("VE Table", analyze_ve_table),
        ("AFR Targets", analyze_afr_targets),
        ("Ignition Timing", analyze_spark_table),
        ("Safety Limits", analyze_safety_limits),
        ("Cranking Settings", analyze_cranking),
        ("Injector Duty", analyze_injector_duty),
        ("Warmup Enrichment", analyze_warmup),
    ]
    
    for name, analyzer in analyzers:
        try:
            issues, suggestions = analyzer(config)
            if issues or suggestions:
                print(f"\n📋 {name}")
                print("-" * 40)
                for issue in issues:
                    print(f"  {issue}")
                for suggestion in suggestions:
                    print(f"  {suggestion}")
                all_issues.extend(issues)
                all_suggestions.extend(suggestions)
        except Exception as e:
            print(f"\n⚠️ Error analyzing {name}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    critical = [i for i in all_issues if '🚨' in i]
    warnings = [i for i in all_issues if '⚠️' in i]
    
    if critical:
        print(f"\n🚨 CRITICAL ISSUES: {len(critical)}")
        for c in critical:
            print(f"  {c}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS: {len(warnings)}")
    
    print(f"\n✓ Suggestions: {len([s for s in all_suggestions if '✓' in s])}")
    print(f"ℹ️  Notes: {len([s for s in all_suggestions if 'ℹ️' in s or '📊' in s])}")
    
    if not critical and not warnings:
        print("\n✅ No critical issues found!")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
