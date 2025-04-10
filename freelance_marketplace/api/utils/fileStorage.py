import uuid

import boto3
from typing import List
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.core.config import settings


class FileStorage:
    def __init__(
        self,
        bucket_name: str,
    ):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws.access_key_id,
            aws_secret_access_key=settings.aws.secret_access_key,
            region_name=settings.aws.region_name,
            endpoint_url=settings.aws.endpoint_url,
        )

        self.__ensure_bucket()

    def __ensure_bucket(self):
        existing_buckets = self.s3.list_buckets()
        if self.bucket_name not in [bucket["Name"] for bucket in existing_buckets["Buckets"]]:
            self.s3.create_bucket(Bucket=self.bucket_name)

    def upload_file(self, file_path: str, s3_key: str):
        if self.file_exists_in_s3(s3_key=s3_key):
            raise FileExistsError(f"File {s3_key} already exists")

        self.s3.upload_file(file_path, self.bucket_name, s3_key)

    def download_file(self, s3_key: str, destination_path: str):
        self.s3.download_file(self.bucket_name, s3_key, destination_path)

    def list_files(self, prefix: str = "") -> List[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]

    def delete_file(self, s3_key: str):
        self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expiration,
        )
    @staticmethod
    def generate_file_hash(file_path: str) -> str:
        """Generate a unique hash for the file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def file_exists_in_s3(self, s3_key: str) -> bool:
        """Check if a file already exists in S3 by key"""
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except self.s3.exceptions.ClientError as e:
            return False

if __name__ == "__main__":
    # Define your bucket name
    bucket_name = "my-local-bucket"

    # Initialize the FileStorage instance
    file_storage = FileStorage(bucket_name=bucket_name)

    # Test uploading a file
    file_path = "data_manipulation_utils.py"  # Make sure this file exists in your local directory
    s3_key = f"{file_storage.generate_file_hash(file_path=file_path)}{str(uuid.uuid4())}"
    s3_key_with_prefix = f"documents/{s3_key}"
    print(f"Uploading {file_path} to {s3_key_with_prefix}...")
    file_storage.upload_file(file_path, s3_key_with_prefix)

    # Test listing files in the bucket
    print(f"Listing files in bucket '{bucket_name}' with prefix 'documents/'")
    files = file_storage.list_files("documents/")
    print("Files:", files)

    # Test downloading a file
    destination_path = s3_key
    print(f"Downloading file {s3_key_with_prefix} to {destination_path}...")
    file_storage.download_file(s3_key_with_prefix, destination_path)

    # Test deleting a file
    print(f"Deleting file {s3_key} from the bucket...")
    file_storage.delete_file(s3_key_with_prefix)

    # Test generating a presigned URL
    print(f"Generating presigned URL for {s3_key_with_prefix}...")
    presigned_url = file_storage.generate_presigned_url(s3_key_with_prefix)
    print("Presigned URL:", presigned_url)