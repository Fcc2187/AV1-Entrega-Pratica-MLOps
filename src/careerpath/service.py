"""BentoML HTTP service for the versioned Adult income pipeline."""

import logging
import os
from pathlib import Path

import bentoml
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from careerpath.model import load_artifact, predict_income
from careerpath.monitoring import InferenceLoggingMiddleware, configure_monitoring
from careerpath.schema import Prediction, Profile

_ROOT = Path(__file__).resolve().parents[2]
_pipeline, _metadata = load_artifact(
    _ROOT / "models" / "adult-income-v1.pkl",
    _ROOT / "models" / "metadata.json",
)


async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "model_version": _metadata["model_version"]})


health_app = Starlette(routes=[Route("/health", health)])


@bentoml.service(name="careerpath", workers=1)
@bentoml.asgi_app(health_app)
class CareerPathService:
    """Serve one validated profile per request."""

    @bentoml.on_startup
    def start_monitoring(self) -> None:
        self._inference_logger = configure_monitoring(
            Path(os.environ.get("CAREERPATH_LOG_PATH", "logs/inference.jsonl"))
        )

    @bentoml.on_shutdown
    def stop_monitoring(self) -> None:
        for handler in self._inference_logger.handlers[:]:
            handler.close()
            self._inference_logger.removeHandler(handler)

    @bentoml.api(route="/predict", input_spec=Profile)
    def predict(self, **profile: object) -> Prediction:
        return Prediction(**predict_income(_pipeline, _metadata, profile))


CareerPathService.add_asgi_middleware(
    InferenceLoggingMiddleware,
    logger=logging.getLogger("careerpath.monitoring"),
    model_version=_metadata["model_version"],
)
