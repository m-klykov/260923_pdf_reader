from typing import List, Optional, Tuple
import pdfplumber

# Тип для задаваемых пользователем относительных координат: ((left, top), (right, bottom))
CropBoxRatio = Tuple[Tuple[float, float], Tuple[float, float]]


class PDFWrapper:
    """
    Класс-обертка над pdfplumber.
    При вызове .open(pdf_path) загружает весь текст и таблицы во внутреннюю память.
    """

    def __init__(self, crop_box: Optional[CropBoxRatio] = None):
        """
        :param crop_box: Кортеж угловых точек полезного контента ((left, top), (right, bottom)).
                         Все значения — вещественные числа от 0.0 до 1.0.
                         Пример: ((0.0, 0.1), (1.0, 0.9)) — обрезать верхние 10% и нижние 10% страницы.
        """
        self.crop_box = crop_box

        # Храним строки текста по страницам: [ ["стр1_строка1", "стр1_строка2"], ["стр2_строка1", ...] ]
        self._page_lines: List[List[str]] = []

        # Храним все таблицы документа сквозным списком
        self._tables: List[List[List[Optional[str]]]] = []

    def open(self, pdf_path: str) -> None:
        """
        Открывает PDF-файл, вычитывает весь текст по страницам
        и собирает все таблицы во внутренние переменные, после чего закрывает файл.
        """

        table_settings = {
            # "vertical_strategy": "text",  # Ищем колонки по выравниванию текста
            # "horizontal_strategy": "text",  # Ищем колонки по выравниванию текста
            # "horizontal_strategy": "lines",  # Ищем строки по физическим линиям
            # "snap_tolerance": 3,
        }

        self._page_lines.clear()
        self._tables.clear()

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Определение полезной области страницы
                target_page = self._apply_crop_if_needed(page)

                # 1. Извлекаем и чистим текстовые строки текущей страницы
                text = target_page.extract_text(layout=False) or ""
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                self._page_lines.append(lines)

                # 2. Извлекаем все таблицы текущей страницы и добавляем их в общий сквозной список
                tables = target_page.extract_tables(table_settings=table_settings) or []
                for table in tables:
                    if table:
                        self._tables.append(table)

    def get_page_count(self) -> int:
        """Возвращает общее количество страниц в документе."""
        return len(self._page_lines)

    def get_lines(self, page_number: int = 1) -> List[str]:
        """
        Возвращает массив строк текста для указанной страницы.

        :param page_number: Номер страницы (начиная с 1).
        """
        if page_number < 1 or page_number > self.get_page_count():
            raise IndexError(
                f"Запрошена страница {page_number}, но в документе всего страниц: {self.get_page_count()}"
            )

        return self._page_lines[page_number - 1]

    def get_tables_count(self) -> int:
        """Возвращает общее количество таблиц в документе."""
        return len(self._tables)

    def get_table(self, table_number: int = 1) -> List[List[Optional[str]]]:
        """
        Возвращает таблицу по ее номеру (сквозная нумерация).

        :param table_number: Номер таблицы (начиная с 1).
        """
        if table_number < 1 or table_number > self.get_tables_count():
            raise IndexError(
                f"Запрошена таблица {table_number}, но в документе всего таблиц: {self.get_tables_count()}"
            )

        return self._tables[table_number - 1]

    def _apply_crop_if_needed(self, page: pdfplumber.page.Page) -> pdfplumber.page.Page:
        """
        Пересчитывает относительные координаты crop_box (0.0..1.0)
        в абсолютные точки PDF (0..width, 0..height) и возвращает обрезанную страницу.
        """
        if not self.crop_box:
            return page

        (left_r, top_r), (right_r, bottom_r) = self.crop_box

        # Валидация входных значений
        if not (0.0 <= left_r < right_r <= 1.0 and 0.0 <= top_r < bottom_r <= 1.0):
            raise ValueError(
                f"Некорректные значения crop_box: {self.crop_box}. "
                "Координаты должны быть от 0.0 до 1.0, при этом left < right и top < bottom."
            )

        # Пересчет в абсолютные координаты PDF (в пунктах)
        page_width = float(page.width)
        page_height = float(page.height)

        x0 = left_r * page_width
        top = top_r * page_height
        x1 = right_r * page_width
        bottom = bottom_r * page_height

        # Bounding box в pdfplumber: (x0, top, x1, bottom)
        bounding_box = (x0, top, x1, bottom)

        print(f"bounding: {bounding_box}")

        cropped_page = page.crop(bounding_box)

        # strict_page = cropped_page.filter(
        #     lambda obj: obj.get("top", 0) <= bottom
        # )

        return cropped_page
