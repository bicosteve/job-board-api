import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

from ..utils.logger import Logger

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}


class FileService:
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        if not filename:
            return False
        return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def save_uploaded_file(file, upload_folder: str) -> str:
        filename = secure_filename(file.filename)
        if not filename:
            Logger.warn("Invalid upload filename")
            raise ValueError("Invalid file name")

        if not FileService.is_allowed_file(filename):
            Logger.warn(f"Unsupported file type for upload: {filename}")
            raise ValueError("Unsupported file type. Allowed: pdf, doc, docx, txt")

        upload_path = Path(upload_folder)
        upload_path.mkdir(parents=True, exist_ok=True)

        new_name = f"{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
        destination = upload_path / new_name
        file.save(str(destination))
        Logger.info(f"File uploaded to {destination}")

        return new_name
