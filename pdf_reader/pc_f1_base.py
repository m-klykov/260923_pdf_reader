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
    Q = "q0"   # Qualifying
    SQ = "sq"  # Sprint Shootout / Sprint Qualifying
    S = "s0"   # Sprint Race
    R = "r0"   # Race


class DocType(Enum):
    """Типы официальных отчетов/документов FIA."""
    CLASSIFICATION = "classification"        # P, Q, R
    MAXIMUM_SPEEDS = "maximumspeeds"        # P, Q, R
    BEST_SECTOR_TIMES = "bestsectortimes"    # P, Q, R
    RACE_CONTROL_MESSAGES = "racecontrolmessages"  # P, Q, R
    SECTOR_ANALYSIS = "sectoranalysis" # P, Q, R
    LAP_TIMES = "laptimes" # P, Q
    TRACK_ANALYSIS = "trackanalysis" # P, Q
    LAP_ANALYSIS = "lapanalysis" # R
    FASTEST_LAPS = "fastestlaps" # R
    HISTORY_CHART = "historychart" # R
    PIT_STOP_SUMMARY = "pitstopsummary" # R
    LAP_CHART = "lapchart" # R
    DRIVERS_CHAMPIONSHIP = "driverschampionship" # R
    CONSTRUCTORS_CHAMPIONSHIP = "constructorschampionship" # R


