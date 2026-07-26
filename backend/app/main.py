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
POST /api/v1/payments/checkout     -> GCash checkout URL (see app/payments)
POST /api/v1/ai/identify           -> identify ANY component from a photo (PREMIUM)

Premium access is proved either by a Firebase ID token (`Authorization:
Bearer …`, checked against the entitlement a GCash payment wrote) or by the
`X-Premium-Token` development header.
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.components import database as db
from app.config import settings
from app.generators import wiring_svg
from app.models import Board, CodeSnippet, Component, ScanResult, WiringDiagram
from app.ai import identifier as ai_identifier
from app.ai.router import router as ai_router
from app.payments.providers import get_provider
from app.payments.router import router as payments_router
from app.security import require_premium as _require_premium
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


app.include_router(payments_router)
app.include_router(ai_router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "components": len(db.all_components()),
        "ocr_available": ocr.is_available(),
        "payments": get_provider().name,
        "ai_identification": ai_identifier.is_available(),
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
