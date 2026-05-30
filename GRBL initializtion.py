
"""
Ініціалізація GRBL та зв'язок з вимірювальним вузлом.
Базується на simple_stream.py (gnea/grbl, MIT License).
"""
import serial
import time

GRBL_PORT = 'COM3'   
MEAS_PORT = 'COM4'   
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

def grbl_init():
    """Пробудження GRBL — точна послідовність з simple_stream.py."""
    grbl.write(b'\r\n\r\n')    
    time.sleep(2)               
    grbl.flushInput()          

    grbl_send('$X')            
    grbl_send('G21')            
    grbl_send('G90')            
    grbl_send('G92 X0 Y0')      
    print('GRBL initialized.')

def read_photocurrent() -> float:
    """Запустити FSM на Arduino #2, отримати дельта-сигнал (V_light - V_dark)."""
    meas.write(b'MEASURE\n')
    while True:
        line = meas.readline().decode('ascii', errors='ignore').strip()
        if line.startswith('DATA:'):
            return float(line.split(':')[1])
