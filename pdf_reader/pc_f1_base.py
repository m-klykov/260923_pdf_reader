from enum import Enum
from typing import List, Optional, Tuple

from .m_pdf_wrapper import PDFWrapper
from .m_table_wrapper import TableWrapper
from .pc_base import PdfConvBase


class SessionType(Enum):
    """Типы сессий уик-энда Формулы-1."""
    P1 = "p1"  # Practice 1
    P2 = "p2"  # Practice 2
    P3 = "p3"  # Practice 3
    Q = "q0"  # Qualifying
    SQ = "sq"  # Sprint Shootout / Sprint Qualifying
    S = "s0"  # Sprint Race
    R = "r0"  # Race


class DocType(Enum):
    """Типы официальных отчетов/документов FIA."""
    CLASSIFICATION = "classification" # P,Q,R
    MAXIMUM_SPEEDS = "maximumspeeds" # P,Q,R
    BEST_SECTOR_TIMES = "bestsectortimes"
    LAP_TIMES = "laptimes"
    RACE_CONTROL_MESSAGES = "racecontrolmessages"
    SECTOR_ANALYSIS = "sectoranalysis"
    TRACK_ANALYSIS = "trackanalysis"
    WEATHER_REPORT = "weatherreport"
    CONSTRUCTORS_CHAMPIONSHIP = "constructorschampionship"
    DRIVERS_CHAMPIONSHIP = "driverschampionship"
    FASTEST_LAPS = "fastestlaps"
    HISTORY_CHART = "historychart"
    LAP_ANALYSIS = "lapanalysis"
    LAP_CHART = "lapchart"
    PIT_STOP_SUMMARY = "pitstopsummary"


