import datetime
import logging
from fastapi import APIRouter, Body, HTTPException, Path, Request, Response, status
from pydantic import constr
from sqlalchemy import select
from typing import Annotated
from ..constants import SHORTEN_URL_CODE_REGEX
from ..db import AsyncSession, models as db_models
from ..schemes.api import NewOriginalUrl, NewShortenUrl, ShortenUrl
from ..utils import generate_random_string


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/api/v1',
    tags=['API']
)


@router.post('/shorten',
             operation_id='create-shorten-url',
             response_model=NewShortenUrl,
             response_model_by_alias=False,
             status_code=status.HTTP_201_CREATED,
             summary='Create shorten URL',
             description='Generates new code and returns shorten URL based on that code',
             responses={
                 status.HTTP_201_CREATED: {'description': 'Shorten URL is created'}
             })
async def create_shorten_url(
    url: Annotated[NewOriginalUrl, Body()],
    request: Request,
    response: Response
):
    async with AsyncSession.begin() as session:
        while True:
            # добавить проверку на количество записей в БД, чтоб вернуть ошибку или увелчить длину кодовой строки
            code = generate_random_string(6)
            db_query = select(
                select(db_models.ShortenUrl)
                    .where(db_models.ShortenUrl.code == code)
                    .exists()
            )
            is_code_existing = (await session.execute(db_query)).scalar()
            if not is_code_existing:
                break
        shorten_url = db_models.ShortenUrl(
            code=code,
            original_url=str(url.url),
            creation_timestamp=datetime.datetime.utcnow()
        )
        session.add(shorten_url)
    shorten_url = NewShortenUrl(shorten_url=str(request.url.replace(path=f'/s/{code}', query='', fragment='')))
    logger.info(f'Shorten URL "{shorten_url.shorten_url}" is created')
    return shorten_url


@router.get('/stats/{code}',
            operation_id='get-shorten-url-statistics',
            response_model=ShortenUrl,
            response_model_by_alias=False,
            summary='Get shorten URL statistics by its code',
            description='Retrives main information about shorten URL and its usage statistics',
            responses={
                status.HTTP_200_OK: {
                    'description': 'Shorten URL statistics is retrived'
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'Shorten URL is not found',
                    'content': {'application/json': {'example': {'detail': 'Shorten URL is not found'}}}
                }
            })
async def get_shorten_url_statistics(
    code: Annotated[constr(pattern=SHORTEN_URL_CODE_REGEX),
                    Path(description='Shorten URL code', example='3tQ3Ta')]
):
    db_query = (
        select(db_models.ShortenUrl)
            .where(db_models.ShortenUrl.code == code)
    )
    async with AsyncSession.begin() as session:
        shorten_url = (await session.execute(db_query)).unique().scalars().one_or_none()
    if not shorten_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Shorten URL is not found'
        )
    return ShortenUrl.model_validate(shorten_url, from_attributes=True)