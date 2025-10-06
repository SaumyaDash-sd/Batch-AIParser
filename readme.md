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



📌 Step 4 - Validation Logic (login_setup/main.py)
Core login validation is handled here:

Compare user credentials against database records.

Return necessary values that can later:

Be appended in the database

Or sent to the frontend for display

Returns:

True → Successful login

False → Unsuccessful login




📌 Step 5 - Database Interaction (Helper Functions)
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



📌 Step 6 - Response Flow
If validation passes →
Return Success ✅ (with user/session details if required)

If validation fails →
Return Failure ❌ (invalid username/password)

Frontend displays appropriate message to user.




🔄 Summary Flow Diagram

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
✅ Conclusion
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

yaml
Copy code

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
📡 Step 6 - Router Layer (router.py)
Main endpoint:

python
Copy code
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

🧠 Step 7 - Data Conversion Logic
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

🧩 Step 8 - Core Logic (test_process/main.py)
After successful format conversions:

The function test_prompt_process() is triggered.

Inside this, execute_prompt() is called — which runs the main GPT calling logic.

Responsibilities:
Execute the user-provided prompt on the data.

Run GPT API calls using credentials entered by the user.

Process the data row-by-row (or in chunks based on chunk_size).

Store intermediate results or required info in the database.

🛠 Step 9 - Utilities (utils.py)
The utility functions in utils.py handle:

GPT API interaction and processing logic.

Formatting and transforming the GPT responses.

Appending important details in the database, such as:

Job details

Processing cost

User activity tracking

Any metadata required for audit or usage analytics

💾 Step 10 - Final Output Handling
Once the GPT processing is completed:

The output is stored in a new DataFrame.

This DataFrame is converted back into bytes (CSV/Excel format).

Sent to the frontend for:

Preview display

Download option (user can download processed file)

🔄 Summary Flow Diagram
pgsql
Copy code
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
✅ Key Highlights
Modular design: Router → Logic → Utils → DB

Supports dynamic prompt testing and GPT processing

Secure credential handling (API key, endpoint, etc.)

Real-time preview and downloadable output

Seamless frontend–backend integration

🧱 Tech Stack Summary
Layer	Technology
Frontend	React / Next.js (with API integration)
Backend	FastAPI
Database	PostgreSQL / MySQL (depending on setup)
Model API	GPT / LLM (via API key + endpoint)
Libraries	Pandas, Pydantic, Uvicorn, Requests

🚀 Run Command
To start the backend server:

bash
Copy code
uvicorn main:app --reload
If your entry file is inside a folder (e.g., backend/main.py), use:

bash
Copy code
uvicorn backend.main:app --reload
🧩 Folder Overview
bash
Copy code
project/
├── main.py                  # Entry point
├── login_setup/             # Handles user login and authentication
├── test_process/            # Handles test job processing
│   ├── __init__.py
│   ├── main.py              # Core processing logic
│   ├── router.py            # API endpoint definitions
│   └── utils.py             # Helper and GPT-related functions
└── requirements.txt

