---
name: stm32-cubemx
description: "STM32CubeMX CLI operations for configuring pins, peripherals, DMA, interrupts, and generating code. Use cases: (1) Add/modify STM32 peripheral configuration (2) Configure USART/SPI/I2C/ADC/TIM peripherals (3) Set up DMA and interrupts (4) Generate CMake/GCC project code. Default target MCU: STM32F103C8Tx."
---

# STM32CubeMX CLI Operations

## Environment Setup

```bash
# STM32CubeMX path (modify based on your installation)
CUBEMX=/path/to/STM32CubeMX/STM32CubeMX

# Project path (adjust for your project)
PROJECT_DIR=/path/to/your/project
IOC_FILE=$PROJECT_DIR/your_project.ioc
SCRIPT_FILE=$PROJECT_DIR/cube_headless.txt
```

## Core Workflow

```
1. Modify IOC config file → 2. Run CLI to generate code → 3. CMake build verification
```

### Step 1: Modify IOC File

Edit the `.ioc` file to add/modify peripheral configuration.

**Key Configuration Sections:**
- `Mcu.IP0=XXX` - Peripheral IP list, `Mcu.IPNb` is the count
- `Mcu.Pin0=PAx` - Pin list, `Mcu.PinsNb` is the count
- `XXX.Signal=YYY` - Pin signal mapping
- `ProjectManager.functionlistsort` - Initialization function list

### Step 2: Generate Code

```bash
# Headless mode (recommended)
$CUBEMX -q $SCRIPT_FILE

# Script file content
cat > $SCRIPT_FILE << 'EOF'
config load /path/to/your/project/your_project.ioc
project generate
exit
EOF
```

### Step 3: Build Verification

```bash
cd $PROJECT_DIR
rm -rf build/Debug
cmake --preset Debug
cmake --build build/Debug
```

## CLI Command Reference

| Command | Purpose | Example |
|------|------|------|
| `config load <path>` | Load IOC configuration | `config load /path/to/project.ioc` |
| `config save <path>` | Save IOC configuration | `config save /path/to/project.ioc` |
| `project generate` | Generate complete project | `project generate` |
| `project toolchain <name>` | Set toolchain | `project toolchain CMake` |
| `project path <path>` | Set project path | `project path /path/to/project` |
| `project name <name>` | Set project name | `project name MyProject` |
| `load <mcu>` | Load MCU | `load STM32F103C8Tx` |
| `setDriver <IP> <HAL\|LL>` | Set driver type | `setDriver ADC LL` |
| `exit` | Exit program | `exit` |

## Common Peripheral Configuration Templates

### USART + DMA

See [references/USART_DMA.md](references/USART_DMA.md) for detailed configuration

```ini
# Add IP
Mcu.IP6=USART2
Mcu.IPNb=7

# Pin configuration
PA2.Signal=USART2_TX
PA3.Signal=USART2_RX

# USART2 parameters
USART2.BaudRate=115200
USART2.Dmaenabledrx=1
USART2.Dmaenabledtx=1

# DMA configuration
Dma.Request0=USART2_RX
Dma.Request1=USART2_TX
Dma.USART2_RX.0.Instance=DMA1_Channel6
Dma.USART2_TX.1.Instance=DMA1_Channel7

# Interrupts
NVIC.USART2_IRQn=true\:0\:0\:false\:false\:true\:true\:true\:true
```

### ADC Acquisition

```ini
# Add ADC1
Mcu.IP0=ADC1

# ADC configuration
ADC1.Channel-1\#ChannelRegularConversion=ADC_CHANNEL_5
ADC1.Rank-1\#ChannelRegularConversion=1
ADC1.SamplingTime-1\#ChannelRegularConversion=ADC_SAMPLETIME_1CYCLE_5
ADC1.NbrOfConversionFlag=1
ADC1.master=1

# Pin
PA5.Signal=ADCx_IN5
SH.ADCx_IN5.0=ADC1_IN5,IN5
```

### TIM PWM

```ini
# TIM3 configuration
TIM3.Channel-PWM\ Generation1\ CH1=PWM_CHANNEL1
TIM3.Channel-PWM\ Generation2\ CH2=PWM_CHANNEL2
TIM3.IPParametersWithoutCheck=Prescaler,Period

# Pins
PA6.Signal=TIM3_CH1
PA7.Signal=TIM3_CH2
```

## STM32F103C8T6 Resource Mapping

### USART

| Peripheral | TX | RX | DMA TX | DMA RX |
|------|-----|-----|--------|--------|
| USART1 | PA9 | PA10 | DMA1_Ch4 | DMA1_Ch5 |
| USART2 | PA2 | PA3 | DMA1_Ch7 | DMA1_Ch6 |
| USART3 | PB10 | PB11 | DMA1_Ch2 | DMA1_Ch3 |

### ADC Channels

| Channel | Pin | Channel | Pin |
|------|------|------|------|
| IN0 | PA0 | IN5 | PA5 |
| IN1 | PA1 | IN6 | PA6 |
| IN2 | PA2 | IN7 | PA7 |
| IN3 | PA3 | IN8 | PB0 |
| IN4 | PA4 | IN9 | PB1 |

### TIM Channels

| Timer | CH1 | CH2 | CH3 | CH4 |
|--------|-----|-----|-----|-----|
| TIM1 | PA8 | PA9 | PA10 | PA11 |
| TIM2 | PA0/PA5/PA15 | PA1/PB3 | PA2 | PA3 |
| TIM3 | PA6/PB4 | PA7/PB5 | PB0 | PB1 |
| TIM4 | PB6 | PB7 | PB8 | PB9 |

## Troubleshooting

### Q1: CLI execution has no effect
**Cause**: Paths must be absolute
```bash
# Wrong
./STM32CubeMX -q script.txt
# Correct
/path/to/STM32CubeMX/STM32CubeMX -q /path/to/project/script.txt
```

### Q2: Generated code missing initialization functions
**Cause**: `functionlistsort` does not include the corresponding function
```ini
# Add initialization function
ProjectManager.functionlistsort=...,N-MX_XXX_Init-XXX-false-HAL-true
```

### Q3: Peripheral code not generated
**Checklist**:
1. Is IP in the `Mcu.IPx` list?
2. Is `Mcu.IPNb` count correct?
3. Is pin Signal configured?

### Q4: DMA not associated
**Solution**: Enable peripheral DMA parameters
```ini
USART2.Dmaenabledrx=1
USART2.Dmaenabledtx=1
```

## Quick Reference

```bash
# Complete workflow
cd /path/to/your/project
# 1. Edit IOC file
# 2. Generate code
/path/to/STM32CubeMX/STM32CubeMX -q cube_headless.txt
# 3. Build
cmake --preset Debug && cmake --build build/Debug
# 4. Check size
arm-none-eabi-size build/Debug/your_project.elf
```

## References

- [references/USART_DMA.md](references/USART_DMA.md) - Complete USART + DMA configuration
- [references/IOC_structure.md](references/IOC_structure.md) - Detailed IOC file structure
- [UM1718 STM32CubeMX User Manual](https://www.st.com/resource/en/user_manual/um1718-stm32cubemx-description-stmicroelectronics.pdf)
