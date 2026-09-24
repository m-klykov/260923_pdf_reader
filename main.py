from pdf_reader.pc_f1_race import PdfConvF1Race

# ==========================================
# Пример использования
# ==========================================
if __name__ == "__main__":
    converter = PdfConvF1Race()
    acc = converter.convert("data/2026_14_esp_f1_r0_timing_race.pdf")

    for row in acc.get_table():
        print(row)

