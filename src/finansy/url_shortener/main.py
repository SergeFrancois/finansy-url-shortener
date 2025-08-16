import importlib.metadata
import logging
import yaml
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from . import constants
from .config import config
from .db import create_db, ensure_session_factory_initialized
from .logging import make_log_record
from .routers import router as api_router


logger = logging.getLogger(__name__)

app = FastAPI(
    title='URL shortener service',
    description='A simple web service for creating shortened links similar to [Bitly](https://bitly.com/).',
    version=importlib.metadata.version('finansy-url-shortener'),
    generate_unique_id_function=lambda route: f'{route.tags[0]}.{route.name}',
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': 'Internal error',
            'content': {'application/json': {'example': {'detail': 'Unknown error'}}}
        }
    },
    openapi_tags=[
        {
            'name': 'Main',
            'description': 'Main service operations'
        },
        {
            'name': 'API',
            'description': 'Operations related to service API'
        }
    ]
)
app.include_router(api_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        description=app.description,
        version=app.version,
        routes=app.routes
    )
    openapi_schema['tags'] = app.openapi_tags
    for path in openapi_schema['paths']:
        for method in openapi_schema['paths'][path]:
            if openapi_schema['paths'][path][method]['responses'].get('422'):
                openapi_schema['paths'][path][method]['responses']['400'] = (
                    openapi_schema['paths'][path][method]['responses']['422']
                )
                openapi_schema['paths'][path][method]['responses'].pop('422')
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    errors = jsonable_encoder(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': errors}
    )


@app.middleware('http')
async def handle_unhandled_exception(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception('Unhandled exception')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({'detail': 'Unknown error'})
        )


@app.on_event('startup')
async def handle_startup_event():
    try:
        try:
            with open(constants.LOGGING_CONFIG_PATH, 'r') as file:
                logging_config = yaml.safe_load(file.read())
        except Exception as ex:
            raise Exception('Logging configuration loading failed') from ex
        logging.config.dictConfig(logging_config)
        logging.setLogRecordFactory(make_log_record)
        logger.info('URL shortener service is starting...')
        try:
            config.load()
        except Exception as ex:
            raise Exception('URL shortener service configuration loading failed') from ex
        await create_db()
        ensure_session_factory_initialized()
        logger.info('URL shortener service is started')
    except Exception as ex:
        logger.exception('URL shortener service starting failed')
        raise Exception('URL shortener service starting failed') from ex


@app.on_event('shutdown')
async def handle_shutdown_event():
    try:
        logger.info('URL shortener service is stopping...')
        logger.info('URL shortener service is stopped')
    except Exception as ex:
        logger.exception('URL shortener service stopping failed')
        raise Exception('URL shortener service stopping failed') from ex
