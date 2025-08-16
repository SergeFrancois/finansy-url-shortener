from sqlalchemy.dialects.sqlite import DATETIME, INTEGER, TEXT
from sqlalchemy.orm import DeclarativeBase, mapped_column


ISO_DATETIME = DATETIME(
    storage_format='%(year)04d-%(month)02d-%(day)02dT%(hour)02d:%(minute)02d:%(second)02d.%(microsecond)06d',
    regexp=r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)(?:\.(\d+))?',
)


class BaseModel(DeclarativeBase):
    pass


class ShortenUrl(BaseModel):
    
    __tablename__ = 'shorten_url'
    
    code = mapped_column(TEXT, primary_key=True)
    original_url = mapped_column(TEXT, nullable=False)
    request_count = mapped_column(INTEGER, nullable=False, default=0)
    creation_timestamp = mapped_column(ISO_DATETIME, nullable=False)