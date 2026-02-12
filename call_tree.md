# Call Tree: Demo_Init

## Metadata

- **Root Function**: `Demo_Init`
- **Generated**: 2026-02-10 22:17:37
- **Total Functions**: 14
- **Unique Functions**: 14
- **Max Depth**: 2
- **Circular Dependencies**: 0

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Demo_Init
    participant COM_InitCommunication
    participant COM_InitCAN
    participant COM_InitEthernet
    participant COM_InitLIN
    participant Demo_InitVariables
    participant HW_InitHardware
    participant HW_InitADC
    participant HW_InitClock
    participant HW_InitGPIO
    participant HW_InitPWM
    participant SW_InitSoftware
    participant SW_InitConfig
    participant SW_InitState

    Demo_Init->>COM_InitCommunication: call(baud_rate, buffer_size)
    COM_InitCommunication->>COM_InitCAN: call
    COM_InitCommunication->>COM_InitEthernet: call
    COM_InitCommunication->>COM_InitLIN: call
    Demo_Init->>Demo_InitVariables: call(config_mode)
    Demo_Init->>HW_InitHardware: call(clock_freq, gpio_mask)
    HW_InitHardware->>HW_InitADC: call
    HW_InitHardware->>HW_InitClock: call
    HW_InitHardware->>HW_InitGPIO: call
    HW_InitHardware->>HW_InitPWM: call
    Demo_Init->>SW_InitSoftware: call(state, config)
    SW_InitSoftware->>SW_InitConfig: call
    SW_InitSoftware->>SW_InitState: call
```

## Function Details

| Function | File | Line | Return Type | Parameters |
|----------|------|------|-------------|------------|
| `COM_InitCAN` | communication.c | 9 | `void` | `void` |
| `COM_InitCommunication` | communication.c | 27 | `void` | `uint32 baud_rate`<br>`uint16 buffer_size` |
| `COM_InitEthernet` | communication.c | 21 | `void` | `void` |
| `COM_InitLIN` | communication.c | 15 | `void` | `void` |
| `Demo_Init` | demo.c | 8 | `void` | `void` |
| `Demo_InitVariables` | demo.c | 19 | `void` | `uint32 config_mode` |
| `HW_InitADC` | hardware.c | 27 | `void` | `void` |
| `HW_InitClock` | hardware.c | 9 | `void` | `void` |
| `HW_InitGPIO` | hardware.c | 15 | `void` | `void` |
| `HW_InitHardware` | hardware.c | 33 | `void` | `uint32 clock_freq`<br>`uint32 gpio_mask` |
| `HW_InitPWM` | hardware.c | 21 | `void` | `void` |
| `SW_InitConfig` | software.c | 15 | `void` | `void` |
| `SW_InitSoftware` | software.c | 21 | `void` | `uint8 state`<br>`uint8 config` |
| `SW_InitState` | software.c | 9 | `void` | `void` |

## Call Tree (Text)

```
Demo_Init (demo.c:8)
├── COM_InitCommunication (communication.c:27)
│   ├── COM_InitCAN (communication.c:9)
│   ├── COM_InitEthernet (communication.c:21)
│   └── COM_InitLIN (communication.c:15)
├── Demo_InitVariables (demo.c:19)
├── HW_InitHardware (hardware.c:33)
│   ├── HW_InitADC (hardware.c:27)
│   ├── HW_InitClock (hardware.c:9)
│   ├── HW_InitGPIO (hardware.c:15)
│   └── HW_InitPWM (hardware.c:21)
└── SW_InitSoftware (software.c:21)
    ├── SW_InitConfig (software.c:15)
    └── SW_InitState (software.c:9)
```
