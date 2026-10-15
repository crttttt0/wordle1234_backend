from fastapi import APIRouter

from app.api.endpoints import games, players

api_router = APIRouter(prefix="/api")
api_router.include_router(players.router)
api_router.include_router(games.router)
