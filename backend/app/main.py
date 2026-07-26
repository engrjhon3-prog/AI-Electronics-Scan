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
from app.payments import entitlements
from app.payments.providers import get_provider
from app.payments.router import router as payments_router
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


def _require_premium(
    x_premium_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> None:
    """Gate premium features.

    Accepts, in order:
      1. A Firebase ID token (`Authorization: Bearer …`) whose account holds a
         live entitlement — which is exactly what a paid GCash checkout writes.
      2. The development token in `X-Premium-Token`.
    """
    if not settings.require_premium:
        return
    if x_premium_token and x_premium_token == settings.premium_dev_token:
        return
    if authorization and authorization.lower().startswith("bearer "):
        claims = entitlements.verify_id_token(authorization.split(" ", 1)[1].strip())
        if claims:
            if claims.get("premium") is True or claims.get("admin") is True:
                return
            email = (claims.get("email") or "").lower()
            record = entitlements.get_store().get_entitlement(email) if email else None
            if record and record.get("premium"):
                expires = entitlements._parse_dt(record.get("expiresAt"))
                if expires is None or expires > entitlements._now():
                    return
    raise HTTPException(
        status_code=402,
        detail="This feature requires a Pro subscription. Subscribe with GCash "
        "in the app, then retry with your account token.",
    )


app.include_router(payments_router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "components": len(db.all_components()),
        "ocr_available": ocr.is_available(),
        "payments": get_provider().name,
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
