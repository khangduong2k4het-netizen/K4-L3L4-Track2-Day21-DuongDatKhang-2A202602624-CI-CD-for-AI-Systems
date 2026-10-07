from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path
import boto3
import math
import pandas as pd
import joblib
import os

MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", "~/models/model.joblib")).expanduser()
FEATURE_NAMES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]


def download_model():
    """
    Tai model tu S3 luc khoi dong, dung AWS credentials hoac IAM role cua EC2.
    """
    bucket = os.getenv("ARTIFACT_BUCKET")
    if not bucket:
        raise RuntimeError("Set ARTIFACT_BUCKET to the S3 bucket containing the model")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = MODEL_PATH.with_suffix(".joblib.download")
    boto3.client("s3").download_file(bucket, MODEL_KEY, str(temporary_path))
    temporary_path.replace(MODEL_PATH)
    print("Model downloaded from S3.", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    download_model()
    app.state.model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(lifespan=lifespan)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    if len(req.features) != len(FEATURE_NAMES):
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")
    if not all(math.isfinite(value) for value in req.features):
        raise HTTPException(status_code=400, detail="Features must contain finite numbers")
    features = pd.DataFrame([req.features], columns=FEATURE_NAMES)
    prediction = int(app.state.model.predict(features)[0])
    return {
        "prediction": prediction,
        "label": "thu_nhap_cao" if prediction == 1 else "thu_nhap_thap",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
