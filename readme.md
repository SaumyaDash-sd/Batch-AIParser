# DATA PROCESSOR PRO



# 🔐 Login Setup Flow

This document explains the **end-to-end flow** of the Login Setup logic in our project — from user input on the frontend to database validation and final response.  

---



## 📌 Step 1 - Frontend (User Input)

- User enters:
  - **Username**
  - **Password**

- Clicks **Submit** button.  

👉 On submit → values (`username`, `password`) are sent to the **backend Auth API**.

---



## 📌 Step 2 - Backend Entry Point (`main.py`)

- Request first hits **`main.py`** (backend entry).
- **Router check**: identifies which router to call → `login_router`.  
  - Router prefix: **`/auth`**

- The **login logic** is added in the `login_setup` folder which contains:

login_setup/
├── init.py
├── main.py
├── router.py
└── utils.py



👉 Request reaches `login_router` API defined inside **`login_setup/router.py`**.

---




## 📌 Step 3 - Router Layer (`router.py`)

- Main endpoints inside `login_router`:

  ```python 
  @login_router.get("/login/{email}/{password}")
  @login_router.get("/validate-access-token/")
Responsibilities:

Receive username & password from the frontend.

Pass these values for validation.

Decide response:

✅ Authentication successful → return success response.

❌ Authentication failed → return failure response.

👉 Note:
This file only decides the response (success/failure).
The actual validation logic is implemented in login_setup/main.py.



## 📌 Step 4 - Validation Logic (login_setup/main.py)
Core login validation is handled here:
Compare user credentials against database records.
Return necessary values that can later:
Be appended in the database
Or sent to the frontend for display

Returns:
True → Successful login
False → Unsuccessful login




# 📌 Step 5 - Database Interaction (Helper Functions)
Functions that support login flow:

Read Database → Fetch user details for given username.
Update Database → Update:

- last login time

- access token

- unique_id

- description

- job title 
etc.

Utilities → Extra operations when user hits Submit.



## 📌 Step 6 - Response Flow
If validation passes →
Return Success ✅ (with user/session details if required)

If validation fails →
Return Failure ❌ (invalid username/password)

Frontend displays appropriate message to user.




## 🔄 Summary Flow Diagram

Frontend (User Input)
        ↓
Backend Entry (main.py)
        ↓
Login Router (router.py)
        ↓
Validation (login_setup/main.py)
        ↓
Database (Read/Update)
        ↓
Response (Success / Failure)


## ✅ Conclusion
This setup ensures a clean separation of concerns:

Frontend → Collects input

Backend Entry → Routes request

Router → Decides response type

Validation Logic → Handles authentication

Database Layer → Provides user data + updates

Response → Final message shown to user




#########################################################################################################



# ⚙️ Test Process Flow

This document explains the complete **Test Process setup** — starting from when a logged-in user chooses to proceed with **Test Process**, fills in inputs, uploads a file, adds prompts and credentials, and finally triggers backend processing through the API.

---

## 🧭 Step 1 - User Action (Frontend)

Once the **user is authenticated**, they are allowed to proceed to the **Test Process** section.

When the user clicks the **Test Process tab**, the following input boxes appear:

- **Job Title**
- **Excel file** to be used for testing the prompt

### 🔘 On Submit:
Once the **Submit** button is clicked:
- The user is navigated to the **Preview Page**.
- The **top 20 rows** of the uploaded Excel file are displayed.
- The **`generate_summary_function`** is called in the **frontend itself** to show this preview.

---

## 🪄 Step 2 - Prompt Page

When the user clicks **Next**, they are taken to the **Prompt Page**, where they must:

- Add their **Prompt** (which will be used for GPT processing).
- Select **Placeholder Fields** from the uploaded Excel sheet.

After filling these, the user clicks **Next** to proceed.

---

## 🔑 Step 3 - Credentials Page

On the **Credentials Page**, the user must enter all **mandatory fields**, such as:

- **API Key**
- **Endpoint**
- **Temperature**
- **Chunk Size**
- Other necessary credentials

Once filled, clicking **Next** takes the user to the **Overview & Confirmation Page**.

---

## 🚀 Step 4 - Overview & Confirmation Page

This is the final review step where all user inputs are summarized.

The user presses the **“Start Processing”** button.

➡️ This triggers the **backend API**:
/test-job/process/test-prompt/


---

## 🧩 Step 5 - Backend Entry (main.py)

When the **Start Processing** button is clicked:
- The request hits the **`test_process_router`** (prefix: `/test-job`).
- Defined in **`main.py`** as:

  ```python
  app.include_router(test_process_router, prefix="/test-job")
