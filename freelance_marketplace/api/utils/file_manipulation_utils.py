import subprocess
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile
import uuid


class FileManipulator:

    @classmethod
    async def create_tmp_file(
            cls,
            file: UploadFile
    ) -> str:
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return temp_path

    @staticmethod
    def is_image(file_path: str) -> bool:
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verifies image integrity
            return True
        except (UnidentifiedImageError, OSError):
            return False
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def compress_image(
            cls,
            file_path: str
    ):
        try:
            subprocess.run(
                ["jpegoptim","--max=70" ,"--strip-all", "--quiet", "--all-progressive", file_path],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"jpegoptim failed: {e}")
