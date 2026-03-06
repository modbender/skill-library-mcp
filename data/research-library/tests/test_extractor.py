"""
Comprehensive tests for the extraction pipeline.

Tests synthetic documents, measures performance, and reports results.
"""

import io
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import pytest

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reslib.extractor import (
    DocumentExtractor,
    ExtractionResult,
    FileType,
    ConfidenceScores,
    BatchExtractor,
    CodeExtractor,
    PDFExtractor,
    ImageExtractor,
    extract_file,
    get_supported_extensions,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def extractor():
    """Create a fresh DocumentExtractor instance."""
    return DocumentExtractor()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def performance_log():
    """Collect performance measurements."""
    measurements = []
    yield measurements
    
    # Print summary at end
    if measurements:
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        for m in measurements:
            status = "✅" if m['passed_target'] else "❌"
            print(f"{status} {m['test']}: {m['time_ms']:.2f}ms (target: <{m['target_ms']}ms)")
        print("=" * 60)


# ============================================================================
# Helper Functions
# ============================================================================

def create_synthetic_pdf(path: Path, pages: int = 3, topic: str = "servo motor control"):
    """Create a synthetic PDF for testing."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        
        content_per_page = [
            f"""
            Servo Motor Control Systems - Page 1
            
            Introduction to Servo Motors
            
            A servo motor is a rotary actuator that allows for precise control
            of angular position, velocity, and acceleration. Servo motors are
            used in robotics, CNC machinery, and automated manufacturing.
            
            Key Components:
            - DC or AC motor
            - Position sensor (encoder or potentiometer)
            - Control circuit (feedback loop)
            
            PWM Control Theory:
            The servo position is controlled by PWM signals with typical
            pulse widths of 1ms to 2ms within a 20ms period.
            """,
            f"""
            Servo Motor Control Systems - Page 2
            
            PID Control Implementation
            
            The PID controller calculates error as:
            e(t) = setpoint - measured_value
            
            Control output:
            u(t) = Kp*e(t) + Ki*integral(e) + Kd*de/dt
            
            Tuning Parameters:
            - Kp (Proportional): Response speed
            - Ki (Integral): Steady-state error
            - Kd (Derivative): Overshoot damping
            
            Arduino Code Example:
            void updateServo(int target) {{
                int error = target - currentPos;
                output = Kp * error + Ki * integral + Kd * derivative;
            }}
            """,
            f"""
            Servo Motor Control Systems - Page 3
            
            Applications and Specifications
            
            Common Applications:
            1. Robotic arms and manipulators
            2. CNC machine tool positioning
            3. Camera pan/tilt systems
            4. Antenna tracking systems
            
            Typical Specifications:
            - Torque: 1-50 kg-cm
            - Speed: 0.1-0.5 sec/60°
            - Voltage: 4.8V - 7.2V
            - Position accuracy: ±0.1°
            
            Safety Considerations:
            - Overcurrent protection
            - Thermal monitoring
            - Emergency stop circuits
            """,
        ]
        
        for i in range(min(pages, len(content_per_page))):
            if i > 0:
                c.showPage()
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, height - 72, f"Servo Motor Control - Page {i+1}")
            
            # Content
            c.setFont("Helvetica", 11)
            y = height - 120
            for line in content_per_page[i].strip().split('\n'):
                line = line.strip()
                if y < 72:
                    break
                c.drawString(72, y, line[:80])  # Truncate long lines
                y -= 14
        
        c.save()
        return True
    
    except ImportError:
        # reportlab not available, create minimal PDF manually
        # This is a valid minimal PDF
        pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 44 >> stream
BT /F1 12 Tf 100 700 Td (Servo Motor Control Test) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer << /Size 5 /Root 1 0 R >>
startxref
307
%%EOF"""
        path.write_bytes(pdf_content)
        return True


def create_synthetic_image(path: Path, with_text: bool = True):
    """Create a synthetic image for testing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image with white background
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        if with_text:
            # Add some text (barcode-like pattern)
            draw.rectangle([100, 100, 700, 200], outline='black', width=2)
            
            # Draw barcode-like lines
            x = 120
            for i in range(40):
                width = 3 if i % 3 == 0 else 1
                draw.rectangle([x, 110, x + width, 190], fill='black')
                x += 10 + (i % 5)
            
            # Add text below
            draw.text((100, 220), "BARCODE: ABC-123-XYZ", fill='black')
            draw.text((100, 260), "Product: Servo Motor SG90", fill='black')
            draw.text((100, 300), "Specifications:", fill='black')
            draw.text((120, 340), "- Torque: 1.8 kg-cm", fill='black')
            draw.text((120, 380), "- Speed: 0.1 sec/60 deg", fill='black')
            draw.text((120, 420), "- Voltage: 4.8-6V", fill='black')
        
        # Add EXIF-like metadata via PNG info
        img.save(path, 'PNG')
        return True
    
    except ImportError:
        # PIL not available, create minimal valid PNG
        # 1x1 white pixel PNG
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        path.write_bytes(png_data)
        return True


def create_python_file(path: Path):
    """Create a synthetic Python file for testing."""
    content = '''"""
Servo Motor Controller Module

This module provides classes for controlling servo motors
using PWM signals and PID feedback control.

Author: Test Author
Version: 1.0.0
"""

import time
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ServoConfig:
    """Configuration for a servo motor."""
    min_pulse: int = 1000  # microseconds
    max_pulse: int = 2000  # microseconds
    min_angle: float = 0.0
    max_angle: float = 180.0


class PIDController:
    """
    PID controller for servo position control.
    
    Implements a standard PID control loop with
    anti-windup protection.
    """
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05):
        """
        Initialize PID controller.
        
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.time()
    
    def update(self, setpoint: float, measured: float) -> float:
        """
        Calculate PID output.
        
        Args:
            setpoint: Desired value
            measured: Current measured value
            
        Returns:
            Control output value
        """
        current_time = time.time()
        dt = current_time - self._last_time
        
        error = setpoint - measured
        
        # Proportional
        p_term = self.kp * error
        
        # Integral with anti-windup
        self._integral += error * dt
        self._integral = max(-100, min(100, self._integral))
        i_term = self.ki * self._integral
        
        # Derivative
        derivative = (error - self._last_error) / dt if dt > 0 else 0
        d_term = self.kd * derivative
        
        self._last_error = error
        self._last_time = current_time
        
        return p_term + i_term + d_term
    
    def reset(self):
        """Reset controller state."""
        self._integral = 0.0
        self._last_error = 0.0


class ServoMotor:
    """
    Servo motor controller class.
    
    Provides methods for position control with optional
    PID feedback.
    """
    
    def __init__(self, pin: int, config: Optional[ServoConfig] = None):
        """
        Initialize servo motor.
        
        Args:
            pin: GPIO pin number
            config: Servo configuration (uses defaults if None)
        """
        self.pin = pin
        self.config = config or ServoConfig()
        self._current_angle = 0.0
        self._pid: Optional[PIDController] = None
    
    def set_angle(self, angle: float) -> None:
        """
        Set servo to specified angle.
        
        Args:
            angle: Target angle in degrees
        """
        # Clamp angle to valid range
        angle = max(self.config.min_angle, min(self.config.max_angle, angle))
        
        # Calculate pulse width
        pulse = self._angle_to_pulse(angle)
        
        # TODO: Actually send PWM signal
        self._current_angle = angle
    
    def get_angle(self) -> float:
        """Get current servo angle."""
        return self._current_angle
    
    def _angle_to_pulse(self, angle: float) -> int:
        """Convert angle to pulse width in microseconds."""
        angle_range = self.config.max_angle - self.config.min_angle
        pulse_range = self.config.max_pulse - self.config.min_pulse
        
        normalized = (angle - self.config.min_angle) / angle_range
        pulse = self.config.min_pulse + (normalized * pulse_range)
        
        return int(pulse)
    
    def enable_pid(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05):
        """Enable PID control for the servo."""
        self._pid = PIDController(kp, ki, kd)


def calculate_trajectory(
    start: Tuple[float, float, float],
    end: Tuple[float, float, float],
    steps: int = 100
) -> list:
    """
    Calculate smooth trajectory between two points.
    
    Uses cubic interpolation for smooth motion.
    
    Args:
        start: Starting position (x, y, z)
        end: Ending position (x, y, z)
        steps: Number of interpolation steps
        
    Returns:
        List of (x, y, z) tuples representing the trajectory
    """
    trajectory = []
    
    for i in range(steps + 1):
        t = i / steps
        # Cubic ease-in-out
        t = t * t * (3 - 2 * t)
        
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        z = start[2] + (end[2] - start[2]) * t
        
        trajectory.append((x, y, z))
    
    return trajectory


if __name__ == '__main__':
    # Test code
    servo = ServoMotor(pin=18)
    servo.set_angle(90)
    print(f"Servo angle: {servo.get_angle()}")
'''
    path.write_text(content)


def create_gcode_file(path: Path):
    """Create a synthetic G-code file for testing."""
    content = '''; G-code for servo bracket milling
; Material: Aluminum 6061
; Tool: 6mm end mill
; Generated: 2024-01-15

G21 ; Set units to millimeters
G90 ; Absolute positioning
G17 ; XY plane selection

; Home and setup
G28 ; Home all axes
M6 T1 ; Tool change to tool 1
S12000 M3 ; Spindle on at 12000 RPM

; Move to start position
G0 X0 Y0 Z10 ; Rapid to start
G0 X10 Y10 ; Position over workpiece

; Rough cut - servo mounting holes
G1 Z-2 F500 ; Plunge cut
G1 X50 F1000 ; Linear move
G2 X60 Y20 I10 J0 ; Arc CW
G1 Y50
G3 X50 Y60 I-10 J0 ; Arc CCW
G1 X10
G1 Y10

; Second pass - finishing
G1 Z-4 F300
G1 X50 F800
G2 X60 Y20 I10 J0
G1 Y50
G3 X50 Y60 I-10 J0
G1 X10
G1 Y10

; Drill mounting holes
G0 Z5 ; Retract
G0 X15 Y15 ; Position for hole 1
G1 Z-5 F200 ; Drill
G0 Z5
G0 X45 Y15 ; Position for hole 2
G1 Z-5 F200
G0 Z5
G0 X45 Y45 ; Position for hole 3
G1 Z-5 F200
G0 Z5
G0 X15 Y45 ; Position for hole 4
G1 Z-5 F200
G0 Z5

; End program
M5 ; Spindle off
M9 ; Coolant off
G28 ; Return to home
M30 ; Program end
'''
    path.write_text(content)


def create_cpp_file(path: Path):
    """Create a synthetic C++/Arduino file for testing."""
    content = '''/*
 * Servo Motor Controller
 * 
 * Arduino library for controlling multiple servo motors
 * with position feedback and smooth motion profiles.
 * 
 * Author: Test Developer
 * License: MIT
 */

#include <Arduino.h>
#include <Servo.h>

// Pin definitions
#define SERVO_PIN_1 9
#define SERVO_PIN_2 10
#define POT_PIN A0

// Configuration constants
const int MIN_PULSE = 544;
const int MAX_PULSE = 2400;
const int UPDATE_INTERVAL = 20;  // milliseconds

// Global servo objects
Servo servo1;
Servo servo2;

// Position tracking
volatile int currentPosition = 90;
volatile int targetPosition = 90;

/**
 * PID controller class for smooth servo control
 */
class PIDController {
public:
    PIDController(float kp, float ki, float kd)
        : _kp(kp), _ki(ki), _kd(kd), _integral(0), _lastError(0) {}
    
    float compute(float setpoint, float measured) {
        float error = setpoint - measured;
        _integral += error;
        float derivative = error - _lastError;
        _lastError = error;
        
        return _kp * error + _ki * _integral + _kd * derivative;
    }
    
    void reset() {
        _integral = 0;
        _lastError = 0;
    }

private:
    float _kp, _ki, _kd;
    float _integral;
    float _lastError;
};

// Global PID instance
PIDController pid(1.0, 0.1, 0.05);

/**
 * Initialize servo motors and pins
 */
void setup() {
    Serial.begin(115200);
    Serial.println("Servo Controller Starting...");
    
    // Attach servos
    servo1.attach(SERVO_PIN_1, MIN_PULSE, MAX_PULSE);
    servo2.attach(SERVO_PIN_2, MIN_PULSE, MAX_PULSE);
    
    // Set initial position
    servo1.write(90);
    servo2.write(90);
    
    // Configure ADC
    pinMode(POT_PIN, INPUT);
    
    Serial.println("Initialization complete.");
}

/**
 * Main control loop
 */
void loop() {
    static unsigned long lastUpdate = 0;
    
    // Read potentiometer for target
    int potValue = analogRead(POT_PIN);
    targetPosition = map(potValue, 0, 1023, 0, 180);
    
    // Update at fixed interval
    if (millis() - lastUpdate >= UPDATE_INTERVAL) {
        lastUpdate = millis();
        
        // Compute PID output
        float output = pid.compute(targetPosition, currentPosition);
        
        // Apply to servo
        currentPosition += constrain(output, -5, 5);
        currentPosition = constrain(currentPosition, 0, 180);
        
        servo1.write(currentPosition);
        
        // Debug output
        Serial.print("Target: ");
        Serial.print(targetPosition);
        Serial.print(" Current: ");
        Serial.println(currentPosition);
    }
}

/**
 * Set servo to specific angle with smooth motion
 * 
 * @param angle Target angle in degrees (0-180)
 * @param speed Motion speed (1-10)
 */
void setServoAngle(int angle, int speed) {
    angle = constrain(angle, 0, 180);
    speed = constrain(speed, 1, 10);
    
    int step = (angle > currentPosition) ? 1 : -1;
    int delayMs = 20 / speed;
    
    while (currentPosition != angle) {
        currentPosition += step;
        servo1.write(currentPosition);
        delay(delayMs);
    }
}
'''
    path.write_text(content)


def create_corrupted_pdf(path: Path):
    """Create a corrupted PDF file for testing error handling."""
    # Write invalid PDF header followed by garbage
    path.write_bytes(b"%PDF-1.4\n" + os.urandom(1000))


# ============================================================================
# PDF Extraction Tests
# ============================================================================

class TestPDFExtraction:
    """Tests for PDF extraction."""
    
    def test_extract_text_pdf(self, extractor, temp_dir, performance_log):
        """Test extraction of born-digital text PDF."""
        pdf_path = temp_dir / "servo_manual.pdf"
        create_synthetic_pdf(pdf_path, pages=3)
        
        start = time.perf_counter()
        result = extractor.extract(pdf_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        performance_log.append({
            'test': 'Text PDF (3 pages)',
            'time_ms': elapsed_ms,
            'target_ms': 100,
            'passed_target': elapsed_ms < 100
        })
        
        assert result.file_type == FileType.PDF
        assert result.confidence >= 0.8  # Should be high for text PDF
        assert 'servo' in result.text.lower() or 'pdf' in result.text.lower()
        assert result.metadata.get('pages', 0) >= 1
    
    def test_pdf_metadata_extraction(self, extractor, temp_dir):
        """Test that PDF metadata is extracted."""
        pdf_path = temp_dir / "test.pdf"
        create_synthetic_pdf(pdf_path, pages=1)
        
        result = extractor.extract(pdf_path)
        
        assert 'filename' in result.metadata
        assert 'file_size' in result.metadata
        assert result.metadata['file_size'] > 0
    
    def test_corrupted_pdf_graceful_failure(self, extractor, temp_dir, performance_log):
        """Test graceful handling of corrupted PDF."""
        pdf_path = temp_dir / "corrupted.pdf"
        create_corrupted_pdf(pdf_path)
        
        start = time.perf_counter()
        result = extractor.extract(pdf_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        performance_log.append({
            'test': 'Corrupted PDF (graceful fail)',
            'time_ms': elapsed_ms,
            'target_ms': 500,
            'passed_target': elapsed_ms < 500
        })
        
        # Should not raise, should return low confidence
        assert result.confidence <= ConfidenceScores.FALLBACK_FILENAME
        assert 'corrupted' in result.text.lower() or result.error is not None


# ============================================================================
# Image Extraction Tests
# ============================================================================

class TestImageExtraction:
    """Tests for image extraction."""
    
    def test_extract_image_metadata(self, extractor, temp_dir, performance_log):
        """Test extraction of image metadata."""
        img_path = temp_dir / "barcode.png"
        create_synthetic_image(img_path)
        
        start = time.perf_counter()
        result = extractor.extract(img_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        performance_log.append({
            'test': 'Image (PNG with text)',
            'time_ms': elapsed_ms,
            'target_ms': 500,
            'passed_target': elapsed_ms < 500
        })
        
        assert result.file_type == FileType.IMAGE
        assert result.confidence > 0  # At least some confidence
        assert 'filename' in result.metadata
        
        # Should have dimensions if PIL worked
        if 'width' in result.metadata:
            assert result.metadata['width'] > 0
            assert result.metadata['height'] > 0
    
    def test_image_ocr_fallback(self, extractor, temp_dir):
        """Test that OCR falls back gracefully when unavailable."""
        img_path = temp_dir / "test.png"
        create_synthetic_image(img_path, with_text=True)
        
        result = extractor.extract(img_path)
        
        # Should still return something, even without OCR
        assert result.text  # Non-empty
        assert result.file_type == FileType.IMAGE


# ============================================================================
# Code Extraction Tests
# ============================================================================

class TestCodeExtraction:
    """Tests for code extraction."""
    
    def test_extract_python(self, extractor, temp_dir, performance_log):
        """Test Python code extraction with AST parsing."""
        py_path = temp_dir / "servo_controller.py"
        create_python_file(py_path)
        
        start = time.perf_counter()
        result = extractor.extract(py_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        performance_log.append({
            'test': 'Python code (AST parsing)',
            'time_ms': elapsed_ms,
            'target_ms': 50,
            'passed_target': elapsed_ms < 50
        })
        
        assert result.file_type == FileType.CODE
        assert result.language == 'python'
        assert result.confidence == ConfidenceScores.CODE_DETECTED
        
        # Check that classes and functions were found
        assert 'PIDController' in result.text
        assert 'ServoMotor' in result.text
        assert 'calculate_trajectory' in result.text
        
        # Check metadata
        assert 'functions' in result.metadata or 'classes' in result.metadata
    
    def test_extract_gcode(self, extractor, temp_dir, performance_log):
        """Test G-code extraction and command parsing."""
        gcode_path = temp_dir / "servo_bracket.gcode"
        create_gcode_file(gcode_path)
        
        start = time.perf_counter()
        result = extractor.extract(gcode_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        performance_log.append({
            'test': 'G-code (command parsing)',
            'time_ms': elapsed_ms,
            'target_ms': 30,
            'passed_target': elapsed_ms < 30
        })
        
        assert result.file_type == FileType.CODE
        assert result.language == 'gcode'
        assert result.confidence == ConfidenceScores.CODE_DETECTED
        
        # Check commands were extracted
        assert 'G0' in result.text or 'G1' in result.text
        assert 'commands' in result.metadata
        
        # Should have found positioning commands
        commands = result.metadata.get('commands', {})
        assert any(c in commands for c in ['G0', 'G1', 'G2', 'G3'])
    
    def test_extract_cpp(self, extractor, temp_dir, performance_log):
        """Test C++/Arduino code extraction."""
        cpp_path = temp_dir / "servo_controller.ino"
        create_cpp_file(cpp_path)
        
        start = time.perf_counter()
        result = extractor.extract(cpp_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        performance_log.append({
            'test': 'Arduino/C++ code',
            'time_ms': elapsed_ms,
            'target_ms': 50,
            'passed_target': elapsed_ms < 50
        })
        
        assert result.file_type == FileType.CODE
        assert result.language == 'arduino'
        assert result.confidence == ConfidenceScores.CODE_DETECTED
        
        # Check key elements found
        assert 'PIDController' in result.text
        assert 'setup' in result.text.lower()
        assert 'loop' in result.text.lower()
    
    def test_python_syntax_error_fallback(self, extractor, temp_dir):
        """Test Python extraction falls back on syntax errors."""
        py_path = temp_dir / "broken.py"
        py_path.write_text('''
def valid_function():
    """This function is valid."""
    return 42

# Syntax error below
def broken_function(
    """Missing closing paren"""
    pass
''')
        
        result = extractor.extract(py_path)
        
        # Should still extract something
        assert result.text
        assert result.file_type == FileType.CODE
        # Confidence should be lower due to syntax error
        assert result.confidence <= ConfidenceScores.CODE_UNKNOWN


# ============================================================================
# Auto-Detection Tests
# ============================================================================

class TestFileTypeDetection:
    """Tests for file type auto-detection."""
    
    def test_detect_pdf(self, extractor, temp_dir):
        """Test PDF detection."""
        pdf_path = temp_dir / "test.pdf"
        create_synthetic_pdf(pdf_path)
        
        file_type = extractor.detect_file_type(pdf_path)
        assert file_type == FileType.PDF
    
    def test_detect_image_extensions(self, extractor, temp_dir):
        """Test various image extension detection."""
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            img_path = temp_dir / f"test{ext}"
            img_path.write_bytes(b'\x00')  # Minimal content
            
            file_type = extractor.detect_file_type(img_path)
            assert file_type == FileType.IMAGE, f"Failed for {ext}"
    
    def test_detect_code_extensions(self, extractor, temp_dir):
        """Test various code extension detection."""
        for ext in ['.py', '.cpp', '.c', '.js', '.gcode']:
            code_path = temp_dir / f"test{ext}"
            code_path.write_text("// code")
            
            file_type = extractor.detect_file_type(code_path)
            assert file_type == FileType.CODE, f"Failed for {ext}"


# ============================================================================
# Batch Processing Tests
# ============================================================================

class TestBatchProcessing:
    """Tests for batch extraction."""
    
    def test_batch_extract_directory(self, temp_dir):
        """Test batch extraction of a directory."""
        # Create mixed files
        create_python_file(temp_dir / "code.py")
        create_gcode_file(temp_dir / "part.gcode")
        (temp_dir / "readme.md").write_text("# Test\nThis is a test.")
        
        batch = BatchExtractor()
        results = batch.extract_directory(temp_dir, recursive=False)
        
        assert len(results) >= 2  # At least py and gcode
        assert all(isinstance(r, ExtractionResult) for r in results)
    
    def test_batch_progress_callback(self, temp_dir):
        """Test that progress callback is called."""
        create_python_file(temp_dir / "a.py")
        create_python_file(temp_dir / "b.py")
        
        progress_calls = []
        
        def callback(current, total, filename):
            progress_calls.append((current, total, filename))
        
        batch = BatchExtractor()
        batch.extract_directory(temp_dir, progress_callback=callback)
        
        assert len(progress_calls) >= 2


# ============================================================================
# Confidence Scoring Tests
# ============================================================================

class TestConfidenceScoring:
    """Tests for confidence score assignment."""
    
    def test_text_pdf_confidence(self, extractor, temp_dir):
        """Text PDFs should have high confidence."""
        pdf_path = temp_dir / "text.pdf"
        create_synthetic_pdf(pdf_path)
        
        result = extractor.extract(pdf_path)
        
        # Born-digital text PDF should be ~1.0
        assert result.confidence >= 0.8
    
    def test_code_detected_confidence(self, extractor, temp_dir):
        """Detected code should have confidence 1.0."""
        py_path = temp_dir / "valid.py"
        py_path.write_text('def hello(): pass')
        
        result = extractor.extract(py_path)
        
        assert result.confidence == ConfidenceScores.CODE_DETECTED
    
    def test_unknown_file_low_confidence(self, extractor, temp_dir):
        """Unknown files should have low confidence."""
        unk_path = temp_dir / "data.xyz"
        unk_path.write_bytes(os.urandom(100))
        
        result = extractor.extract(unk_path)
        
        assert result.confidence <= ConfidenceScores.CODE_UNKNOWN


# ============================================================================
# Statistics Tests
# ============================================================================

class TestStatistics:
    """Tests for extraction statistics tracking."""
    
    def test_statistics_tracking(self, temp_dir):
        """Test that statistics are tracked correctly."""
        extractor = DocumentExtractor()
        
        create_python_file(temp_dir / "a.py")
        create_gcode_file(temp_dir / "b.gcode")
        
        extractor.extract(temp_dir / "a.py")
        extractor.extract(temp_dir / "b.gcode")
        
        stats = extractor.get_statistics()
        
        assert stats['total_extractions'] == 2
        assert stats['total_time_ms'] > 0
        assert stats['average_time_ms'] > 0
    
    def test_statistics_reset(self, temp_dir):
        """Test statistics reset."""
        extractor = DocumentExtractor()
        
        create_python_file(temp_dir / "test.py")
        extractor.extract(temp_dir / "test.py")
        
        extractor.reset_statistics()
        stats = extractor.get_statistics()
        
        assert stats['total_extractions'] == 0


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_nonexistent_file(self, extractor):
        """Test handling of nonexistent file."""
        result = extractor.extract("/nonexistent/file.pdf")
        
        assert result.error is not None
        assert result.confidence == ConfidenceScores.EXTRACTION_FAILED
    
    def test_empty_file(self, extractor, temp_dir):
        """Test handling of empty file."""
        empty_path = temp_dir / "empty.py"
        empty_path.write_text("")
        
        result = extractor.extract(empty_path)
        
        # Should handle gracefully
        assert result.file_type == FileType.CODE
    
    def test_binary_file_detection(self, extractor, temp_dir):
        """Test detection of binary content in unknown files."""
        bin_path = temp_dir / "data.bin"
        bin_path.write_bytes(os.urandom(1000))
        
        result = extractor.extract(bin_path)
        
        # Should detect as binary and give low confidence
        assert 'binary' in result.text.lower() or result.confidence < 0.5


# ============================================================================
# Performance Report Generator
# ============================================================================

def generate_build_log_entry(measurements: list) -> str:
    """Generate BUILD_LOG.md entry from test measurements."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"""## [{timestamp}] Extraction Pipeline

### Completed
- [x] PDF extraction (pdfplumber)
- [x] Image metadata/OCR (PIL + pytesseract fallback)
- [x] Code parsing (AST for Python, regex for C++/G-code)
- [x] Confidence scoring
- [x] Tests passing

### Performance (Actual)
"""
    
    for m in measurements:
        status = "✅" if m['passed_target'] else "⚠️"
        entry += f"- {m['test']}: {m['time_ms']:.1f}ms (target: <{m['target_ms']}ms) {status}\n"
    
    entry += """
### Notes
- OCR requires pytesseract + tesseract-ocr system package
- Falls back gracefully when dependencies unavailable
- Confidence scoring based on text quality heuristics

### Next
- [ ] Database storage (SQLite + FTS5)
- [ ] Search agent integration
"""
    
    return entry


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == '__main__':
    # Run with pytest and collect performance data
    import subprocess
    
    print("Running extraction pipeline tests...")
    print("=" * 60)
    
    result = subprocess.run(
        ['python', '-m', 'pytest', __file__, '-v', '--tb=short'],
        capture_output=False
    )
    
    sys.exit(result.returncode)
