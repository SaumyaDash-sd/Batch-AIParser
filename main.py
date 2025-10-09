from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates


import login_setup
import test_process
import job_history
import batch_process
import batch_history


app = FastAPI()

# Allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Point Jinja2Templates to your "frontend/templates" folder
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/")
@app.get("/home")
async def serve_home():
    return FileResponse("frontend/templates/index.html")


# Mount login router under /auth
app.include_router(login_setup.login_router, prefix="/auth", tags=["Login setup"])
app.include_router(test_process.test_process_router, prefix="/test-job", tags=["Test job process"])
app.include_router(job_history.job_history_router, prefix="/job", tags=["Test job history"])
app.include_router(batch_process.batch_process_router, prefix="/batch-job", tags=["Batch job process"])
app.include_router(batch_history.batch_job_history_router, prefix="/batch-history", tags=["Batch job history"])
