#!/usr/bin/env python3
import glob
import os
import platform
import sys
import time
import serial
import serial.tools.list_ports

DEFAULT_BAUD = 115200


def is_raspberry_pi():
    if platform.system() != "Linux":
        return False
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "Raspberry Pi" in f.read()
    except Exception:
        return False


def detect_port():
    os_name = platform.system()

    # 1. Raspberry Pi 5 Hardware Header
    if is_raspberry_pi():
        if os.path.exists("/dev/ttyAMA0"):
            return "Raspberry Pi 5 (Pins 8 & 10)", "/dev/ttyAMA0"
        elif os.path.exists("/dev/serial0"):
            return "Raspberry Pi (Pins 8 & 10)", "/dev/serial0"
        return "Raspberry Pi", None

    # 2. Windows Laptop
    elif os_name == "Windows":
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if (
                p.vid == 0x0403
                or "FTDI" in p.description
                or "USB Serial" in p.description
            ):
                return f"Windows ({p.description})", p.device
        if ports:
            return f"Windows ({ports[0].description})", ports[0].device
        return "Windows", None

    # 3. Ubuntu Workstation
    elif os_name == "Linux":
        ftdi_links = glob.glob("/dev/serial/by-id/*FTDI*")
        if ftdi_links:
            return "Ubuntu (DTECH FTDI)", ftdi_links[0]
        for p in serial.tools.list_ports.comports():
            if p.vid == 0x0403 or "FT232" in (p.description or ""):
                return f"Ubuntu ({p.description})", p.device
        generic = glob.glob("/dev/ttyUSB*")
        if generic:
            return "Ubuntu (USB Serial)", generic[0]
        return "Ubuntu", None

    return "Unknown", None


def run_listener(port, baud):
    print(f"\n[LISTENER ACTIVE] Listening on {port} at {baud} baud...")
    print("Press Ctrl+C to exit.\n" + "-" * 50)

    ser = serial.Serial(port, baud, timeout=1)
    ser.reset_input_buffer()

    while True:
        try:
            raw_bytes = ser.readline()
            if not raw_bytes:
                continue

            # Decode safely and display
            line = raw_bytes.decode("utf-8", errors="replace").strip()
            if line:
                # If the line contains replacement characters, baud rate is wrong
                if "\ufffd" in line:
                    print(
                        f"[{time.strftime('%H:%M:%S')}] [CORRUPT/WRONG BAUD]: {line}"
                    )
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Received: {line}")

        except serial.SerialException:
            print("\n[WARNING] Device disconnected. Reconnecting...")
            ser.close()
            time.sleep(1)
            ser = serial.Serial(port, baud, timeout=1)
        except KeyboardInterrupt:
            print("\nExiting listener...")
            ser.close()
            break


def run_sender(port, baud):
    print(f"\n[SENDER ACTIVE] Transmitting on {port} at {baud} baud.")
    ser = serial.Serial(port, baud, timeout=1)
    ser.reset_output_buffer()

    mode = input("Choose mode -> [1] Manual input, [2] Auto pulse (1/2): ").strip()
    system_name = platform.system()

    if mode == "2":
        count = 1
        while True:
            try:
                msg = f"{system_name} Heartbeat #{count} [{time.strftime('%H:%M:%S')}]\n"
                ser.write(msg.encode("utf-8"))
                print(f"Sent: {msg.strip()}")
                count += 1
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopped pulse.")
                break
    else:
        print("Type your message and press Enter. Ctrl+C to exit.")
        while True:
            try:
                msg = input("Send > ")
                if msg.strip():
                    ser.write((msg + "\n").encode("utf-8"))
            except KeyboardInterrupt:
                print("\nExiting sender...")
                break
    ser.close()


def main():
    env_name, port = detect_port()
    if not port:
        print(f"[ERROR] No serial/UART port detected for {env_name}.")
        sys.exit(1)

    print("=" * 50)
    print(f" Device : {env_name}")
    print(f" Port   : {port}")
    print(f" Baud   : {DEFAULT_BAUD}")
    print("=" * 50)

    print("\nSelect Action:")
    print("  [1] Listener (Receive messages)")
    print("  [2] Sender   (Transmit messages)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        run_listener(port, DEFAULT_BAUD)
    elif choice == "2":
        run_sender(port, DEFAULT_BAUD)


if __name__ == "__main__":
    main()