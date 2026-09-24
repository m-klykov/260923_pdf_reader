from typing import List
from .m_pdf_wrapper import PDFWrapper
from .m_table_wrapper import TableWrapper


class PdfConvBase:
    def __init__(self):
        pass

    def convert(self, pdf_path: str) -> List[TableWrapper]:
        """
        Извлекает все таблицы из документа с помощью PDFWrapper.
        Для каждой таблицы первая строка принимается за список имен колонок,
        остальные строки — за значения.

        :return: Список объектов TableWrapper для каждой найденной таблицы.
        """
        tables_list: List[TableWrapper] = []

        # Создаем и загружаем PDF через обертку
        pdf = PDFWrapper()
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()

        # Итерируемся по всем таблицам документа (сквозная нумерация с 1)
        for table_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(table_number=table_idx)

            if raw_table and len(raw_table) > 0:
                # Создаем обертку с заголовком по умолчанию
                table_wrapper = TableWrapper(title=f"Table #{table_idx}")

                # Первая строка таблицы — заголовки колонок
                col_names = raw_table[0]

                # Все последующие строки — данные
                for row_values in raw_table[1:]:
                    # Фильтруем полностью пустые строки
                    if row_values and any(row_values):
                        table_wrapper.add_line(col_names, row_values)

                tables_list.append(table_wrapper)

        return tables_list