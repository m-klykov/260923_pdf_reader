from typing import List, Optional, Tuple, Dict, Any
import pdfplumber

CropBoxRatio = Tuple[Tuple[float, float], Tuple[float, float]]


class PDFWrapper:
    """
    Класс-обертка над pdfplumber.
    При вызове .open(pdf_path) загружает весь текст и таблицы во внутреннюю память,
    а также запоминает координаты каждой таблицы для анализа контекста выше/вокруг нее.
    """

    def __init__(self, crop_box: Optional[CropBoxRatio] = None):
        self.crop_box = crop_box

        # Храним строки текста по страницам
        self._page_lines: List[List[str]] = []

        # Храним таблицы документа сквозным списком
        self._tables: List[List[List[Optional[str]]]] = []

        # Храним метаданные таблиц (индекс страницы и bbox: x0, top, x1, bottom)
        self._table_meta: List[Dict[str, Any]] = []

        # Сохраняем ссылки на pdfplumber pages для точечной работы с геопроцессингом
        self._pages_cache: List[pdfplumber.page.Page] = []

    def open(self, pdf_path: str) -> None:
        table_settings = {}

        self._page_lines.clear()
        self._tables.clear()
        self._table_meta.clear()
        self._pages_cache.clear()

        # Важно: не используем context manager 'with', если планируем
        # делать отложенный extract_text из cropped-областей страниц.
        # Загружаем PDF в память через pdfplumber.open.
        pdf = pdfplumber.open(pdf_path)

        for page_idx, page in enumerate(pdf.pages):
            target_page = self._apply_crop_if_needed(page)
            self._pages_cache.append(target_page)

            # 1. Извлекаем текстовые строки текущей страницы
            text = target_page.extract_text(layout=False) or ""
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            self._page_lines.append(lines)

            # 2. Поиск таблиц с извлечением их координат (find_tables)
            found_tables = target_page.find_tables(table_settings=table_settings) or []
            for t in found_tables:
                extracted_data = t.extract()
                if extracted_data:
                    self._tables.append(extracted_data)
                    self._table_meta.append({
                        "page_idx": page_idx,
                        "bbox": t.bbox,  # (x0, top, x1, bottom)
                    })

    def get_page_count(self) -> int:
        return len(self._page_lines)

    def get_lines(self, page_number: int = 1) -> List[str]:
        if page_number < 1 or page_number > self.get_page_count():
            raise IndexError(
                f"Запрошена страница {page_number}, но в документе всего страниц: {self.get_page_count()}"
            )
        return self._page_lines[page_number - 1]

    def get_tables_count(self) -> int:
        return len(self._tables)

    def get_table(self, table_number: int = 1) -> Optional[List[List[Optional[str]]]]:
        if table_number < 1 or table_number > self.get_tables_count():
            return None
        return self._tables[table_number - 1]

    def get_text_above_table(self,
        table_number: int,
        margin_height: float = 30.0,
        margin_offset: float = 5.0,

    ) -> str:
        """
        Извлекает текст из геометрической области СТРОГО НАД таблицей.

        :param table_number: Номер таблицы (начиная с 1).
        :param margin_height: Высота области над таблицей в пунктах (по умолчанию 30 pt).
        :param margin_offset: насколько приподнять область заголовка над таблицей
                              чтобы пропустить названия колонок
        :return: Строка с найденным текстом над таблицей.
        """
        if table_number < 1 or table_number > self.get_tables_count():
            return ""

        meta = self._table_meta[table_number - 1]
        page_idx = meta["page_idx"]
        x0, top, x1, _ = meta["bbox"]

        page = self._pages_cache[page_idx]

        # Формируем bbox области над таблицей
        crop_x0 = max(0.0, x0 - 5.0)  # небольшая погрешность влево
        crop_top = max(0.0, top - margin_height - margin_offset)
        crop_x1 = min(float(page.width), x1 + 5.0)
        crop_bottom = top - margin_offset
        if crop_bottom <= crop_top:
            return ""

        # Вырезаем область над таблицей и извлекаем из неё текст
        above_crop = (crop_x0, crop_top, crop_x1, crop_bottom)
        cropped_region = page.crop(above_crop)

        text = cropped_region.extract_text(layout=False) or ""
        return text.strip()

    def _apply_crop_if_needed(self, page: pdfplumber.page.Page) -> pdfplumber.page.Page:
        if not self.crop_box:
            return page

        (left_r, top_r), (right_r, bottom_r) = self.crop_box

        if not (0.0 <= left_r < right_r <= 1.0 and 0.0 <= top_r < bottom_r <= 1.0):
            raise ValueError(f"Некорректные значения crop_box: {self.crop_box}")

        page_width = float(page.width)
        page_height = float(page.height)

        bounding_box = (
            left_r * page_width,
            top_r * page_height,
            right_r * page_width,
            bottom_r * page_height,
        )

        return page.crop(bounding_box)