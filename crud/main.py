from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from models import Prisoner
from database import get_session
from schemas import PrisonerCreate, PrisonerUpdate, PrisonerResponse
from contextlib import asynccontextmanager
import boto3
from fastapi.responses import FileResponse

REPOERT_SERVICE_URL = "http://reportservice:8000"

access_key = "minioadmin"
secret_key = "minioadmin"
endpoint_url = "http://minio:9000"

s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

bucket_name = "main"
try:
    s3_client.create_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' created successfully.")
except Exception:
    print("cant create bucket, already exists")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database on startup
    from models import Prisoner
    from base import engine
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(bind=engine)
    yield
    # Clean up resources on shutdown (if needed)
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.post("/", response_model=PrisonerResponse)
def create_prisoner(prisoner: PrisonerCreate, session: Session = Depends(get_session)):
    db_prisoner = Prisoner(**prisoner.dict())
    session.add(db_prisoner)
    session.commit()
    session.refresh(db_prisoner)
    return db_prisoner

@app.get("/", response_model=list[PrisonerResponse])
def get_prisoners(session: Session = Depends(get_session)):
    prisoners = session.exec(select(Prisoner)).all()
    return prisoners

@app.get("/{uuid}", response_model=PrisonerResponse)
def get_prisoner(uuid: str, session: Session = Depends(get_session)):
    prisoner = session.exec(select(Prisoner).where(Prisoner.id == uuid)).first()
    if not prisoner:
        raise HTTPException(status_code=404, detail="Prisoner not found")
    return prisoner

@app.put("/{uuid}", response_model=PrisonerResponse)
def update_prisoner(uuid: str, prisoner_update: PrisonerUpdate, session: Session = Depends(get_session)):
    prisoner = session.exec(select(Prisoner).where(Prisoner.id == uuid)).first()
    if not prisoner:
        raise HTTPException(status_code=404, detail="Prisoner not found")
    for key, value in prisoner_update.dict(exclude_unset=True).items():
        setattr(prisoner, key, value)
    session.add(prisoner)
    session.commit()
    session.refresh(prisoner)
    return prisoner

@app.delete("/{uuid}")
def delete_prisoner(uuid: str, session: Session = Depends(get_session)):
    prisoner = session.exec(select(Prisoner).where(Prisoner.id == uuid)).first()
    if not prisoner:
        raise HTTPException(status_code=404, detail="Prisoner not found")
    session.delete(prisoner)
    session.commit()
    return {"message": "Prisoner deleted successfully"}

@app.get("/reports/file")
def generate_report(session: Session = Depends(get_session)):
    report = requests.get(REPOERT_SERVICE_URL + "/report/file").json()
    print(report)
    return report

@app.get("/reports/report")
def generate_report(session: Session = Depends(get_session)):
    report = requests.get(REPOERT_SERVICE_URL + "/report/file").json()
    print(report)
    return report

@app.get("/reports/report_file/{report_id}")
def get_report(report_id: str, session: Session = Depends(get_session)):
    s3_client.download_file(bucket_name, f"{report_id}", f"{report_id}")
    return FileResponse(f"{report_id}")

import pydantic
import requests
from fastapi import Request

class PathData(pydantic.BaseModel):
    path: str

@app.post("/reports_by_path/")
def proxy_reports(request: Request, pathData: PathData):
    report_service_endpoint = REPOERT_SERVICE_URL + f"/{pathData.path}"
    response = requests.get(report_service_endpoint)
    return response.json()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
