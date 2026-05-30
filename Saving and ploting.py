import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import csv

def normalize(data: np.ndarray) -> np.ndarray:
    """Лінійне нормування до діапазону [0, 1]."""
    mn, mx = data.min(), data.max()
    return (data - mn) / (mx - mn + 1e-12)

def correct_background(data: np.ndarray, bg_rows: int = 5) -> np.ndarray:
    """
    Корекція нерівномірного фону: відніманням середнього
    по перших і останніх рядках зображення (поза зразком).
    """
    bg = np.mean(np.vstack([data[:bg_rows], data[-bg_rows:]]), axis=0)
    return np.clip(data - bg, 0, None)

def save_csv(data: np.ndarray, xs: np.ndarray,
             ys: np.ndarray, path: str = 'lbic_result.csv'):
    with open(path, 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['Y/X'] + [f'{x:.3f}' for x in xs])
        for j, y in enumerate(ys):
            wr.writerow([f'{y:.3f}'] + list(data[j]))
    print(f'CSV збережено: {path}')

def plot_lbic_map(data: np.ndarray, xs: np.ndarray,
                  ys: np.ndarray, smooth: float = 0.5):
    """Теплова карта розподілу фотоструму + гістограма сигналу."""
    z = normalize(correct_background(data))
    if smooth > 0:
        z = gaussian_filter(z, sigma=smooth)  # гаусове згладжування

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # Теплова карта (LBIC-map)
    im = ax1.imshow(z, origin='lower', cmap='hot',
                    extent=[xs[0], xs[-1], ys[0], ys[-1]],
                    aspect='equal', vmin=0, vmax=1)
    plt.colorbar(im, ax=ax1, label='Нормований фотострум, відн. од.')
    ax1.set(xlabel='X, мм', ylabel='Y, мм',
            title='LBIC-карта розподілу фотоструму')

    # Гістограма розподілу сигналу
    ax2.hist(z.ravel(), bins=80, color='#cc3300',
             edgecolor='white', linewidth=0.3)
    ax2.set(xlabel='Нормований фотострум, відн. од.',
            ylabel='Кількість пікселів',
            title='Гістограма розподілу сигналу')

    plt.tight_layout()
    plt.savefig('lbic_map.png', dpi=200, bbox_inches='tight')
    print('Карту збережено: lbic_map.png')