The router uses the test_process folder for further processing.

📁 Folder structure:

css
Copy code
test_process/
├── __init__.py
├── main.py
├── router.py
└── utils.py



## 📡 Step 6 - Router Layer (router.py)
Main endpoint:

@test_process_router.post("/process/test-prompt/")
Responsibilities:
Receive all values entered by the user on the frontend:

Excel file (in bytes)
Job Title
Prompt
Placeholder fields
Credentials (API key, endpoint, temperature, etc.)
Chunk size
Authenticate the user using the provided authentication details.
If the user is authenticated, proceed further.
Convert all received values into required backend formats for processing.



## 🧠 Step 7 - Data Conversion Logic
Before executing the main logic:

The raw data received from frontend must be transformed into usable formats.

🔄 Example Conversions:
Input Type	Received As	Converted To	Used For
Excel File	Bytes	Pandas DataFrame	For prompt testing
Prompt	String	Variable	Passed into GPT processing
Credentials	Key-Value JSON	Multiple Variables	For API authentication
Fields	JSON List	Python List	Placeholder replacements

📘 Once the Excel file is converted:

It is read as a Pandas DataFrame.
The columns of this DataFrame are used across multiple internal processes.



## 🧩 Step 8 - Core Logic (test_process/main.py)
After successful format conversions:

The function test_prompt_process() is triggered.
Inside this, execute_prompt() is called — which runs the main GPT calling logic.

Responsibilities:
Execute the user-provided prompt on the data.
Run GPT API calls using credentials entered by the user.
Process the data row-by-row (or in chunks based on chunk_size).
Store intermediate results or required info in the database.



## 🛠 Step 9 - Utilities (utils.py)
The utility functions in utils.py handle:
GPT API interaction and processing logic.
Formatting and transforming the GPT responses.
Appending important details in the database, such as:
Job details
Processing costUser activity tracking
Any metadata required for audit or usage analytics


## 💾 Step 10 - Final Output Handling
Once the GPT processing is completed:

The output is stored in a new DataFrame.

This DataFrame is converted back into bytes (CSV/Excel format).

Sent to the frontend for:

Preview display

Download option (user can download processed file)

## 🔄 Summary Flow Diagram

User (Frontend)
    ↓
Preview Page (generate_summary_function)
    ↓
Prompt Page (Prompt + Placeholder Fields)
    ↓
Credentials Page (API Key, Endpoint, etc.)
    ↓
Overview & Confirmation
    ↓
Backend main.py (test_process_router)
    ↓
Router (router.py → /process/test-prompt/)
    ↓
Data Conversion (Bytes → DataFrame, JSON → Dict)
    ↓
Logic Layer (test_process/main.py → test_prompt_process → execute_prompt)
    ↓
Utilities (utils.py → GPT API + DB Update)
    ↓
Output DataFrame → Bytes → Frontend (Preview + Download)


## 🧱 Tech Stack Summary
Layer	Technology
Frontend	React / Next.js (with API integration)
Backend	FastAPI
Database	PostgreSQL / MySQL (depending on setup)
Model API	GPT / LLM (via API key + endpoint)
Libraries	Pandas, Pydantic, Uvicorn, Requests

