from __future__ import annotations

import os
import io
import logging
from uuid import UUID
from dotenv import load_dotenv
from typing import Optional, BinaryIO, Union

from minio import Minio
from minio.error import S3Error

from summarizer.utils import get_logger
from summarizer.config.config import MinIOConfig
from summarizer.config.default import MINIO_CONFIG_DEFAULT

load_dotenv()


class MinIOStorageService:
    def __init__(self, config: Optional[MinIOConfig] = None, logger: Optional[logging.Logger] = None):
        self.config = config or MINIO_CONFIG_DEFAULT
        self._client: Optional[Minio] = None
        self.logger = logger or get_logger(
            __name__,
            os.getenv("LOG_FORMAT", "text").lower(),
            getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
        )
        self._ensure_bucket_exists()

    @property
    def client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                endpoint=self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=False
            )
        return self._client
    
    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.client.bucket_exists(self.config.bucket_name):
                self.client.make_bucket(self.config.bucket_name)
                self.logger.debug(
                    msg="MinIO",
                    extra={
                        "event": "create_bucket",
                        "bucket_name": self.config.bucket_name
                    }
                )
        except S3Error as e:
            self.logger.error(
                msg="MinIO",
                extra={
                    "event": "create_bucket",
                    "bucket_name": self.config.bucket_name,
                    "detail": "bucket creation failed or already exists",
                    "error": str(e)
                },
            )
            raise

    def _build_object_path(
        self, 
        user_id: Union[str, int], 
        session_uuid: Union[str, UUID], 
        folder_type: str, 
        filename: str
    ) -> str:
        if folder_type not in ["contents"]:
            raise ValueError(f"Invalid folder_type: {folder_type}. Must be: contents")
        
        return f"{user_id}/{session_uuid}/{folder_type}/{filename}"
    
    def upload_file(
        self,
        user_id: Union[str, int],
        session_uuid: Union[str, UUID], 
        folder_type: str, filename: str, file_data: BinaryIO,
        content_type: str = "application/octet-stream"
    ) -> str:
        object_path = self._build_object_path(user_id, session_uuid, folder_type, filename)
        
        try:
            file_data.seek(0, 2)
            file_size = file_data.tell()
            file_data.seek(0)
            
            self.client.put_object(
                bucket_name=self.config.bucket_name,
                object_name=object_path,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            
            self.logger.info(
                msg="MinIO",
                extra={
                    "event": "upload_file",
                    "object_path": object_path,
                    "file_size": file_size,
                    "content_type": content_type
                }
            )
            return object_path
            
        except S3Error as e:
            self.logger.error(
                msg="MinIO",
                extra={
                    "event": "upload_file",
                    "object_path": object_path,
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    def upload_text(
        self,
        user_id: Union[str, int], 
        session_uuid: Union[str, UUID], 
        filename: str, 
        text_content: str, 
        encoding: str = "utf-8"
    ) -> str:
        text_data = text_content.encode(encoding)
        file_stream = io.BytesIO(text_data)
        
        return self.upload_file(
            user_id=user_id,
            session_uuid=session_uuid,
            folder_type="contents",
            filename=filename,
            file_data=file_stream,
            content_type="text/plain"
        )
    
    def download_file(
        self, 
        user_id: Union[str, int], 
        session_uuid: Union[str, UUID], 
        folder_type: str,
        filename: str
    ) -> bytes:
        object_path = self._build_object_path(user_id, session_uuid, folder_type, filename)
        
        try:
            response = self.client.get_object(self.config.bucket_name, object_path)
            data = response.read()
            response.close()
            response.release_conn()
            
            self.logger.info(
                msg="MinIO",
                extra={
                    "event": "file_downloaded",
                    "object_path": object_path,
                    "data_size": len(data)
                }
            )
            return data
            
        except S3Error as e:
            self.logger.error(
                msg="MinIO",
                extra={
                    "event": "download_file",
                    "object_path": object_path,
                    "error": str(e)
                },
                exc_info=True
            )
            raise

_storage_service: Optional[MinIOStorageService] = None


def get_storage_service() -> MinIOStorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = MinIOStorageService()
    return _storage_service


def get_storage_service_dependency():
    return get_storage_service()
