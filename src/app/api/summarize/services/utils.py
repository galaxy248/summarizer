from typing import Union
from pathlib import Path


class FileUtils:
    @staticmethod
    def is_text_file(file_path: Union[str, Path]):
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        try:
            if file_path.suffix in [".txt", ".md"]:
                return True
        except Exception as e:
            return False

    @staticmethod
    def is_pdf_file(file_path: Union[str, Path]):
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        try:
            if file_path.suffix == ".pdf":
                return True
        except Exception as e:
            return False
