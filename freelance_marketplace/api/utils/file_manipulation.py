import json
from io import BytesIO
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import List, Any, Coroutine

import pandas as pd

import openpyxl
from fastapi import UploadFile
from openpyxl.worksheet.worksheet import Worksheet
from starlette.datastructures import Headers

class FileTransformer:

    @classmethod
    async def __read_xlsx(cls, file_path: str) -> UploadFile:
        with open(file_path, "rb") as f:
            temp_file = SpooledTemporaryFile()
            temp_file.write(f.read())
            temp_file.seek(0)

            file = UploadFile(
                filename=Path(file_path).name,
                file=BytesIO(temp_file.read()),
                headers=Headers({"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
            )
        return file

    @classmethod
    async def __get_xlsx_file_stream(cls, file: UploadFile) -> BytesIO:
        file_content = await file.read()
        return BytesIO(file_content)

    @classmethod
    async def __read_xlsx_sheet(cls, file_stream: BytesIO) -> Worksheet | None:
        wb = openpyxl.load_workbook(file_stream, data_only=True)
        sheet = wb.active
        return sheet

    @classmethod
    async def __parse_sheet_data(
            cls,
            sheet: Worksheet,
            columns: List[int]
    ) -> list[str]:
        all_rows = list(sheet.iter_rows(values_only=True))
        df = pd.DataFrame(all_rows)

        result_json = df.to_json(orient='split')
        sheet_dict: dict = json.loads(result_json)
        result_list = []
        data_list = sheet_dict.get('data', [])
        for row in data_list:
            for column in columns:
                result_list.append(row[column])
        result_list.pop(0)
        return list(set(result_list))

    @classmethod
    async def __root_dir(cls) -> str:
        root_dir = Path(__file__).resolve().parent
        while not (root_dir / "pyproject.toml").exists() and root_dir != root_dir.parent:
            root_dir = root_dir.parent
        return root_dir

    @classmethod
    async def get_file_content(
            cls,
            file_path: str,
            columns: List[int],
    ) -> list[str]:
        path = f"{await cls.__root_dir()}/{file_path}"
        file = await cls.__read_xlsx(file_path=path)
        file_stream = await cls.__get_xlsx_file_stream(file=file)
        sheet = await cls.__read_xlsx_sheet(file_stream=file_stream)
        sheet_dict = await cls.__parse_sheet_data(sheet=sheet, columns=columns)
        return sheet_dict

