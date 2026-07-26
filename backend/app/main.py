"""FastAPI application: the AI Electronics Scanner backend.

Endpoints
---------
GET  /                              -> service metadata
GET  /health                       -> liveness probe
POST /api/v1/scan                  -> identify a component from an image (FREE)
GET  /api/v1/components            -> list the knowledge base (FREE)
GET  /api/v1/components/{id}       -> component detail + pinout (FREE)
GET  /api/v1/components/{id}/wiring?board=uno   -> wiring diagram (PREMIUM)
GET  /api/v1/components/{id}/code?board=uno     -> code snippet   (PREMIUM)

Premium endpoints require the `X-Premium-Token` header in this reference
implementation. Swap `_require_premium` for real receipt / Firebase claim
verification before shipping paid features.
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.components import database as db
from app.config import settings
from app.generators import wiring_svg
from app.models import Board, CodeSnippet, Component, ScanResult, WiringDiagram
from app.vision import ocr
from app.vision import pipeline

app = FastAPI(title=settings.app_name, version=settings.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_premium(x_premium_token: Optional[str] = Header(default=None)) -> None:
    """Gate premium features.

    Reference implementation: accept a dev token. In production, verify a
    Play/App Store receipt or a Firebase custom claim here instead.
    """
    if not settings.require_premium:
        return
    if x_premium_token and x_premium_token == settings.premium_dev_token:
        return
    raise HTTPException(
        status_code=402,
        detail="This feature requires a premium subscription. "
        "Provide a valid X-Premium-Token.",
    )


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "components": len(db.all_components()),
        "ocr_available": ocr.is_available(),
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/scan", response_model=ScanResult)
async def scan(image: UploadFile = File(...)) -> ScanResult:
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image upload.")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image too large.")
    return pipeline.analyze(data)


@app.get("/api/v1/components", response_model=list[Component])
def list_components() -> list[Component]:
    return db.all_components()


@app.get("/api/v1/components/{component_id}", response_model=Component)
def get_component(component_id: str) -> Component:
    comp = db.get_component(component_id)
    if comp is None:
        raise HTTPException(status_code=404, detail="Unknown component.")
    return comp


@app.get("/api/v1/components/{component_id}/wiring", response_model=WiringDiagram)
def get_wiring(
    component_id: str,
    board: Board = Query(default=Board.uno),
    _: None = Depends(_require_premium),
) -> WiringDiagram:
    comp = db.get_component(component_id)
    if comp is None:
        raise HTTPException(status_code=404, detail="Unknown component.")
    diagram = db.get_wiring(component_id, board)
    if diagram is None:
        raise HTTPException(
            status_code=404,
            detail=f"No wiring diagram for {component_id} on board '{board.value}'.",
        )
    diagram.svg = wiring_svg.render(diagram, comp.name)
    return diagram


@app.get("/api/v1/components/{component_id}/code", response_model=CodeSnippet)
def get_code(
    component_id: str,
    board: Board = Query(default=Board.uno),
    _: None = Depends(_require_premium),
) -> CodeSnippet:
    comp = db.get_component(component_id)
    if comp is None:
        raise HTTPException(status_code=404, detail="Unknown component.")
    snippet = db.get_code(component_id, board)
    if snippet is None:
        raise HTTPException(
            status_code=404,
            detail=f"No code snippet for {component_id} on board '{board.value}'.",
        )
    return snippet
