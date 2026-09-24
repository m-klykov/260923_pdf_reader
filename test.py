import pdfplumber
import pandas as pd
import re


def parse_f1_pdf_debug(pdf_path):
    # Настройки для точного распознавания таблиц FIA
    table_settings = {
        # "vertical_strategy": "text",  # Ищем колонки по выравниванию текста
        # "horizontal_strategy": "lines",  # Ищем строки по физическим линиям
        # "snap_tolerance": 3,
    }

    # Стандартные колонки official classification FIA:
    HEADERS_MAIN = [
        "NO",  # Pos (1)
        "DRIVER_NO",  # Driver No (12)
        "DRIVER",  # Driver Name (Kimi ANTONELLI)
        "NAT",  # Национальность (часто пустая ячейка/иконка)
        "SPONSOR_FLAG",  # Пустая ячейка
        "TEAM",  # Команда (Mercedes-AMG PETRONAS F1 Team)
        "LAPS",  # Круги (57)
        "TIME_RETIRED",  # Время / Статус (1:34:23.754)
        "GAP",  # Отрыв от лидера (4.351)
        "INT",  # Отрыв от предыдущей машины (0.738)
        "KPH",  # Средняя скорость (196.024)
        "BEST_TIME",  # Лучший круг (1:36.030)
        "BEST_LAP",  # На каком круге показан лучший результат (57)
        "PTS"  # Очки (25)
    ]

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            print(f"\n==========================================")
            print(f"            СТРАНИЦА {page_num}")
            print(f"==========================================")

            # --- 1. Извлечение шапки и плашек (сырой текст) ---
            raw_text = page.extract_text()
            if raw_text:
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

                print("\n--- Шапка документа (Метаданные / Плашки) ---")
                header_lines = []
                for line in lines:
                    # Останавливаем сбор шапки, когда начинается таблица (первый гонщик или заголовки)
                    # Обычно таблица начинается со слов "NO", "DRIVER", "POS" или первой цифры позиций
                    if line.startswith(("NO", "POS", "1 ", "NC", "FASTEST LAP")):
                        # pass
                        break
                    header_lines.append(line)

                for h_num, h_line in enumerate(header_lines):
                    print(f" [HEADER {h_num}]: {h_line}")

            # --- 2. Извлечение таблиц ---
            tables = page.extract_tables(table_settings)

            if not tables:
                print(f"--- Страница {page_num}: таблицы не найдены ---")
                continue

            for table_num, table in enumerate(tables, start=1):
                print(f"\n=== Страница {page_num} | Таблица {table_num} ===")

                for row in table:
                    # Очищаем ячейки от переносов строк (\n) и лишних пробелов
                    clean_row = [
                        cell.replace('\n', ' ').strip() if cell else ""
                        for cell in row
                    ]

                    # Пропускаем полностью пустые строки
                    if any(clean_row):
                        print(clean_row)

# Пример использования
parse_f1_pdf_debug("data/2026_14_esp_f1_r0_timing_race.pdf")
