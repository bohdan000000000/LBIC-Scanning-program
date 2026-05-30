#!/usr/bin/env python3
"""
Ініціалізація GRBL та зв'язок з вимірювальним вузлом.
Базується на simple_stream.py (gnea/grbl, MIT License).
"""
import serial
import time

GRBL_PORT = 'COM3'   # Arduino #1 (GRBL)  - Linux: /dev/ttyUSB0
MEAS_PORT = 'COM4'   # Arduino #2 (вимір) - Linux: /dev/ttyUSB1
BAUD      = 115200

grbl = serial.Serial(GRBL_PORT, BAUD, timeout=10)
meas = serial.Serial(MEAS_PORT, BAUD, timeout=5)

def grbl_send(cmd: str) -> str:
    """
    Надіслати G-код команду GRBL, дочекатись відповіді 'ok' або 'error'.
    Патерн: send -> wait -> receive (simple_stream.py).
    """
    grbl.write((cmd.strip() + '\n').encode('ascii'))
    while True:
        line = grbl.readline().decode('ascii', errors='ignore').strip()
        if line == 'ok':
            return 'ok'
        if line.startswith('error'):
            print(f'[GRBL ERR] cmd="{cmd}" -> "{line}"')
            return line
        # Ігноруємо статусні рядки виду <Idle|MPos:0.000,...>

def grbl_init():
    """Пробудження GRBL — точна послідовність з simple_stream.py."""
    grbl.write(b'\r\n\r\n')    # Wake up
    time.sleep(2)               # Чекаємо ініціалізацію ATmega328P
    grbl.flushInput()           # Очищаємо вітальний текст прошивки

    grbl_send('$X')             # Зняти Alarm Lock
    grbl_send('G21')            # Одиниці — міліметри
    grbl_send('G90')            # Абсолютні координати
    grbl_send('G92 X0 Y0')      # Поточна точка = початок координат (0, 0)
    print('GRBL initialized.')

def read_photocurrent() -> float:
    """Запустити FSM на Arduino #2, отримати дельта-сигнал (V_light - V_dark)."""
    meas.write(b'MEASURE\n')
    while True:
        line = meas.readline().decode('ascii', errors='ignore').strip()
        if line.startswith('DATA:'):
            return float(line.split(':')[1])