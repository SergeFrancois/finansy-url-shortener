import logging
from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from pydantic import constr
from sqlalchemy import select
from typing import Annotated
from ..constants import SHORTEN_URL_CODE_REGEX
from ..db import AsyncSession, models as db_models


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='',
    tags=['Main']
)


@router.get('/s/{code}',
            operation_id='redirect-to-original-url',
            summary='Redirect to original URL by shorten URL code',
            description='Retrives original URL by shorten URL code and redirect to it',
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            responses={
                status.HTTP_307_TEMPORARY_REDIRECT: {
                    'description': 'Redirection to original URL',
                    'content': None
                },
                status.HTTP_404_NOT_FOUND: {
                    'description': 'Shorten URL is not found',
                    'content': {'application/json': {'example': {'detail': 'Shorten URL is not found'}}}
                }
            })
async def redirect_to_original_url(
    code: Annotated[constr(pattern=SHORTEN_URL_CODE_REGEX),
                    Path(description='Shorten URL code', example='3tQ3Ta')]
):
    db_query = (
        select(db_models.ShortenUrl)
            .where(db_models.ShortenUrl.code == code)
    )
    async with AsyncSession.begin() as session:
        shorten_url = (await session.execute(db_query)).unique().scalars().one_or_none()
        if shorten_url:
            shorten_url.request_count += 1
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Shorten URL is not found'
            )
    return RedirectResponse(url=shorten_url.original_url)