class PdfConvF1Base(PdfConvBase):
    """Базовый парсер документов Формулы-1."""

    # Список колонок для итоговых таблиц сессий практик (P1, P2, P3)
    PRACTICE_CLASSIFICATION_COLUMNS = [
        "pos", "no", "driver", "", "", "", "entrant",
        "time", "laps", "gap", "int", "kmh", "time_of_day"
    ]

    # Список колонок для квалификаций (Q)
    QUALIFYING_CLASSIFICATION_COLUMNS = [
        "pos", "no", "driver", "", "", "entrant",
        "q1_time", "q1_laps", "q1_proc", "q1_dtime",
        "q2_time", "q2_laps", "q2_dtime",
        "q3_time", "q3_laps", "q3_dtime",
    ]

    # Список колонок для гонок (R)
    RACE_CLASSIFICATION_COLUMNS = [
        "pos", "no", "driver", "", "", "entrant",
        "laps", "time", "gap", "int", "kmh",
        "fastest", "on", "pts"
    ]

    # Список колонок для максимальной скорости
    MAXIMUM_SPEEDS_COLUMNS = [
        "pos", "no", "driver", "kmh",
    ]

    # Список колонок для лучших секторов
    BEST_SECTOR_TIMES_COLUMNS = [
        "pos", "no", "driver", "time",
    ]

    # Список колонок для сообщений дирекции гонки
    RACE_CONTROL_MESSAGES_COLUMNS = [
        "time", "message",
    ]

    # Список колонок для SECTOR_ANALYSIS
    SECTOR_ANALYSIS_COLUMNS = [
        "lap",
        "s1_time", "s1_kmh",
        "s2_time", "s2_kmh",
        "s3_time", "s3_kmh",
        "time",
    ]

    # Список колонок для LAP_TIMES
    LAP_TIMES_COLUMNS = [
        "no", "p", "time",
    ]

    # Список колонок для TRACK_ANALYSIS
    TRACK_ANALYSIS_COLUMNS = [
        "transponder", "pit exit",
        "laps", "pit entry",
    ]

    # Список колонок для LAP_ANALYSIS
    LAP_ANALYSIS_COLUMNS = [
        "lap", "p", "time",
    ]

    # Список колонок для FASTEST_LAPS
    FASTEST_LAPS_COLUMNS = [
        "pos", "no", "driver", "", "", "", "entrant",
        "time", "on", "gap", "int", "kmh", "time_of_day"
    ]

    # Список колонок для HISTORY_CHART
    HISTORY_CHART_COLUMNS = [
        "no", "gap", "time",
    ]

    # Список колонок для PIT_STOP_SUMMARY
    PIT_STOP_SUMMARY_COLUMNS = [
        "no", "driver", "entrant",
        "lap", "time_of_day", "stop",
        "duration", "total", "time"
    ]


    def __init__(
            self,
            session_type: SessionType,
            doc_type: DocType,
    ):
        super().__init__()
        self.session_type = session_type
        self.doc_type = doc_type
        self.crop_box = None

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
            case DocType.RACE_CONTROL_MESSAGES:
                return self._convert_race_control_mess(pdf_path)
            case DocType.SECTOR_ANALYSIS:
                return self._convert_sector_analysis(pdf_path)
            case DocType.LAP_TIMES:
                return self._convert_lap_times(pdf_path)
            case DocType.TRACK_ANALYSIS:
                return self._convert_track_analysis(pdf_path)
            case DocType.LAP_ANALYSIS:
                return self._convert_lap_analysis(pdf_path)
            case DocType.FASTEST_LAPS:
                return self._convert_fastest_laps(pdf_path)
            case DocType.HISTORY_CHART:
                return self._convert_history_chart(pdf_path)
            case DocType.PIT_STOP_SUMMARY:
                return self._convert_race_pit_stop_summary(pdf_path)
            case DocType.LAP_CHART:
                return self._convert_lap_chart(pdf_path)
            case DocType.DRIVERS_CHAMPIONSHIP:
                return self._convert_drivers_championship(pdf_path)
            case DocType.CONSTRUCTORS_CHAMPIONSHIP:
                return self._convert_constructors_championship(pdf_path)
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
                raw_table = pdf.get_table(table_number=1) or []
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.PRACTICE_CLASSIFICATION_COLUMNS,
                    rows=raw_table
                )
                return [table_wrapper]

            case SessionType.Q:
                raw_table = pdf.get_table(table_number=1) or []
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.QUALIFYING_CLASSIFICATION_COLUMNS,
                    rows=raw_table
                )
                return [table_wrapper]

            case SessionType.R:
                raw_table = pdf.get_table(table_number=1) or []
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.RACE_CLASSIFICATION_COLUMNS,
                    rows=raw_table
                )

                if pdf.get_tables_count() > 1:
                    raw_table_not_classified = pdf.get_table(table_number=2) or []
                    self._append_rows(
                        table_wrapper=table_wrapper,
                        columns=self.RACE_CLASSIFICATION_COLUMNS,
                        rows=raw_table_not_classified,
                        skip_first_col=True,
                        ignore_keywords=["NOT CLASSIFIED"]
                    )

                return [table_wrapper]

            case _:
                raise NotImplementedError(
                    f"Обработка классификации для сессии '{self.session_type.value}' еще не реализована."
                )

    def _convert_max_speeds(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа MAXIMUM_SPEEDS."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        if pdf.get_tables_count() == 0:
            return []

        res = []
        table_titles = ["Speed Trap", "Finish Line", "Intermediate 1", "Intermediate 2"]

        for idx, title in enumerate(table_titles, start=1):
            raw_table = pdf.get_table(table_number=idx)
            if raw_table:
                table_wrapper = TableWrapper(title=title)
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.MAXIMUM_SPEEDS_COLUMNS,
                    rows=raw_table,
                    num_first_col=(idx > 1)  # Нумерация нужна начиная со 2-й таблицы
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
        table_titles = ["Sector 1", "Sector 2", "Sector 3"]

        for idx, title in enumerate(table_titles, start=1):
            raw_table = pdf.get_table(table_number=idx)
            if raw_table:
                table_wrapper = TableWrapper(title=title)
                self._append_rows(
                    table_wrapper=table_wrapper,
                    columns=self.BEST_SECTOR_TIMES_COLUMNS,
                    rows=raw_table,
                    num_first_col=(idx > 1)  # Нумерация нужна начиная со 2-й таблицы
                )
                res.append(table_wrapper)

        return res

    def _convert_race_control_mess(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа RACE_CONTROL_MESSAGES."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        table_wrapper = TableWrapper(title="Race Control Messages")
        tables_count = pdf.get_tables_count()

        for table_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(table_number=table_idx) or []
            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.RACE_CONTROL_MESSAGES_COLUMNS,
                rows=raw_table
            )

        return [table_wrapper]

    def _convert_sector_analysis(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка отчетов Sector Analysis."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()
        if tables_count == 0:
            return []

        result_tables = []

        table_wrapper = None

        for t_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(t_idx)
            if not raw_table:
                continue

            # 1. Извлекаем текст непосредственно НАД данной таблицей
            title = pdf.get_text_above_table(
                table_number=t_idx, margin_height=15.0, margin_offset=30
            )

            if title:
                table_wrapper = TableWrapper(title=title)
                result_tables.append(table_wrapper)

            if table_wrapper is None:
                table_wrapper = TableWrapper(title="unknown")
                result_tables.append(table_wrapper)


            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.SECTOR_ANALYSIS_COLUMNS,
                rows=raw_table
            )

        return result_tables

    def _convert_lap_times(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка отчетов Laptimes."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()
        if tables_count == 0:
            return []

        result_tables = []

        table_wrapper = None

        for t_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(t_idx)
            if not raw_table:
                continue

            first_table = t_idx % 2 == 1

            if first_table:
                # для нечетной таблицы получаем заголовок
                # и создаем накопитель,
                # Четная просто подклеиватся к нечетной
                title = pdf.get_text_above_table(
                    table_number=t_idx,
                    margin_height=15.0, margin_offset=15.0,
                    ext_width=100.0
                )

                table_wrapper = TableWrapper(title=title)
                result_tables.append(table_wrapper)


            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.LAP_TIMES_COLUMNS,
                rows=raw_table
            )

        return result_tables

    def _convert_track_analysis(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка отчетов On Track Analysis."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()
        if tables_count == 0:
            return []

        result_tables = []

        for t_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(t_idx)
            if not raw_table:
                continue

            title = pdf.get_text_above_table(
                table_number=t_idx,
                margin_height=15.0, margin_offset=15.0,
            )

            table_wrapper = TableWrapper(title=title)

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.TRACK_ANALYSIS_COLUMNS,
                rows=raw_table
            )

            result_tables.append(table_wrapper)

        return result_tables

    def _convert_lap_analysis(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка отчетов Race Lap Analysis."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()
        if tables_count == 0:
            return []

        result_tables = []

        table_wrapper = None

        for t_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(t_idx)
            if not raw_table:
                continue

            first_table = t_idx % 2 == 1

            if first_table:
                # для нечетной таблицы получаем заголовок
                # и создаем накопитель,
                # Четная просто подклеиватся к нечетной
                title = pdf.get_text_above_table(
                    table_number=t_idx,
                    margin_height=15.0, margin_offset=15.0,
                    ext_width=100.0
                )

                table_wrapper = TableWrapper(title=title)
                result_tables.append(table_wrapper)

            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.LAP_ANALYSIS_COLUMNS,
                rows=raw_table
            )

        return result_tables

    def _convert_fastest_laps(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа CLASSIFICATION."""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        if pdf.get_tables_count() == 0:
            return []

        # Создаем главный враппер таблицы
        main_title = "Fastest Laps"
        table_wrapper = TableWrapper(title=main_title)

        raw_table = pdf.get_table(table_number=1) or []
        self._append_rows(
            table_wrapper=table_wrapper,
            columns=self.FASTEST_LAPS_COLUMNS,
            rows=raw_table
        )
        return [table_wrapper]

    def _convert_history_chart(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка отчетов Race History Chart"""
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        tables_count = pdf.get_tables_count()
        if tables_count == 0:
            return []

        result_tables = []

        for t_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(t_idx)
            if not raw_table:
                continue

            title = f"Lap {t_idx}"

            table_wrapper = TableWrapper(title=title)
            result_tables.append(table_wrapper)


            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.HISTORY_CHART_COLUMNS,
                rows=raw_table
            )

        return result_tables

    def _convert_race_pit_stop_summary(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа PIT_STOP_SUMMARY """
        pdf = PDFWrapper(crop_box=self.crop_box)
        pdf.open(pdf_path)

        table_wrapper = TableWrapper(title="Pit Stop Summary")
        tables_count = pdf.get_tables_count()

        for table_idx in range(1, tables_count + 1):
            raw_table = pdf.get_table(table_number=table_idx) or []
            self._append_rows(
                table_wrapper=table_wrapper,
                columns=self.PIT_STOP_SUMMARY_COLUMNS,
                rows=raw_table
            )

        return [table_wrapper]

    def _convert_lap_chart(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа LAP_CHART """
        # обрезаем лишнее, нам нужен только текст
        area = ((0, 100 / 740), (1, 670 / 740))
        pdf = PDFWrapper(area)

        pdf.open(pdf_path)

        table_wrapper = TableWrapper(title="Lap Chart")
        page_count = pdf.get_page_count()

        rows = []
        columns = []

        for page_idx in range(1, page_count + 1):
            lines = pdf.get_lines(page_number=page_idx)

            if len(lines) < 4:
                continue

            if page_idx == 1:
                line = lines[2]
                columns = line.split()

            for ind in range(3, len(lines)):
                line = lines[ind]
                values = line.split()

                if values[0] == "LAP":
                    values[0] = values[0] + " " + values[1]  # -> "LAP 5"
                    del values[1]

                rows.append(values)

        if rows:
            self._append_rows(
                table_wrapper=table_wrapper,
                columns=columns,
                rows=rows
            )

        return [table_wrapper]

    def _convert_drivers_championship(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа DRIVERS_CHAMPIONSHIP """
        # обрезаем лишнее, нам нужен только текст
        area = ((0, 100 / 740), (1, 670 / 740))
        pdf = PDFWrapper(area)

        pdf.open(pdf_path)

        table_wrapper = TableWrapper(title="Drivers Championship")
        page_count = pdf.get_page_count()

        rows = []
        columns = []

        for page_idx in range(1, page_count + 1):
            lines = pdf.get_lines(page_number=page_idx)
            raw_table = pdf.get_table(table_number=page_idx) or []

            if len(lines) < 4:
                continue

            if page_idx == 1:
                line = lines[2] # DRIVER TOTAL AUS CHN JPN ...
                # print(f"line: {line}")

                counts = {}
                columns_sor = []

                # нумеруем дубликаты
                for item in line.split()[2:]: # абревиатуры строн:
                    if item in counts:
                        counts[item] += 1
                        columns_sor.append(f"{item}{counts[item]}")
                    else:
                        counts[item] = 0
                        columns_sor.append(item)

                columns = ["pos", "driver", "total"]
                for v in columns_sor:
                    columns.append(v) # колонка очков
                    columns.append(v+"_place") # позиция

            for row in raw_table:
                values = row[:3] # no, driver, total
                for col in row[3:]:
                    # я ячейrе "очки \n позиция" или "позиция"
                    col_parts = str(col).split()
                    if len(col_parts)<2:
                        values.append("") # очков нету, добавляем пустое значение
                    values += col_parts

                rows.append(values)

        if rows:
            self._append_rows(
                table_wrapper=table_wrapper,
                columns=columns,
                rows=rows
            )

        return [table_wrapper]

    def _convert_constructors_championship(self, pdf_path: str) -> List[TableWrapper]:
        """Обработка документов типа Constructors Championship """
        # обрезаем лишнее, нам нужен только текст
        area = ((0, 100 / 740), (1, 670 / 740))
        pdf = PDFWrapper(area)

        pdf.open(pdf_path)

        table_wrapper = TableWrapper(title="Drivers Championship")
        page_count = pdf.get_page_count()

        rows = []
        columns = []

        for page_idx in range(1, page_count + 1):
            lines = pdf.get_lines(page_number=page_idx)
            raw_table = pdf.get_table(table_number=page_idx) or []

            if len(lines) < 4:
                continue

            if page_idx == 1:
                line = lines[2] # DRIVER TOTAL AUS CHN JPN ...
                # print(f"line: {line}")

                counts = {}
                columns_sor = []

                # нумеруем дубликаты
                for item in line.split()[2:]: # абревиатуры строн:
                    if item in counts:
                        counts[item] += 1
                        columns_sor.append(f"{item}{counts[item]}")
                    else:
                        counts[item] = 0
                        columns_sor.append(item)

                columns = ["pos", "entrant", "total"]
                for v in columns_sor:
                    columns.append(v) # колонка очков
                    columns.append(v+"_pl1") # позиция 1
                    columns.append(v+"_pl2") # позиция 2

            for row in raw_table:
                if row[1] == "NOTES":
                    break

                values = row[:3] # no, entrant, total
                for col in row[3:]:
                    # я ячейrе "очки \n позиция" или "позиция"
                    col_parts = str(col).split()
                    if len(col_parts)<3:
                        values.append("") # очков нету, добавляем пустое значение
                    values += col_parts

                rows.append(values)

        if rows:
            self._append_rows(
                table_wrapper=table_wrapper,
                columns=columns,
                rows=rows
            )

        return [table_wrapper]

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

        :param table_wrapper: Целевой TableWrapper.
        :param columns: Список имен колонок таблицы.
        :param rows: Двумерный массив сырых данных.
        :param ignore_keywords: Игнорировать строки с указанным текстом в первой ячейке (подзаголовки).
        :param skip_first_col: В исходных данных не хватает первой колонки, добавить пустую ячейку "".
        :param num_first_col: Автоматически добавить порядок нумерации (1, 2, 3...) в первую колонку.
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
                # Добавляем пустую ячейку в начало
                row_values = [""] + row_values
            elif num_first_col:
                # Добавляем нумерацию в начало
                row_values = [str(l_num)] + row_values
                l_num += 1

            table_wrapper.add_line(columns, row_values)