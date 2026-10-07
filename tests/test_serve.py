from unittest.mock import Mock

from fastapi.testclient import TestClient
import joblib
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from src import serve


@pytest.fixture
def s3_model(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACT_BUCKET", "income-test-bucket")
    monkeypatch.setattr(serve, "MODEL_PATH", tmp_path / "models/model.joblib")
    client = Mock()
    monkeypatch.setattr(serve.boto3, "client", lambda service: client)

    def install_model(prediction):
        model = DummyClassifier(strategy="constant", constant=prediction)
        model.fit(pd.DataFrame([[0] * 10, [1] * 10], columns=serve.FEATURE_NAMES), [0, 1])
        client.download_file.side_effect = lambda bucket, key, destination: joblib.dump(model, destination)
        return client

    return install_model


@pytest.mark.parametrize("prediction,label", [(0, "thu_nhap_thap"), (1, "thu_nhap_cao")])
def test_startup_download_health_and_prediction(s3_model, prediction, label):
    storage = s3_model(prediction)
    with TestClient(serve.app) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        response = client.post("/score", json={"features": [60, 2, 5, 2, 4, 0, 1, 0, 0, 45]})
        assert response.status_code == 200
        assert response.json() == {"prediction": prediction, "label": label}
    storage.download_file.assert_called_once_with(
        "income-test-bucket", serve.MODEL_KEY, str(serve.MODEL_PATH.with_suffix(".joblib.download"))
    )


@pytest.mark.parametrize("features", [[], [1] * 9, [1] * 11])
def test_wrong_feature_count_returns_400(s3_model, features):
    s3_model(0)
    with TestClient(serve.app) as client:
        assert client.post("/score", json={"features": features}).status_code == 400


def test_nonfinite_features_return_400(s3_model):
    s3_model(0)
    with TestClient(serve.app) as client:
        response = client.post("/score", content='{"features": [1,1,1,1,1,1,1,1,1,Infinity]}', headers={"Content-Type": "application/json"})
        assert response.status_code == 400


def test_failed_download_stops_startup(s3_model):
    storage = s3_model(0)
    storage.download_file.side_effect = RuntimeError("S3 download failed")
    with pytest.raises(RuntimeError, match="S3 download failed"):
        with TestClient(serve.app):
            pass


def test_missing_bucket_stops_startup(monkeypatch):
    monkeypatch.delenv("ARTIFACT_BUCKET", raising=False)
    with pytest.raises(RuntimeError, match="ARTIFACT_BUCKET"):
        with TestClient(serve.app):
            pass
