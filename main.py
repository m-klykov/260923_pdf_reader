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
        for row in table._rows: # get_table():
            print(row)

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

    converter = PdfConvF1Base(session_type=SessionType.R, doc_type=DocType.TRACK_ANALYSIS)
    res = converter.convert("data/2026_14_esp_f1_q0_timing_trackanalysis_v01.pdf")
    view_result("q On Track Analysis", res)




