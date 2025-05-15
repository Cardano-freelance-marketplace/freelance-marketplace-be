import uuid
from fastapi import UploadFile


class FileManipulator:

    @staticmethod
    async def create_tmp_file(
            file: UploadFile
    ) -> str:

        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        return temp_path
