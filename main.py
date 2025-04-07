

import math
import matplotlib.pyplot as plt
from typing import List
from datetime import datetime
import os

M_PI = math.pi

# Параметри квантування
M_levels = 256
num_bits = 8


def analog_signal(t: float, m: float) -> float:
    return -m * math.cos(5.65 * t + M_PI / m)


def discretize_signal(N: int, Td: float, m: float) -> List[float]:
    return [analog_signal(n * Td, m) for n in range(N + 1)]


def calculate_relative_error(original: float, reconstructed: float) -> float:
    if abs(original) < 1e-10:
        return float('nan')
    return abs((original - reconstructed) / original) * 100.0


def save_table_to_png(data, headers, title, filename):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')

    # Создаем таблицу
    table = ax.table(cellText=data, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Устанавливаем заголовок
    plt.title(title, fontsize=12, pad=20)

    # Сохраняем в файл
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Таблиця збережена в файл: {filename}")


def main():
    print("--- Введення вихідних даних ---")

    while True:
        try:
            N = int(input("Введіть кількість відліків (N): "))
            if N < 0:
                raise ValueError
            break
        except ValueError:
            print("Некоректне введення. Введіть ціле невід'ємне число.")

    while True:
        try:
            Td = float(input("Введіть період дискретизації (Td): "))
            if Td <= 0:
                raise ValueError
            break
        except ValueError:
            print("Некоректне введення. Введіть додатне число.")

    while True:
        try:
            m = float(input("Введіть порядковий номер групи (m): "))
            if m <= 0:
                raise ValueError
            break
        except ValueError:
            print("Некоректне введення. Введіть додатне число.")

    print("---------------------------------\n")

    # Создаем папку для результатов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"results_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)

    # Розрахунок параметрів
    amplitude = m
    dynamic_range = 2.0 * amplitude
    Q_step = dynamic_range / (M_levels - 1.0)

    print("--- Розраховані параметри ---")
    print(f"Амплітуда сигналу (A = m групи): {amplitude:.5f}")
    print(f"Кількість рівнів квантування (M): {M_levels}")
    print(f"Розрядність коду (m_roz=log2(M)): {num_bits} біт")
    print(f"Крок квантування (Q = 2*A/(M-1)): {Q_step:.8f}")
    print("--------------------------------\n")

    # Дискретизація
    s_n = discretize_signal(N, Td, m)

    # Квантування
    Stu_n = []
    Sru_n = []
    Sts_n = []
    Srs_n = []

    for value in s_n:
        # Беззнакове усечення
        stu = int((value + amplitude) / Q_step)
        if stu < 0:
            stu = 0
        elif stu >= M_levels:
            stu = M_levels - 1
        Stu_n.append(stu)

        # Беззнакове округлення
        sru = round((value + amplitude) / Q_step)
        if sru < 0:
            sru = 0
        elif sru >= M_levels:
            sru = M_levels - 1
        Sru_n.append(sru)

        # Знакове усечення
        sts = int(value / Q_step)
        min_signed = -(M_levels // 2)
        max_signed = (M_levels // 2) - 1
        if sts < min_signed:
            sts = min_signed
        elif sts > max_signed:
            sts = max_signed
        Sts_n.append(sts)

        # Знакове округлення
        srs = round(value / Q_step)
        if srs < min_signed:
            srs = min_signed
        elif srs > max_signed:
            srs = max_signed
        Srs_n.append(srs)

    # Відновлення сигналу
    Atu_n = [stu * Q_step - amplitude for stu in Stu_n]
    Aru_n = [sru * Q_step - amplitude for sru in Sru_n]
    Ats_n = [sts * Q_step for sts in Sts_n]
    Ars_n = [srs * Q_step for srs in Srs_n]

    # Подготовка данных для таблицы Дискретизации и Квантования
    discr_quant_data = []
    for n in range(N + 1):
        discr_quant_data.append([
            str(n),
            f"{n * Td:.3f}",
            f"{s_n[n]:.4f}",
            str(Stu_n[n]),
            str(Sru_n[n]),
            str(Sts_n[n]),
            str(Srs_n[n])
        ])

    # Сохранение таблицы Дискретизации и Квантования
    discr_quant_filename = os.path.join(results_dir, "discretization_quantization.png")
    save_table_to_png(
        discr_quant_data,
        ["n", "t=n*Td", "s(n)", "Stu(n)", "Sru(n)", "Sts(n)", "Srs(n)"],
        "Дискретизація та Квантування",
        discr_quant_filename
    )

    # Подготовка данных для таблицы Восстановления сигнала
    reconstruction_data = []
    for n in range(N + 1):
        reconstruction_data.append([
            str(n),
            f"{s_n[n]:.4f}",
            f"{Atu_n[n]:.4f}",
            f"{Aru_n[n]:.4f}",
            f"{Ats_n[n]:.4f}",
            f"{Ars_n[n]:.4f}"
        ])

    # Сохранение таблицы Восстановления сигнала
    reconstruction_filename = os.path.join(results_dir, "signal_reconstruction.png")
    save_table_to_png(
        reconstruction_data,
        ["n", "s(n) Ориг.", "Atu(n) БЗ_Ур", "Aru(n) БЗ_Ок", "Ats(n) ЗЗ_Ур", "Ars(n) ЗЗ_Ок"],
        "Відновлення сигналу",
        reconstruction_filename
    )

    # Розрахунок середньої відносної похибки
    total_err = [0.0, 0.0, 0.0, 0.0]  # Atu, Aru, Ats, Ars
    count = [0, 0, 0, 0]

    for n in range(N + 1):
        current_s = s_n[n]
        errors = [
            calculate_relative_error(current_s, Atu_n[n]),
            calculate_relative_error(current_s, Aru_n[n]),
            calculate_relative_error(current_s, Ats_n[n]),
            calculate_relative_error(current_s, Ars_n[n])
        ]

        for i in range(4):
            if not math.isnan(errors[i]):
                total_err[i] += errors[i]
                count[i] += 1

    avg_errors = [
        total_err[0] / count[0] if count[0] > 0 else 0.0,
        total_err[1] / count[1] if count[1] > 0 else 0.0,
        total_err[2] / count[2] if count[2] > 0 else 0.0,
        total_err[3] / count[3] if count[3] > 0 else 0.0
    ]

    # Подготовка данных для таблицы ошибок
    error_data = [
        ["БезЗн, Уріз", f"{avg_errors[0]:.3f} %"],
        ["БезЗн, Окр", f"{avg_errors[1]:.3f} %"],
        ["ЗіЗн, Уріз", f"{avg_errors[2]:.3f} %"],
        ["ЗіЗн, Окр", f"{avg_errors[3]:.3f} %"]
    ]

    # Сохранение таблицы ошибок
    error_filename = os.path.join(results_dir, "error_calculation.png")
    save_table_to_png(
        error_data,
        ["Метод", "Середня похибка"],
        "Розрахунок середньої відносної похибки",
        error_filename
    )

    print(f"\nВсі результати збережено у папці: {results_dir}")


if __name__ == "__main__":
    main()