import pytest

from docs_src.testing.tutorial002 import test_app


@pytest.mark.asyncio
async def test_test_app() -> None:
    await test_app()
