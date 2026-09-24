from .m_pdf_wrapper import PDFWrapper
from .m_table_wrapper import TableWrapper


class PdfConvBase:
    def __init__(self):
        pass

    def convert(self, pdf_path: str) -> TableWrapper:
        """
        Извлекает первую таблицу из документа с помощью PDFWrapper.
        Первая строка таблицы принимается за список имен колонок,
        остальные строки — за значения.
        """
        table = TableWrapper()

        # Создаем и загружаем PDF через обертку
        pdf = PDFWrapper()
        pdf.open(pdf_path)

        # Проверяем наличие таблиц в документе
        if pdf.get_tables_count() > 0:
            # Получаем первую таблицу (нумерация с 1)
            first_table = pdf.get_table(table_number=1)

            if first_table and len(first_table) > 0:
                # Первая строка таблицы — заголовки колонок
                col_names = first_table[0]

                # Все последующие строки — данные
                for row_values in first_table[1:]:
                    # Фильтруем полностью пустые строки
                    if row_values and any(row_values):
                        table.add_line(col_names, row_values)

        return table