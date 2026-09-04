# Universal UART Bridge

A zero-configuration, cross-platform serial diagnostic tool for testing and establishing UART communication between a **Raspberry Pi 5** GPIO header and a host workstation (**Ubuntu Linux** or **Windows**).

The script automatically detects the host environment, resolves the correct serial port device path (`/dev/ttyAMA0`, `/dev/serial/by-id/`, or `COMx`), and provides dedicated **Listener** and **Sender** (manual or heartbeat pulse) modes.

---

## Features

* **Zero Manual Port Mapping:**
  * **Raspberry Pi 5:** Automatically selects the RP1 hardware UART controller (`/dev/ttyAMA0`).
  * **Ubuntu Workstation:** Uses `/dev/serial/by-id/` and FTDI hardware Vendor IDs (0x0403) to ensure stable binding regardless of USB hub re-indexing.
  * **Windows:** Scans hardware COM registry to auto-bind the USB-to-UART adapter.
* **Dual Operation Modes:**
  * **Listener:** Continuous UTF-8 stream monitoring with baud corruption detection.
  * **Sender:** Supports both interactive live message entry and automated 1 Hz heartbeat pulses.
* **Resilience:** Built-in exception handling to reconnect automatically if the USB cable is physically unplugged or reset.

---

## Hardware Pinout & Wiring

UART lines must be crossed over ($TX \rightarrow RX$ and $RX \rightarrow TX$). Ensure a common ground is connected.

| Raspberry Pi 5 Header | Pi Signal | DTECH / FTDI Cable Wire | Host Function |
|:---|:---|:---|:---|
| **Pin 6** | GND | **GND** (Black) | Ground Reference |
| **Pin 8** | GPIO 14 (TXD0) | **RXD** (Yellow or White) | Host Receives |
| **Pin 10** | GPIO 15 (RXD0) | **TXD** (Orange or Green) | Host Transmits |

> **Warning:** Do NOT connect the 5V power wire (Red) from the USB adapter to the Raspberry Pi if the Pi is powered by its own power supply. Raspberry Pi GPIO pins operate strictly on **3.3V logic**.

---

## Prerequisites & System Setup

### 1. Raspberry Pi 5 (RP1 GPIO Setup)

The Raspberry Pi 5 routes the default Linux serial console to a dedicated 3-pin JST debug connector. To route UART to physical header Pins 8 & 10:

1. Edit the boot configuration:
   ```bash
   sudo nano /boot/firmware/config.txt