from pdf_reader.pc_f1_base import PdfConvF1Base, SessionType, DocType

# ==========================================
# Пример использования
# ==========================================

def view_result(title, res):
    print()
    print(f"=== {title} ===")
    print()
    for table in res:
        print(f"--- {table.title} ---")
        for row in table.get_rows(): # get_table():
            print(row)


import sys
from typing import List, Tuple, Callable


def run_cli():
    """Интерактивное консольное меню для выбора файла и типа парсинга."""

    # Список вариантов: (Заголовок, SessionType, DocType, Путь к файлу)
    test_cases: List[Tuple[str, SessionType, DocType, str]] = [
        # --- CLASSIFICATION ---
        ("P1 Classification", SessionType.P1, DocType.CLASSIFICATION,
         "data/2026_14_esp_f1_p1_timing_classification_v01.pdf"),
        ("Q Classification", SessionType.Q, DocType.CLASSIFICATION,
         "data/2026_14_esp_f1_q0_timing_classification_v01.pdf"),
        ("Race Classification", SessionType.R, DocType.CLASSIFICATION,
         "data/2026_14_esp_f1_r0_timing_classification_v01.pdf"),

        # --- SPEEDS & SECTORS ---
        ("Race Maximum Speeds", SessionType.R, DocType.MAXIMUM_SPEEDS,
         "data/2026_14_esp_f1_r0_timing_maximumspeeds_v01.pdf"),
        ("Race Best Sector Times", SessionType.R, DocType.BEST_SECTOR_TIMES,
         "data/2026_14_esp_f1_r0_timing_bestsectortimes_v01.pdf"),

        # --- MESSAGES & SECTOR ANALYSIS ---
        ("Race Control Messages", SessionType.R, DocType.RACE_CONTROL_MESSAGES,
         "data/2026_14_esp_f1_r0_timing_racecontrolmessages_v01.pdf"),
        ("P1 Sector Analysis", SessionType.P1, DocType.SECTOR_ANALYSIS,
         "data/2026_14_esp_f1_p1_timing_sectoranalysis_v01.pdf"),
        ("Q Sector Analysis", SessionType.Q, DocType.SECTOR_ANALYSIS,
         "data/2026_14_esp_f1_q0_timing_sectoranalysis_v01.pdf"),
        ("Race Sector Analysis", SessionType.R, DocType.SECTOR_ANALYSIS,
         "data/2026_14_esp_f1_r0_timing_sectoranalysis_v01.pdf"),

        # --- LAP & TRACK ANALYSIS ---
        ("P1 Lap Times", SessionType.P1, DocType.LAP_TIMES, "data/2026_14_esp_f1_p1_timing_laptimes_v01.pdf"),
        ("Q On Track Analysis", SessionType.Q, DocType.TRACK_ANALYSIS,
         "data/2026_14_esp_f1_q0_timing_trackanalysis_v01.pdf"),
        ("Race Lap Analysis", SessionType.R, DocType.LAP_ANALYSIS, "data/2026_14_esp_f1_r0_timing_lapanalysis_v01.pdf"),
        ("Race Fastest Laps", SessionType.R, DocType.FASTEST_LAPS, "data/2026_14_esp_f1_r0_timing_fastestlaps_v01.pdf"),

        # --- CHARTS & SUMMARY ---
        ("Race History Chart", SessionType.R, DocType.HISTORY_CHART,
         "data/2026_14_esp_f1_r0_timing_historychart_v01.pdf"),
        ("Race Pit Stop Summary", SessionType.R, DocType.PIT_STOP_SUMMARY,
         "data/2026_14_esp_f1_r0_timing_pitstopsummary_v01.pdf"),
        ("Race Lap Chart", SessionType.R, DocType.LAP_CHART, "data/2026_14_esp_f1_r0_timing_lapchart_v01.pdf"),

        # --- CHAMPIONSHIPS ---
        ("Drivers Championship", SessionType.R, DocType.DRIVERS_CHAMPIONSHIP,
         "data/2026_14_esp_f1_r0_timing_driverschampionship_v01.pdf"),
        ("Constructors Championship", SessionType.R, DocType.CONSTRUCTORS_CHAMPIONSHIP,
         "data/2026_14_esp_f1_r0_timing_constructorschampionship_v01.pdf"),
    ]

    while True:
        print("\n" + "=" * 50)
        print("          F1 PDF PARSER - ТЕСТОВОЕ МЕНЮ          ")
        print("=" * 50)

        for idx, (label, _, _, _) in enumerate(test_cases, start=1):
            print(f" [{idx:2d}] {label}")

        print(" [ 0] Выход")
        print("=" * 50)

        choice = input("Выберите номер отчета для просмотра: ").strip()

        if choice == "0":
            print("Завершение работы.")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(test_cases)):
            print("\n⚠️ Ошибка: Введите корректный номер из списка!")
            continue

        # Получаем выбранный пресет
        label, session_type, doc_type, pdf_path = test_cases[int(choice) - 1]

        print(f"\n🔄 Запуск конвертации: {label}...")
        print(f"📄 Файл: {pdf_path}")

        try:
            converter = PdfConvF1Base(session_type=session_type, doc_type=doc_type)
            res = converter.convert(pdf_path)
            view_result(label, res)
        except NotImplementedError as e:
            print(f"\nЭтот тип документа еще не реализован: {e}")
        except FileNotFoundError:
            print(f"\nФайл не найден по пути: {pdf_path}")
        except Exception as e:
            print(f"\nОшибка при обработке файла: {e}")

        input("\nНажмите Enter, чтобы вернуться в меню...")