## 🚀 Run Command
To start the backend server:

uvicorn main:app --reload


If your entry file is inside a folder (e.g., backend/main.py), use:

uvicorn backend.main:app --reload


## 🧩 Folder Overview

project/
├── main.py                  # Entry point
├── login_setup/             # Handles user login and authentication
├── test_process/            # Handles test job processing
│   ├── __init__.py
│   ├── main.py              # Core processing logic
│   ├── router.py            # API endpoint definitions
│   └── utils.py             # Helper and GPT-related functions
└── requirements.txt




XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


# 🧾 Job History Feature

This section explains the **Job History functionality** — how the system handles fetching, authenticating, and managing the user’s previously executed test jobs.

---

## 🧭 Step 1 - Frontend (User Interaction)

When the **user clicks the “Job History” tab** on the frontend:

- A request is sent to the **backend router → `job_history_router`**.
- The following APIs are triggered:
  ```python
  @job_history_router.get("/history/test-job/")
  @job_history_router.delete("/history/delete-job/")



## 📡 Step 2 - Backend Router (job_history_router)
When the /history/test-job/ API is hit:

The backend authenticates the user using:

user_id
access_token

If authentication fails:
Response: ❌ "Invalid user credentials"

If authentication is successful:
Fetch all job details for that user_id from the database.



## 🗂 Step 3 - Database Fetching Logic
Once the user is validated:

The backend queries the database for all jobs associated with that user_id.

Each job record may include details like:

- Job Title
- Date of Execution
- Prompt Used
- Model Name / Endpoint
- Output File Name
- Status (Completed / Failed)
- Last Updated Timestamp

Possible Responses:
Scenario	Backend Response
❌ No jobs found	"No job details"
✅ Jobs found	Dictionary of all job-related information

Example Response:
{
  "user_id": "12345",
  "job_history": [
    {
      "job_id": "job_001",
      "job_title": "Product Keyword Mapping",
      "status": "Completed",
      "model_used": "gpt-4",
      "processed_rows": 500,
      "timestamp": "2025-10-04T14:32:00"
    },
    {
      "job_id": "job_002",
      "job_title": "Invoice Summary Generation",
      "status": "Completed",
      "model_used": "gpt-4-mini",
      "processed_rows": 300,
      "timestamp": "2025-10-03T10:22:15"
    }
  ]
}


## 🗑 Step 4 - Delete Job Functionality
When the user clicks “Delete Job” on the frontend:

- The same job_history_router is triggered.

The delete endpoint is hit:
@job_history_router.delete("/history/delete-job/")
Steps:

Authenticate the user again using user_id and access_token.
Check if the specified job_id exists in that user’s history.

If found → remove that record from the database.
Send confirmation message back to frontend.

Response Scenarios:

Scenario	Response
✅ Job found & deleted	"Job deleted successfully"
❌ Invalid user	"User authentication failed"
❌ Job not found	"No such job found in history"

## 🧩 Step 5 - Folder Structure


job_history/
├── __init__.py
├── router.py          # Contains all job history endpoints
├── main.py            # Core logic to fetch, delete, or validate jobs
└── utils.py           # Helper functions for authentication and DB queries


## 🔄 Summary Flow Diagram

Frontend (Job History Tab)
        ↓
Backend main.py
        ↓
job_history_router
        ↓
Authenticate User (user_id + access_token)
        ↓
IF Invalid → Return "Invalid User"
        ↓
ELSE
    ↓
Fetch Job History from DB
    ↓
IF Empty → Return "No Job details"
    ↓
ELSE → Return Job History Dictionary


## 🔁 Delete Flow:
pgsql
Copy code
Frontend (Delete Job Button)
        ↓
job_history_router (DELETE /history/delete-job/)
        ↓
Authenticate User
        ↓
Check Job Existence in DB
        ↓
IF Found → Delete Row → Return "Job deleted successfully"
        ↓
IF Not Found → Return "No such job found"
