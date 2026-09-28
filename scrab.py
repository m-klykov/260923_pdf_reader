from pdf_reader.m_pdf_scraber import PdfScruberModel

if __name__ == "__main__":
    # 1. Инициализируем пайплайн с указанием папок
    pipeline = PdfScruberModel(
        download_dir="scrub/pdf_downloads",
        output_dir="scrub/json_results"
    )

    # 2. Запускаем полный процесс для указанного URL события FIA
    target_page_url = "https://www.fia.com/events/fia-formula-one-world-championship/season-2026/azerbaijan-grand-prix/eventtiming-information"

    processed_jsons = pipeline.run(
        page_url=target_page_url,
        # url_pattern=r"Classification"  # Искать только PDF, у которых в имени есть "Classification"
    )

    print("Созданные файлы:", processed_jsons)