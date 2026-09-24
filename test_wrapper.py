from pdf_reader.m_pdf_wrapper import PDFWrapper

if __name__ == "__main__":
    # 1. Создаем экземпляр без параметров
    area = ( (0, 100/740), (1 , 668/740 ))
    pdf = PDFWrapper( area )

    file_name = "data/2026_14_esp_f1_q0_timing_laptimes_v01.pdf"

    # 2. Считываем данные из файла
    pdf.open(file_name)

    # 3. Работаем со страницами
    print(f"Всего страниц: {pdf.get_page_count()}")
    if pdf.get_page_count() > 0:
        lines_page_1 = pdf.get_lines(page_number=1)
        print(f"Первые строки 1-й страницы:")

        for n, v in enumerate(lines_page_1[:2]):
            print(f"{n}. {v}")

    # 4. Работаем с таблицами
    print(f"\nВсего таблиц во всем документе: {pdf.get_tables_count()}")
    if pdf.get_tables_count() > 0:

        # Берём 1-ю таблицу
        first_table = pdf.get_table(table_number=6)
        print(f"Первая строка 1-й таблицы: {first_table[0]}")
        tab_tit = pdf.get_text_above_table(
            table_number=6, margin_height=15.0, margin_offset=15)
        print(f"Заголовок 1-й таблицы: {tab_tit}")

        for line in first_table:
            print(f"| {line}")

        # Если есть 2-я таблица (например, NOT CLASSIFIED)
        if pdf.get_tables_count() >= 2:
            second_table = pdf.get_table(table_number=2)
            print(f"Первая строка 2-й таблицы: {second_table[0]}")