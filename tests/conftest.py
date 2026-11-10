import pytest

from careerpath.service import CareerPathService


@pytest.fixture(scope="session")
def service_app():
    # Reuse one ASGI stack so BentoML does not register Prometheus series twice.
    return CareerPathService.to_asgi()
