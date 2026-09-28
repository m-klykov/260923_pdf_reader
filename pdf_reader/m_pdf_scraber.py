import json
import os
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from pdf_reader.pc_f1_base import PdfConvF1Base, SessionType, DocType, FileMeta
from pdf_reader.m_table_wrapper import TableWrapper


class PdfScruberModel:
    """
    Класс для автоматического сканирования веб-страниц, загрузки PDF-файлов
    и их конвертации в JSON-структуры.
    """

    def __init__(self, download_dir: str = "downloads", output_dir: str = "output_json"):
        """
        :param download_dir: Папка для сохранения скачанных PDF-файлов.
        :param output_dir: Папка для сохранения итоговых JSON-файлов.
        """
        self.download_dir = download_dir
        self.output_dir = output_dir

        # Создаем целевые директории, если их еще нет
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    # =========================================================================
    # ЭТАП 1: Сканирование страницы и поиск PDF-ссылок
    # =========================================================================

    def fetch_pdf_urls(self, page_url: str, url_pattern: Optional[str] = None) -> List[str]:
        """
        Сканирует HTML-страницу по указанному URL и возвращает список абсолютных ссылок на PDF.

        :param page_url: URL страницы для сканирования.
        :param url_pattern: Опциональная регулярка для фильтрации ссылок (например, r'classification').
        :return: Список абсолютных URL-адресов PDF-файлов.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(page_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        pdf_urls = []

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()

            # Проверяем расширение файла .pdf
            if href.lower().endswith(".pdf"):
                abs_url = urljoin(page_url, href)

                if url_pattern:
                    if re.search(url_pattern, abs_url, re.IGNORECASE):
                        pdf_urls.append(abs_url)
                else:
                    pdf_urls.append(abs_url)

        # Удаляем дубликаты с сохранением порядка
        return list(dict.fromkeys(pdf_urls))

    # =========================================================================
    # ЭТАП 2: Загрузка файлов
    # =========================================================================

    def download_pdf(self, pdf_url: str, subfolder: Optional[str] = None) -> str:
        """
        Скачивает PDF-файл в локальную папку (с поддержкой подпапок).
        """
        target_dir = os.path.join(self.download_dir, subfolder) if subfolder else self.download_dir
        os.makedirs(target_dir, exist_ok=True)

        parsed_url = urlparse(pdf_url)
        filename = os.path.basename(parsed_url.path)

        if not filename or not filename.lower().endswith(".pdf"):
            filename = "document.pdf"

        local_path = os.path.join(target_dir, filename)

        if os.path.exists(local_path):
            print(f"[SKIP DOWNLOAD] Файл уже существует: {local_path}")
            return local_path

        print(f"[DOWNLOAD] {pdf_url} -> {local_path}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        res = requests.get(pdf_url, headers=headers, stream=True)
        res.raise_for_status()

        with open(local_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return local_path

    # =========================================================================
    # ЭТАП 3: Конвертация и сохранение в JSON
    # =========================================================================

    def process_pdf(
            self,
            pdf_path: str,
            session_type: SessionType,
            doc_type: DocType,
            subfolder: Optional[str] = None
    ) -> str:
        """
        Обрабатывает PDF через PdfConvF1Base и сохраняет JSON в указанную подпапку.
        """
        target_dir = os.path.join(self.output_dir, subfolder) if subfolder else self.output_dir
        os.makedirs(target_dir, exist_ok=True)

        converter = PdfConvF1Base(session_type=session_type, doc_type=doc_type)
        tables: List[TableWrapper] = converter.convert(pdf_path)

        result_data: List[Dict[str, Any]] = []
        for table in tables:
            result_data.append({
                "title": table.title,
                "headers": table.get_table()[0] if table.get_table() else [],
                "rows": table.get_rows(),
                "matrix": table.get_table()
            })

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        json_path = os.path.join(target_dir, f"{base_name}.json")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        print(f"[CONVERT] Результат сохранен: {json_path}")
        return json_path

    # =========================================================================
    # ПОЛНЫЙ ЦИКЛ ОБРАБОТКИ (Пайплайн)
    # =========================================================================

    def run(
            self,
            page_url: str,
            url_pattern: Optional[str] = None
    ) -> List[str]:
        """
        Запускает полный цикл: поиск ссылок -> скачивание -> парсинг -> сохранение в JSON.

        :return: Список путей к сформированным JSON-файлам.
        """
        print(f"=== Старт обработки URL: {page_url} ===")

        # 1. Поиск ссылок
        pdf_urls = self.fetch_pdf_urls(page_url, url_pattern=url_pattern)
        print(f"Найдено PDF-ссылок: {len(pdf_urls)}")

        json_outputs = []

        # 2 и 3. Скачивание и конвертация по каждому файлу
        for url in pdf_urls:
            meta = PdfConvF1Base.parse_file_meta(url)

            if not meta:
                print(f"[SKIP] Не удалось распознать структуру FIA: {os.path.basename(url)}")
                continue

            print(
                f"[PROCESS] GP: {meta.grand_prix_id} | "
                f"Session: {meta.session_type.name} | "
                f"Doc: {meta.doc_type.name}"
            )

            try:
                # 2. Скачивание с учетом подпапки grand_prix_id
                local_pdf_path = self.download_pdf(
                    pdf_url=url,
                    subfolder=meta.grand_prix_id
                )

                # 3. Конвертация с сохранением JSON в подпапку grand_prix_id
                json_path = self.process_pdf(
                    pdf_path=local_pdf_path,
                    session_type=meta.session_type,
                    doc_type=meta.doc_type,
                    subfolder=meta.grand_prix_id
                )
                json_outputs.append(json_path)

            except Exception as e:
                print(f"[ERROR] Ошибка при обработке {url}: {e}")

        print("=== Обработка завершена ===")
        return json_outputs