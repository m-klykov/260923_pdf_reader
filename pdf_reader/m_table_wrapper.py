import re

class TableWrapper:
    def __init__(self,title : str=""):
        self.title = title
        # Храним порядок уникальных имен колонок
        self._columns_order = {}
        # Список строк: каждый элемент — словарь {"ИМЯ_КОЛОНКИ": "ЗНАЧЕНИЕ"}
        self._rows = []

    @staticmethod
    def _clean_col_name(col_name: str) -> str:
        """Очищает имя колонки от переносов строк, табуляций и лишних пробелов."""
        if not col_name:
            return ""
        # Заменяем переносы строк и табуляции на пробел
        cleaned = re.sub(r'[\r\n\t]+', ' ', str(col_name))
        # Схлопываем множественные пробелы и удаляем краевые
        return re.sub(r'\s+', ' ', cleaned).strip()

    @staticmethod
    def _clean_value(val: str) -> str:
        """Очищает значение ячейки от переносов строк, табуляций и лишних пробелов."""
        if val is None:
            return ""
        # return str(val)
        # Заменяем переносы строк и табуляции на пробел
        cleaned = re.sub(r'[\r\n\t]+', ' ', str(val))
        # Схлопываем множественные пробелы и удаляем краевые
        return re.sub(r'\s+', ' ', cleaned).strip()

    def add_line(self, col_names: list[str], values: list[str]) -> None:
        """
        Добавляет строку в аккумулятор.

        - Поведение по длине: zip гарантирует обработку ровно min(len(col_names), len(values)) элементов.
          Лишние значения (если values больше) игнорируются.
          Если values меньше, обработаются только имеющиеся пары, а нехватающие колонки в словарь не попадут.
        """
        row_dict = {}

        # zip прекращает итерацию, как только закончится один из списков
        for raw_col, raw_val in zip(col_names, values):
            clean_col = self._clean_col_name(raw_col)

            # Пропускаем пустые имена колонок
            if not clean_col:
                continue

            clean_val = self._clean_value(raw_val)

            # Сохраняем имя колонки в общий порядок (если встретили впервые)
            self._columns_order[clean_col] = True

            # Добавляем очищенную пару в словарь текущей строки
            row_dict[clean_col] = clean_val

        # Записываем строку, если в ней есть хотя бы одна валидная колонка
        if row_dict:
            self._rows.append(row_dict)

    def get_table(self) -> list[list[str]]:
        """
        Возвращает двумерный массив строк:
        - 1-я строка: список всех уникальных колонок.
        - Последующие: значения для каждой строки (или '' если колонка отсутствовала).
        """
        columns = list(self._columns_order.keys())
        table = [columns]

        for row_dict in self._rows:
            # Если колонка не определялась для данной строки, подставляется ''
            row_values = [row_dict.get(col, "") for col in columns]
            table.append(row_values)

        return table