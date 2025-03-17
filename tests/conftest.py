import pytest
from syrupy.extensions.json import JSONSnapshotExtension


@pytest.fixture
def snapshot_json(snapshot):  # noqa: ANN001, ANN201
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)
