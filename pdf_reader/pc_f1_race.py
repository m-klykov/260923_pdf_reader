from .m_pdf_wrapper import PDFWrapper
from .m_table_wrapper import TableWrapper
from .pc_base import PdfConvBase


class PdfConvF1Race(PdfConvBase):
    # Явное определение схемы колонок в нижнем регистре
    COLUMNS_CLASSIFIED = [
        "no",
        "driver_no",
        "driver",
        "nat",
        "sponsor_flag",
        "team",
        "laps",
        "time_retired",
        "gap",
        "int",
        "kph",
        "best_time",
        "best_lap",
        "pts",
    ]

    # Схема для второй таблицы (NOT CLASSIFIED) — без первой колонки "no"
    COLUMNS_NOT_CLASSIFIED = COLUMNS_CLASSIFIED[1:]

    def convert(self, pdf_path: str) -> TableWrapper:
        """
        Извлекает классифицированных гонщиков из 1-й таблицы 
        и неквалифицированных из 2-й таблицы с помощью PDFWrapper.
        """
        table = TableWrapper()

        # Загружаем PDF во внутреннюю память обертки
        pdf = PDFWrapper()
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()

        # 1. Обработка первой таблицы (финишировавшие гонщики)
        if tables_count >= 1:
            first_table = pdf.get_table(table_number=1)
            for row_values in first_table:
                if row_values and any(row_values):
                    table.add_line(self.COLUMNS_CLASSIFIED, row_values)

        # 2. Обработка второй таблицы (NOT CLASSIFIED)
        if tables_count >= 2:
            second_table = pdf.get_table(table_number=2)
            for row_values in second_table:
                if row_values and any(row_values):
                    # Пропускаем служебные заголовки вроде "NOT CLASSIFIED"
                    first_cell = str(row_values[0]).upper()
                    if "NOT CLASSIFIED" in first_cell:
                        continue

                    # Добавляем данные без первой колонки
                    table.add_line(self.COLUMNS_NOT_CLASSIFIED, row_values)

        return table