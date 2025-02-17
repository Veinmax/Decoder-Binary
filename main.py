import os
import tempfile
import base64
from fastapi import FastAPI, File, UploadFile, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer, BadSignature
from dotenv import load_dotenv, find_dotenv
from schemas import UpdateData
from crud import decode_binary, encode_binary


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv(find_dotenv())
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
serializer = URLSafeSerializer(SECRET_KEY)


# Middleware to handle sessions
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_data = {}
    session_cookie = request.cookies.get("session")
    if session_cookie:
        try:
            session_data = serializer.loads(session_cookie)
        except BadSignature:
            # Invalid session cookie, ignore it
            pass
    request.state.session = session_data
    response = await call_next(request)

    if request.state.session:
        response.set_cookie(
            key="session",
            value=serializer.dumps(request.state.session),
            httponly=True,
            secure=True,
        )
    else:
        response.delete_cookie("session")
    return response


def get_session(request: Request):
    return request.state.session


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), session: dict = Depends(get_session)
) -> dict:
    content = await file.read()
    # Encode binary data to Base64 for JSON serialization
    session["current_records"] = base64.b64encode(content).decode("utf-8")
    return {"message": "File uploaded successfully"}


@app.get("/data")
async def get_data(session: dict = Depends(get_session)) -> dict:
    current_records_base64 = session.get("current_records")
    if not current_records_base64:
        return {"error": "No data found in session"}

    # Decode Base64 back to binary
    content = base64.b64decode(current_records_base64)
    current_records = decode_binary(content)

    mir = next((record for record in current_records if record["type"] == "MIR"), None)
    if not mir:
        return {"error": "MIR record not found"}
    return {
        "temperature": mir["temperature"],
        "test_results": [
            {
                "test_name": record["test_name"],
                "test_value": record["test_value"],
                "pass_fail": record["pass_fail"],
            }
            for record in current_records
            if record["type"] == "PTR"
        ],
    }


@app.post("/update")
async def update_data(data: UpdateData, session: dict = Depends(get_session)):
    current_records_base64 = session.get("current_records")
    if not current_records_base64:
        return {"error": "No data found in session"}

    content = base64.b64decode(current_records_base64)
    current_records = decode_binary(content)
    mir_index = next(
        (idx for idx, record in enumerate(current_records) if record["type"] == "MIR"),
        None,
    )
    if mir_index is None:
        return {"error": "MIR record not found"}

    current_records[mir_index]["temperature"] = data.temperature
    ptr_indices = [
        i for i, record in enumerate(current_records) if record["type"] == "PTR"
    ]

    for i, ptr_idx in enumerate(ptr_indices):
        current_records[ptr_idx].update(
            {
                "test_value": data.test_results[i].test_value,
                "pass_fail": data.test_results[i].pass_fail,
            }
        )

    updated_content = encode_binary(current_records)
    session["current_records"] = base64.b64encode(updated_content).decode("utf-8")
    return {"message": "Data updated successfully"}


@app.get("/download")
async def download_file(session: dict = Depends(get_session)):
    current_records_base64 = session.get("current_records")
    if not current_records_base64:
        return {"error": "No data found in session"}

    content = base64.b64decode(current_records_base64)
    current_records = decode_binary(content)

    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(encode_binary(current_records))
    temp.close()
    return FileResponse(temp.name, filename="modified.bin")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
