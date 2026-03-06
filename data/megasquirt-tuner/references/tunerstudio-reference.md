# TunerStudio Reference Guide

## Connection Setup

### Serial Connection
- Default baud rate: 115200
- Select correct COM port (Windows) or /dev/tty* (Linux/Mac)
- USB-serial adapters often use FTDI or CH340 chips

### Bluetooth Connection
- Pair Megasquirt Bluetooth module
- Default PIN: typically 1234 or 0000
- Connection may be slower than USB

### Firmware Selection
- **MS1/Extra**: Original Megasquirt with enhanced code
- **MS2/Extra**: Improved processor, more features
- **MS3**: Latest generation, most capable
- Select matching firmware in project settings

## Main Interface Sections

### Tuning → Basic/Customize Tuning
Access primary tuning tables:
- VE Table (fuel)
- AFR Target Table
- Spark Table
- Idle Control
- Startup/Enrichment

### Tuning → Advanced
- Injection timing
- Boost control
- Launch/flat shift
- Nitrous control
- Variable cam timing

### Tuning → Algorithm
Switch between:
- **Speed Density**: MAP-based (most common)
- **Alpha-N**: TPS-based (individual throttle bodies)
- **Blended**: Combination approach

## Data Logging

### Creating Logs
1. Go to Datalog → Start Logging
2. Select save location
3. Drive/monitor system
4. Stop logging when complete

### Log Analysis
- Open in MegaLogViewer (separate tool)
- Or view in TunerStudio built-in viewer
- Filter by time range or conditions

### Key Logged Parameters
- rpm - Engine speed
- map - Manifold pressure (kPa)
- tps - Throttle position (%)
- clt - Coolant temperature (°C or °F)
- iat - Intake air temperature
- afr1 - Wideband O2 reading
- egoCorrection - Closed-loop correction %
- veCurr - Current VE value
- pulseWidth - Injector pulse width (ms)
- advance - Current spark advance (°)

## VE Analyze (Auto-Tune)

### Setup
1. Requires wideband O2 sensor
2. Go to Tuning → VE Analyze
3. Set target AFR table
4. Configure filter settings:
   - Minimum RPM
   - Minimum engine temperature
   - Maximum EGO correction (limits unsafe changes)

### Running VEAL
1. Start with engine warm
2. Enable VE Analyze → Live
3. Drive through various loads/RPM
4. VEAL automatically adjusts cells
5. Accept or reject changes
6. Save tune when satisfied

### Safety Settings
- Max negative correction: 15-20%
- Max positive correction: 15-20%
- Prevents extreme lean/rich conditions during tuning

## Table Editing

### Keyboard Shortcuts
- **Arrow keys**: Navigate cells
- **+ / -**: Increment/decrement selected cell
- **Ctrl+Click**: Select multiple cells
- **Ctrl+C / Ctrl+V**: Copy/paste
- **Ctrl+Z**: Undo

### Interpolation
- **Interpolate Horizontal**: Smooth row
- **Interpolate Vertical**: Smooth column
- **Smooth**: Apply to selected region

### Table Properties
- Right-click → Table Properties
- Set axis breakpoints
- Adjust table dimensions (if firmware supports)

## Calibration

### TPS Calibration
1. Tuning → Calibrations → TPS
2. Ensure throttle fully closed
3. Click "Get Current" for closed
4. Open throttle fully
5. Click "Get Current" for WOT
6. Accept calibration

### MAP Sensor Calibration
1. Tuning → Calibrations → MAP
2. Key on, engine off (reading = atmospheric)
3. Verify or set offset/scale
4. Common sensors: MPX4250 (250kPa), MPXH6400 (400kPa)

### Temperature Sensor Calibration
Select from preset curves:
- **CLT**: GM, Ford, Bosch common sensors
- **IAT**: Same options
- Or enter custom resistance/temperature pairs

### Wideband Calibration
Depends on controller type:
- **Innovate LC-1/LC-2**: 0-5V = 10-20 AFR
- **AEM UEGO**: 0-5V = 10-20 AFR  
- **14Point7**: Verify voltage range
- Set in Tuning → Calibrations → AFR

## Advanced Features

### Acceleration Wizard
Step-by-step setup for:
- TPS-based accel enrichment
- MAP-based accel enrichment
- Cold accel multiplier
- Decay rates

### Idle Control Wizard
Guides through:
- Valve type selection (PWM, stepper, on/off)
- PWM frequency
- PID tuning
- Target RPM table

### Ignition Wizard
For distributor or coil-on-plug:
- Trigger wheel setup
- Spark output settings
- Dwell time configuration

### Shift Light Settings
- RPM threshold
- Output pin assignment
- Hysteresis (prevent flicker)

## Dashboard Gauges

### Customizing Display
- Right-click → Add Gauge
- Drag to reposition
- Resize by dragging edges

### Available Gauge Types
- Numeric readout
- Horizontal/vertical bar
- Circular gauge
- LED indicator
- Graph (time-based)

### Alerts
Set warnings for:
- High coolant temp
- Lean AFR
- High MAP (overboost)
- Low oil pressure (if sensor connected)

## Controller Settings

### Engine Constants
Critical base settings:
- **Displacement**: Total engine size
- **Injector Flow**: Rated cc/min or lb/hr
- **Number of Cylinders**
- **Injector Opening Time**: Latency at 13.2V
- **Battery Voltage Correction**: PW adjustment for voltage

### Injection Settings
- **Staging**: Simultaneous, alternating, sequential
- **Injection Timing**: End of injection degrees BTDC
- **Dual Table**: Enable for independent bank control

### Ignition Settings
- **Ignition Type**: Basic trigger, wheel decoder, etc.
- **Trigger Angle**: Degrees BTDC for trigger event
- **Spark Output**: Going high, going low, inverted

## Troubleshooting Connection

### Cannot Connect
1. Verify correct COM port
2. Check baud rate matches firmware
3. Try different USB cable
4. Check device manager for driver issues
5. Verify Megasquirt is powered

### Intermittent Connection
- Poor grounding causing noise
- USB cable too long (keep under 10ft)
- Bluetooth interference
- Insufficient power supply

### Data Corruption
- Check grounds
- Shield signal wires
- Reduce serial cable length
- Update firmware

## Firmware Updates

### MS2/Extra
1. Download latest firmware from msextra.com
2. Tools → Upgrade Firmware
3. Select .S19 file
4. Follow prompts (do not interrupt)
5. Reload base tune after update

### MS3
Similar process, use MS3-specific firmware files
Always backup tune before updating

## Keyboard Commands During Runtime

- **Spacebar**: Pause datalog playback
- **F1**: Help (context-sensitive)
- **F5**: Refresh connection
- **Ctrl+S**: Save project
- **Ctrl+R**: Reset connection

## Project Files

### .MSQ Files
- Contains all tuning parameters
- Save versions: baseline, idle-tuned, drivable, etc.
- Can be shared between similar setups

### .MSL Files
- Datalog files
- Binary format, view in MegaLogViewer
- Can be exported to CSV

### Project Directory
Located in Documents/TunerStudioProjects/
Contains:
- Project settings
- Gauge layouts
- Log files
- Tune revisions

## ECU Profiles

### Loading a Profile
- File → Load Tune
- Select .MSQ file
- Sync to controller or save as new

### Saving a Profile
- File → Save Tune
- Choose location
- Use descriptive names with dates/versions

### Compare Tunes
- Tools → Compare MSQs
- Select two files
- Shows differences in tables/settings
- Useful for troubleshooting changes
