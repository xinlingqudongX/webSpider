from fastapi import APIRouter
from .spider_router import router as spider_router
from ws import ws_router

router = APIRouter()

routerPrefix = 'v1'

router.include_router(spider_router)
router.include_router(ws_router.router)