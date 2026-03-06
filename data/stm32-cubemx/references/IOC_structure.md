# IOC File Structure Reference

## Overview

The `.ioc` file is STM32CubeMX's project configuration file in INI format.

## Main Configuration Sections

### 1. MCU Basic Information

```ini
Mcu.Family=STM32F1
Mcu.IP0=ADC1
Mcu.IP1=DMA
Mcu.IP2=NVIC
Mcu.IP3=RCC
Mcu.IP4=SYS
Mcu.IPNb=5
Mcu.Name=STM32F103C(8)Tx
Mcu.Package=LQFP48
Mcu.Pin0=PA0
Mcu.Pin1=PA1
Mcu.PinsNb=10
Mcu.UserConstants=
Mcu.UserName=STM32F103C8Tx
```

### 2. Pin Configuration

```ini
# Basic pin configuration
PA0.GPIO_Label=LED_PIN
PA0.Locked=true
PA0.Signal=ADCx_IN0

# GPIO mode configuration
PA0.GPIO.Mode=AN
PA0.GPIO.Pull=_NOPULL
PA0.GPIO.Speed=GPIO_SPEED_FREQ_LOW

# Shared signals (e.g., ADC)
SH.ADCx_IN0.0=ADC1_IN0,IN0
SH.ADCx_IN0.ConfNb=1
```

### 3. Peripheral IP Configuration

```ini
# RCC (Clock configuration)
RCC.ADCFreqValue=12000000
RCC.AHBFreq_Value=72000000
RCC.APB1Freq_Value=36000000
RCC.APB2Freq_Value=72000000
RCC.HSE_VALUE=8000000
RCC.PLLM=8
RCC.PLLN=72
RCC.PLLP=RCC_PLLP_DIV2
RCC.PLLQ=3
RCC.PLLSourceVirtual=RCC_PLLSOURCE_HSE
RCC.SysCLKFreq_Value=72000000

# SYS
VP_SYS_VS_Systick.Mode=SysTick
VP_SYS_VS_Systick.Signal=SYS_VS_Systick
```

### 4. Peripheral Parameter Configuration

```ini
# USART example
USART2.BaudRate=115200
USART2.WordLength=WORDLENGTH_8B
USART2.StopBits=STOPBITS_1
USART2.Parity=PARITY_NONE
USART2.Mode=MODE_TX_RX
USART2.HwFlowControl=HWCONTROL_NONE
USART2.OverSampling=OVERSAMPLING_16
USART2.VirtualMode=VM_ASYNC
USART2.IPParameters=BaudRate,WordLength,StopBits,Parity,Mode,HwFlowControl,OverSampling,VirtualMode

# TIM example
TIM3.AutoReloadPreload=TIM_AUTORELOAD_PRELOAD_ENABLE
TIM3.CounterMode=TIM_COUNTERMODE_UP
TIM3.Period=999
TIM3.Prescaler=71
TIM3.IPParameters=CounterMode,Period,Prescaler,AutoReloadPreload
```

### 5. DMA Configuration

```ini
# DMA request list
Dma.Request0=USART2_RX
Dma.Request1=USART2_TX
Dma.RequestsNb=2

# Single DMA channel configuration
Dma.USART2_RX.0.Direction=DMA_PERIPH_TO_MEMORY
Dma.USART2_RX.0.Instance=DMA1_Channel6
Dma.USART2_RX.0.MemDataAlignment=DMA_MDATAALIGN_BYTE
Dma.USART2_RX.0.MemInc=DMA_MINC_ENABLE
Dma.USART2_RX.0.Mode=DMA_NORMAL
Dma.USART2_RX.0.PeriphDataAlignment=DMA_PDATAALIGN_BYTE
Dma.USART2_RX.0.PeriphInc=DMA_PINC_DISABLE
Dma.USART2_RX.0.Priority=DMA_PRIORITY_LOW
Dma.USART2_RX.0.RequestParameters=Instance,Direction,PeriphInc,MemInc,PeriphDataAlignment,MemDataAlignment,Mode,Priority
```

### 6. NVIC Interrupt Configuration

```ini
# Interrupt enable and priority
NVIC.USART2_IRQn=true\:0\:0\:false\:false\:true\:true\:true\:true
NVIC.DMA1_Channel6_IRQn=true\:0\:0\:false\:false\:true\:false\:true\:true
NVIC.EXTI0_IRQn=true\:1\:0\:true\:false\:true\:true\:true\:true

# Priority grouping
NVIC.PriorityGroup=NVIC_PRIORITYGROUP_4
```

### 7. Project Management Configuration

```ini
# Project manager
ProjectManager.AskForMigrate=true
ProjectManager.BackupPrevious=false
ProjectManager.CompilerOptimization=Optimization Level 1
ProjectManager.ComputerToolchain=Linux
ProjectManager.CoupleFileByIP=false
ProjectManager.CustomerFirmwarePackage=
ProjectManager.DefaultFWLocation=true
ProjectManager.DeletePrevious=true
ProjectManager.DeviceIdFromTool=true
ProjectManager.FirmwarePackage=STM32Cube FW_F1 V1.8.7
ProjectManager.FreePins=false
ProjectManager.HalAssertFull=false
ProjectManager.HeapSize=0x200
ProjectManager.KeepUserCode=true
ProjectManager.LibraryProject=Library
ProjectManager.MainLocation=Core/Src
ProjectManager.PreviousToolchain=SW4STM32
ProjectManager.ProjectBuild=false
ProjectManager.ProjectFileName=STM32F103C8T6_Template.ioc
ProjectManager.ProjectName=STM32F103C8T6_Template
ProjectManager.RegisterCallBack=
ProjectManager.StackSize=0x400
ProjectManager.TargetToolchain=CMake
ProjectManager.TemplatePair=
ProjectManager.ToolChainLocation=

# Initialization function list (important!)
ProjectManager.functionlistsort=1-SystemClock_Config-RCC-false-HAL-false,2-MX_GPIO_Init-GPIO-false-HAL-true,3-MX_DMA_Init-DMA-false-HAL-true,4-MX_USART2_UART_Init-USART2-false-HAL-true
```

### 8. Toolchain Configuration

```ini
# CMake configuration
Toolchain.CMake.Compiler.Location=
Toolchain.CMake.Compiler.Executable=
Toolchain.CMake.Make.Location=
Toolchain.CMake.Make.Executable=make
```

## Configuration Rules

### Steps to Add a New Peripheral

1. Add IP to `Mcu.IPx` list
2. Update `Mcu.IPNb` count
3. Add pin configuration `Mcu.Pinxx`
4. Update `Mcu.PinsNb` count
5. Configure peripheral parameters
6. Update `ProjectManager.functionlistsort`

### functionlistsort Format

```
Index-FunctionName-Peripheral-IsMSP-HAL/LL-GenerateWeakFunction
```

Example:
```
1-SystemClock_Config-RCC-false-HAL-false
2-MX_GPIO_Init-GPIO-false-HAL-true
3-MX_DMA_Init-DMA-false-HAL-true
4-MX_USART2_UART_Init-USART2-false-HAL-true
```

## Special Character Escaping

Special characters in IOC files must be escaped:

| Character | Escape Sequence |
|------|----------|
| `:` | `\:` |
| `#` | `\#` |
| `=` | `\=` |
| Space | `\ ` (in property names) |

Example:
```ini
ADC1.Channel-1\#ChannelRegularConversion=ADC_CHANNEL_5
NVIC.USART2_IRQn=true\:0\:0\:false\:false\:true\:true\:true\:true
```