class PdfConvF1Base(PdfConvBase):
    """Базовый парсер документов Формулы-1."""

    # Список колонок для итоговых таблиц сессий практик (P1, P2, P3)
    PRACTICE_CLASSIFICATION_COLUMNS = [
        "pos", "no", "driver", "", "", "", "entrant",
        "time", "laps", "gap", "int", "kmh", "time_of_day"
    ]

    # Список колонок для квал (R)
    QUALIFYING_CLASSIFICATION_COLUMNS = [
        "pos", "no", "driver", "", "", "entrant",
        "q1_time", "q1_laps", "q1_proc", "q1_dtime",
        "q2_time", "q2_laps", "q2_dtime",
        "q3_time", "q3_laps", "q3_dtime",
    ]

    # Список колонок для гонок (R)
    RACE_CLASSIFICATION_COLUMNS = [
        "pos", "no", "driver", "", "", "entrant",
        "laps", "time",  "gap", "int", "kmh",
        "fastest", "on", "pts"
    ]

    # Список колонок для квал (R)
    MAXIMUM_SPEEDS_COLUMNS = [
        "pos", "no", "driver", "kmh",
    ]

    # Список колонок для квал (R)
    BEST_SECTOR_TIMES_COLUMNS = [
        "pos", "no", "driver", "time",
    ]

    def __init__(
            self,
            session_type: SessionType,
            doc_type: DocType,
            crop_box: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
    ):
        super().__init__()
        self.session_type = session_type
        self.doc_type = doc_type
        self.crop_box = crop_box

    # =========================================================================
    # 1. ДИСПЕТЧЕР (Точка входа)
    # =========================================================================

    def convert(self, pdf_path: str) -> List[TableWrapper]:
        """
        Метод-диспетчер. Направляет обработку в соответствующий метод
        в зависимости от DocType или выбрасывает ошибку.
        """
        match self.doc_type:
            case DocType.CLASSIFICATION:
                return self._convert_classification(pdf_path)
            case DocType.MAXIMUM_SPEEDS:
                return self._convert_max_speeds(pdf_path)
            case DocType.BEST_SECTOR_TIMES:
                return self._convert_best_sector_times(pdf_path)
            case _:
                raise NotImplementedError(
                    f"Конвертация для типа документа '{self.doc_type.value}' еще не реализована."
                )

    # =========================================================================
    # 2. СПЕЦИАЛИЗИРОВАННЫЕ МЕТОДЫ КОНВЕРТАЦИИ
    # =========================================================================

    def _convert_classification(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа CLASSIFICATION."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        if pdf.get_tables_count() == 0:
            return []

        # Создаем главный враппер таблицы
        main_title = "Classification"
        table_wrapper = TableWrapper(title=main_title)

        match self.session_type:
            case SessionType.P1 | SessionType.P2 | SessionType.P3:
                # Извлекаем сырые строки из 1-й таблицы PDF
                raw_table = pdf.get_table(table_number=1) or []

                # Заполняем TableWrapper через хелпер
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.PRACTICE_CLASSIFICATION_COLUMNS,
                    rows=raw_table
                )
                return [table_wrapper]

            case SessionType.Q:
                # Извлекаем сырые строки из 1-й таблицы PDF
                raw_table = pdf.get_table(table_number=1) or []

                # Заполняем TableWrapper через хелпер
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.QUALIFYING_CLASSIFICATION_COLUMNS,
                    rows=raw_table
                )

                return [table_wrapper]

            case SessionType.R:
                # Извлекаем сырые строки из 1-й таблицы PDF
                raw_table = pdf.get_table(table_number=1) or []

                # Заполняем TableWrapper через хелпер
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.RACE_CLASSIFICATION_COLUMNS,
                    rows=raw_table
                )

                if pdf.get_tables_count() > 1:

                    raw_table = pdf.get_table(table_number=2)
                    # Заполняем TableWrapper через хелпер
                    self._append_rows(
                        table_wrapper=table_wrapper,
                        columns=self.RACE_CLASSIFICATION_COLUMNS,
                        rows=raw_table,
                        skip_first_col=True,
                        ignore_keywords=["NOT CLASSIFIED"]
                    )


                return [table_wrapper]

            case _:
                raise NotImplementedError(
                    f"Обработка классификации для сессии '{self.session_type.value}' еще не реализована."
                )

    def _convert_max_speeds(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа CLASSIFICATION."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        if pdf.get_tables_count() == 0:
            return []

        res = []

        # получаем Speed Trap
        raw_table = pdf.get_table(table_number=1)
        if raw_table:
            table_wrapper = TableWrapper(title="Speed Trap")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.MAXIMUM_SPEEDS_COLUMNS,
                rows=raw_table
            )
            res.append(table_wrapper)

        # получаем Finish Line
        raw_table = pdf.get_table(table_number=2)
        if raw_table:
            table_wrapper = TableWrapper(title="Finish Line")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.MAXIMUM_SPEEDS_COLUMNS,
                rows=raw_table,
                num_first_col=True
            )
            res.append(table_wrapper)

        # получаем Intermediate 1
        raw_table = pdf.get_table(table_number=3)
        if raw_table:
            table_wrapper = TableWrapper(title="Intermediate 1")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.MAXIMUM_SPEEDS_COLUMNS,
                rows=raw_table,
                num_first_col=True
            )
            res.append(table_wrapper)


        # получаем Intermediate 2
        raw_table = pdf.get_table(table_number=4)
        if raw_table:
            table_wrapper = TableWrapper(title="Intermediate 2")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.MAXIMUM_SPEEDS_COLUMNS,
                rows=raw_table,
                num_first_col=True
            )
            res.append(table_wrapper)

        return res

    def _convert_best_sector_times(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа BEST_SECTOR_TIMES."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        if pdf.get_tables_count() == 0:
            return []

        res = []

        # получаем Sector 1
        raw_table = pdf.get_table(table_number=1)
        if raw_table:
            table_wrapper = TableWrapper(title="Sector 1")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.BEST_SECTOR_TIMES_COLUMNS,
                rows=raw_table
            )
            res.append(table_wrapper)

        # получаем Sector 2
        raw_table = pdf.get_table(table_number=2)
        if raw_table:
            table_wrapper = TableWrapper(title="Sector 2")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.BEST_SECTOR_TIMES_COLUMNS,
                rows=raw_table,
                num_first_col=True
            )
            res.append(table_wrapper)

        # получаем Sector 3
        raw_table = pdf.get_table(table_number=3)
        if raw_table:
            table_wrapper = TableWrapper(title="Sector 3")

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.BEST_SECTOR_TIMES_COLUMNS,
                rows=raw_table,
                num_first_col=True
            )
            res.append(table_wrapper)


        return res

    # =========================================================================
    # 3. ВСПОМОГАТЕЛЬНЫЕ ХЕЛПЕРЫ
    # =========================================================================

    def _append_rows(
        self,
        table_wrapper: TableWrapper,
        columns: List[str],
        rows: List[List[Optional[str]]],
        ignore_keywords: Optional[List[str]] = None,
        skip_first_col: bool = False,
        num_first_col: bool = False,
    ) -> None:
        """
        Универсальный метод добавления массива строк в TableWrapper.
        skip_first_col - в исходноке не хватает первой колонки, добавляем
        ignore_keywords - игнорируем строки с указаннім текстом в первой колонке
                         (подзаголовой таблицы)
        num_first_col - добавить в первую колонку последовательность 1,2,3, ...
        """
        if not rows:
            return

        ignore_list = [kw.upper() for kw in (ignore_keywords or [])]

        l_num = 1
        for row in rows:
            # Пропускаем пустые строки
            if not row or not any(row):
                continue

            # Пропускаем строки с ключевыми словами-разделителями
            first_cell = str(row[0]).upper() if row[0] is not None else ""
            if any(kw in first_cell for kw in ignore_list):
                continue

            row_values = row
            if skip_first_col:
                # добавляем пропущенное значение в пропущенную колонка
                row_values = [""] + row_values
            elif num_first_col:
                # добавляем нумерацию в пропущенную колонка
                row_values = [str(l_num)] + row_values
                l_num += 1

            table_wrapper.add_line(columns, row_values)