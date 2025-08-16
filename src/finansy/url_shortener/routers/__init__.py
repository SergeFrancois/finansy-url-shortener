from fastapi import APIRouter
from . import api, main


router = APIRouter(prefix='')
router.include_router(main.router)
router.include_router(api.router)