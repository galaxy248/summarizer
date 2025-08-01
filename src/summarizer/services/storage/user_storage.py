from __future__ import annotations

from typing import Optional, Union
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.api.auth.token import TokenData
from summarizer.services.storage.minio_service import MinIOStorageService, get_storage_service


class UserStorageManager:
    def __init__(self, storage_service: Optional[MinIOStorageService] = None):
        self.storage = storage_service or get_storage_service()
        self._current_user_id: Optional[Union[str, int]] = None
        self._current_session_uuid: Optional[UUID] = None

    def set_user_context(
        self,
        user_id: Union[str, int],
        session_uuid: Optional[UUID] = None
    ) -> UUID:
        self._current_user_id = user_id
        self._current_session_uuid = session_uuid or uuid4()
        return self._current_session_uuid

    def _ensure_context(self):
        if self._current_user_id is None or self._current_session_uuid is None:
            raise ValueError("User context not set. Call set_user_context() first.")

    def save_uploaded_file(
        self,
        file: UploadFile,
        folder_type: str, 
        custom_filename: Optional[str] = None
    ) -> tuple[str, str]:
        self._ensure_context()

        filename = custom_filename or file.filename
        if not filename:
            raise ValueError("Filename must be provided")

        file.file.seek(0)

        object_path = self.storage.upload_file(
            user_id=self._current_user_id,
            session_uuid=self._current_session_uuid,
            folder_type=folder_type,
            filename=filename,
            file_data=file.file,
            content_type=file.content_type or "application/octet-stream"
        )

        return object_path, filename

    def save_text_content(self, text: str, filename: str) -> str:
        self._ensure_context()
        
        return self.storage.upload_text(
            user_id=self._current_user_id,
            session_uuid=self._current_session_uuid,
            filename=filename,
            text_content=text
        )

    def read_file(self, folder_type: str, filename: str) -> bytes:
        self._ensure_context()
        
        return self.storage.download_file(
            user_id=self._current_user_id,
            session_uuid=self._current_session_uuid,
            folder_type=folder_type,
            filename=filename
        )

    @property
    def current_user_id(self) -> Optional[Union[str, int]]:
        return self._current_user_id
    
    @property
    def current_session_uuid(self) -> Optional[UUID]:
        return self._current_session_uuid


def create_user_storage_manager(
    token_data: TokenData,
    session_uuid: Optional[UUID] = None
) -> UserStorageManager:
    manager = UserStorageManager()
    manager.set_user_context(token_data.user_id, session_uuid)
    return manager


def get_user_storage_manager_dependency(token_data: TokenData) -> UserStorageManager:
    return create_user_storage_manager(token_data)
