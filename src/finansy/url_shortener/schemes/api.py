import datetime
from pydantic import AnyHttpUrl, BaseModel, Field, NonNegativeInt
from ..constants import SHORTEN_URL_CODE_REGEX


class NewOriginalUrl(BaseModel):    
    url: AnyHttpUrl = Field(description='Original URL', example='https://www.json.org')


class NewShortenUrl(BaseModel):    
    shorten_url: AnyHttpUrl = Field(description='Shorten URL', example='http://localhost:5001/s/3tQ3Ta')


class ShortenUrl(BaseModel):    
    code: str = Field(pattern=SHORTEN_URL_CODE_REGEX, description='Shorten URL code', example='3tQ3Ta')
    original_url: AnyHttpUrl = Field(description='Original URL', example='https://www.json.org')
    request_count: NonNegativeInt = Field(description='Number of requests (usage count)', example='10')
    creation_timestamp: datetime.datetime = Field(description='Creation timestamp', example='2025-08-16T14:03:49.425298')
