from fastapi import APIRouter

from app.user.adapter.input.api.v1.user import router as user_router
from core.config import config
from core.fastapi import ExtendedFastAPI


def register_routers(app: ExtendedFastAPI):
    api_router = APIRouter(prefix=config.API_PREFIX)

    @api_router.get("/healthz", tags=["common"])
    async def healthz():
        return {"status": "ok"}

    api_router.include_router(user_router)
    app.include_router(api_router)
