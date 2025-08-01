from dataclasses import dataclass


@dataclass
class MinIOConfig:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str

    def __post_init__(self):
        if not self.endpoint or not self.access_key or not self.secret_key or not self.bucket_name:
            raise ValueError("All MinIO configuration fields must be provided.")
