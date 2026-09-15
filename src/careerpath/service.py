"""BentoML HTTP service for the versioned Adult income pipeline."""

from pathlib import Path

import bentoml
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from careerpath.model import load_artifact, predict_income
from careerpath.schema import Prediction, Profile

_ROOT = Path(__file__).resolve().parents[2]
_pipeline, _metadata = load_artifact(
    _ROOT / "models" / "adult-income-v1.pkl",
    _ROOT / "models" / "metadata.json",
)


async def health(_request: Request) -> JSONResponse:
    return JSONResponse(
        {"status": "ok", "model_version": _metadata["model_version"]}
    )


health_app = Starlette(routes=[Route("/health", health)])


@bentoml.service(name="careerpath")
@bentoml.asgi_app(health_app)
class CareerPathService:
    """Serve one validated profile per request."""

    @bentoml.api(route="/predict", input_spec=Profile)
    def predict(self, **profile: object) -> Prediction:
        return Prediction(**predict_income(_pipeline, _metadata, profile))
