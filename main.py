from fastapi import FastAPI
# from login_setup.router import login_router

import login_setup
import test_process


app = FastAPI()

# Mount login router under /auth
app.include_router(login_setup.login_router, prefix="/auth")
app.include_router(test_process.test_process_router, prefix="/test-job")

