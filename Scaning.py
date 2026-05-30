import numpy as np
import time

X_SIZE_MM = 6.0    # ширина зони сканування, мм
Y_SIZE_MM = 6.0    # висота зони сканування, мм
STEP_MM   = 0.020  # крок сканування: 20 мкм
FEED_RATE = 150    # швидкість переміщення, мм/хв
OVERSHOOT = 0.5    # компенсація люфту: підхід з боку -X перед кожним рядком
SETTLE_MS = 30     # час стабілізації каретки після зупинки, мс

def scan_area():
    """
    Растрове LBIC-сканування із програмною компенсацією люфту.
    Синхронізація положення: GRBL надсилає 'ok' тільки після
    повної зупинки каретки (буферизований планoвик руху GRBL).
    """
    xs = np.arange(0, X_SIZE_MM, STEP_MM)
    ys = np.arange(0, Y_SIZE_MM, STEP_MM)
    data = np.zeros((len(ys), len(xs)))
    t0 = time.time()

    for j, y in enumerate(ys):

        # Компенсація люфту гвинта CD-ROM (~0.3..0.5 мм):
        # перед кожним рядком відходимо на OVERSHOOT мм назад по X,
        # потім рухаємось у напрямку +X — систематична похибка скасовується
        grbl_send(f'G0 X{-OVERSHOOT:.3f} Y{y:.3f} F{FEED_RATE}')

        for i, x in enumerate(xs):
            # Переміщення до точки вимірювання
            grbl_send(f'G1 X{x:.3f} Y{y:.3f} F{FEED_RATE}')

            # Стабілізація механіки
            time.sleep(SETTLE_MS / 1000.0)

            # Запуск FSM: DARK -> LIGHT -> ΔV -> DATA:XXXX
            data[j, i] = read_photocurrent()

        eta = (time.time() - t0) / (j + 1) * (len(ys) - j - 1)
        print(f'  Рядок {j+1}/{len(ys)}  |  ~{eta/60:.1f} хв залишилось',
              end='\r')

    print(f'\nСканування завершено за {(time.time()-t0)/60:.1f} хв')
    return data, xs, ys