if __name__ == "__main__":

    # converter = PdfConvF1Base(session_type=SessionType.P1,doc_type=DocType.CLASSIFICATION)
    # res = converter.convert("data/2026_14_esp_f1_p1_timing_classification_v01.pdf")
    # view_result("p1 cla",res)

    # converter = PdfConvF1Base(session_type=SessionType.Q, doc_type=DocType.CLASSIFICATION)
    # res = converter.convert("data/2026_14_esp_f1_q0_timing_classification_v01.pdf")
    # view_result("p1 cla", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.CLASSIFICATION)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_classification_v01.pdf")
    # view_result("p1 cla", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.MAXIMUM_SPEEDS)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_maximumspeeds_v01.pdf")
    # view_result("race max speeds", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.BEST_SECTOR_TIMES)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_bestsectortimes_v01.pdf")
    # view_result("Race Best Sector Times", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.RACE_CONTROL_MESSAGES)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_racecontrolmessages_v01.pdf")
    # view_result("r Race Control Messages", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.SECTOR_ANALYSIS)
    # res = converter.convert("data/2026_14_esp_f1_p1_timing_sectoranalysis_v01.pdf")
    # view_result("p Sector Analysis", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.SECTOR_ANALYSIS)
    # res = converter.convert("data/2026_14_esp_f1_q0_timing_sectoranalysis_v01.pdf")
    # view_result("q Sector Analysis", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.SECTOR_ANALYSIS)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_sectoranalysis_v01.pdf")
    # view_result("r Sector Analysis", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.LAP_TIMES)
    # res = converter.convert("data/2026_14_esp_f1_p1_timing_laptimes_v01.pdf")
    # # res = converter.convert("data/2026_14_esp_f1_q0_timing_laptimes_v01.pdf")
    # view_result("q Lap Times", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.TRACK_ANALYSIS)
    # res = converter.convert("data/2026_14_esp_f1_q0_timing_trackanalysis_v01.pdf")
    # view_result("q On Track Analysis", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.LAP_ANALYSIS)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_lapanalysis_v01.pdf")
    # view_result("Race Lap Analysis", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.FASTEST_LAPS)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_fastestlaps_v01.pdf")
    # view_result("Race Fastest Laps", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.HISTORY_CHART)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_historychart_v01.pdf")
    # view_result("Race History Chart", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.PIT_STOP_SUMMARY)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_pitstopsummary_v01.pdf")
    # view_result("Race Pit Stop Summary", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.LAP_CHART)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_lapchart_v01.pdf")
    # view_result("Race Lap Chart", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.DRIVERS_CHAMPIONSHIP)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_driverschampionship_v01.pdf")
    # view_result("Drivers Championship", res)

    # converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.CONSTRUCTORS_CHAMPIONSHIP)
    # res = converter.convert("data/2026_14_esp_f1_r0_timing_constructorschampionship_v01.pdf")
    # view_result("Constructors Championship", res)

    run_cli()




