# BioTrackr - A simple health App.

**Project Name:** BioTrackr

---

# BioTrackr

**BioTrackr** is a scalable, white-label-ready web platform built with Streamlit and Supabase for tracking blood biomarker data (e.g., glucose, WBC count, hemoglobin). Users can manually enter values, upload PDF lab reports (with optional OCR extraction), visualize trends against clinical reference ranges, and maintain role-based access (full vs. read-only). Labs can onboard, apply custom branding, and manage their patients’ data, all under one unified interface.

---

## 🚀 Features

* **User Authentication**

  * Email/password login (via Supabase Auth)
  * Role assignment: *full* (data entry + dashboard) vs. *readonly* (dashboard only)
  * (Future) Phone-number login support

* **Data Entry & Management**

  * Manual biomarker entry (Glucose, WBC count, Hemoglobin) with date, value, unit
  * PDF upload for lab reports:

    * Stores PDF in Supabase Storage (`reports` bucket)
    * Extracts raw text (using pdfminer or Tesseract OCR)
    * Parses biomarker values via regex, displays extracted data, and saves to database

* **Dashboards & Visualizations**

  * Time-series line charts (Altair) for each biomarker
  * Abnormal-value flagging based on clinical reference ranges (highlighted in red)
  * Detailed data tables with ✅/❌ flags for normal vs. abnormal entries

* **Lab Onboarding & White-Label Infrastructure**

  * Labs can be created with name, logo URL, brand color, and optional custom domain
  * Each lab can assign patients (by phone number) and manage assigned users
  * Future ability to license platform to labs, provide isolated dashboards per lab

* **Admin Tools**

  * “Admin Panel” for managing users and roles
  * System summary: total labs, registered users, uploaded PDFs, biomarker entries
  * View and update user roles (full ↔ readonly) and lab assignments

* **AI-Powered Doctor Chatbot**

  * Built on a free GPT endpoint (`free.yunwu.ai`) for basic medical Q\&A
  * Streamlit chat interface with streaming responses

---

## 📂 Repository Structure

```
bio-trackr/
├── .streamlit/
│   └── secrets.toml
├── pages/
│   ├── admin.py
│   ├── admin_data_enrty.py
│   ├── admin_panel.py
│   ├── data_entry.py
│   ├── dashboard.py
│   ├── doctor_chatbot.py
│   ├── lab_onboarding.py
│   ├── login.py
│   ├── pdf_upload.py
├── utils/
│   ├── auth.py
│   └── pdf_parser.py
├── app.py
├── requirements.txt
└── README.md
```

* **`.streamlit/secrets.toml`**
  Stores Supabase URL, Supabase service role key, Hugging Face token, OpenAI/free-API key, and any other secrets.

* **`pages/`**
  Streamlit multipage scripts:

  * **`login.py`** – User login & signup
  * **`lab_onboarding.py`** – Create new lab with branding
  * **`data_entry.py`** – Manual biomarker entry form
  * **`pdf_upload.py`** – PDF upload, OCR/text extraction, biomarker parsing
  * **`dashboard.py`** – Interactive biomarker charts & tables
  * **`admin.py`** – Admin dashboard summary (system metrics, lab list)
  * **`admin_panel.py`** – Manage user roles and lab assignments
  * **`admin_data_enrty.py`** – Admin can upload biomarker data for any patient
  * **`doctor_chatbot.py`** – AI “Doctor” chatbot powered by GPT-free endpoint

* **`utils/`**

  * **`auth.py`** – Supabase client initialization, login/signup, user role lookup, logout
  * **`pdf_parser.py`** – PDF → text extraction (pdfminer → Tesseract OCR fallback) and biomarker regex parsing

* **`app.py`**
  Primary entrypoint. Sets up the sidebar menu, displays current user, role, and links to each page. Renders the landing page when not logged in.

* **`requirements.txt`**
  Lists all Python dependencies.

---

## ⚙️ Tech Stack

* **Frontend/Web UI:** Streamlit (v1.##+)
* **Authentication, Database & Storage:** Supabase (Postgres + Storage buckets)
* **PDF Parsing & OCR:**

  * [`pdfminer.six`](https://github.com/pdfminer/pdfminer.six) for native text extraction
  * `pdf2image` + [`pytesseract`](https://github.com/madmaze/pytesseract) as OCR fallback
* **Charts & Tables:** Altair (v★) + Pandas (v★)
* **AI Chatbot:** Free GPT endpoint (via `free.yunwu.ai`)
* **Language:** Python 3.9+

---

## 🛠 Prerequisites

1. **Python 3.9 or newer**

2. **Supabase account & project**

   * Create a new Supabase project
   * In “API” settings, copy `API URL` (SUPABASE\_URL) and `anon` key or service\_role key (SUPABASE\_KEY)
   * Configure the following tables (see “Database Schema” below)
   * Create a Storage bucket called `reports` with public disabled

3. **Tesseract OCR** (for PDF OCR fallback)

   * **macOS (Homebrew):**

     ```bash
     brew install tesseract
     ```
   * **Ubuntu (apt):**

     ```bash
     sudo apt update
     sudo apt install tesseract-ocr libtesseract-dev
     ```

4. **System libraries for `pdf2image`**

   * **macOS:** Ghostscript is typically preinstalled. If not:

     ```bash
     brew install ghostscript
     ```
   * **Ubuntu:**

     ```bash
     sudo apt update
     sudo apt install poppler-utils
     ```

---

## 🗄 Database Schema

Below is a minimal set of tables you need to create in your Supabase project. You can use the SQL Editor in Supabase to run these `CREATE TABLE` statements.

```sql
-- -- 1. Create tables

-- -- Tenants (labs)
-- CREATE TABLE IF NOT EXISTS labs (
--   id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
--   name        text NOT NULL,
--   domain      text UNIQUE NOT NULL,
--   branding    jsonb,
--   created_at  timestamptz DEFAULT now()
-- );

-- -- Users
-- CREATE TABLE IF NOT EXISTS users (
--   id          uuid PRIMARY KEY,
--   email       text UNIQUE,
--   phone       text UNIQUE,
--   role        text CHECK (role IN ('lab_admin','full_access','view_only')),
--   lab_id      uuid REFERENCES labs(id),
--   created_at  timestamptz DEFAULT now()
-- );

-- -- Biomarker types & reference ranges
-- CREATE TABLE IF NOT EXISTS biomarker_types (
--   id          serial PRIMARY KEY,
--   name        text UNIQUE NOT NULL,
--   unit        text NOT NULL,
--   normal_low  numeric NOT NULL,
--   normal_high numeric NOT NULL
-- );

-- create table if not exists pdf_files (
--   id uuid default uuid_generate_v4() primary key,
--   user_id uuid references auth.users(id),
--   file_path text not null,
--   file_name text not null,
--   uploaded_at timestamp with time zone default now()
-- );




-- Measured values (with trigger-computed flag)
-- create table if not exists biomarkers (
--   id uuid default uuid_generate_v4() primary key,
--   user_id uuid references auth.users(id),
--   type_id int references biomarker_types(id),
--   biomarker text not null,
--   value numeric not null,
--   unit text,
--   date date not null
-- );
-- drop table if exists biomarkers;

-- insert into biomarkers (user_id, type_id, biomarker, value, unit, date) values
-- ('522a6ccf-5c85-4d5d-9a15-55cede53054b', 1, 'Glucose', 92, 'mg/dL', '2025/05/01'),
-- ('522a6ccf-5c85-4d5d-9a15-55cede53054b', 1, 'Glucose', 108, 'mg/dL', '2025/05/04'),
-- ('522a6ccf-5c85-4d5d-9a15-55cede53054b', 2, 'WBC count', 7500, 'cells/µL', '2025/05/02'),
-- ('522a6ccf-5c85-4d5d-9a15-55cede53054b', 2, 'WBC count', 9000, 'cells/µL', '2025/05/05'),
-- ('522a6ccf-5c85-4d5d-9a15-55cede53054b', 3, 'Hemoglobin', 13.2, 'g/dL', '2025/05/03'),
-- ('522a6ccf-5c85-4d5d-9a15-55cede53054b', 3, 'Hemoglobin', 12.8, 'g/dL', '2025/05/06');


-- select * from biomarkers;


-- -- Uploaded PDF reports
-- CREATE TABLE IF NOT EXISTS pdf_reports (
--   id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
--   user_id       uuid REFERENCES users(id),
--   lab_id        uuid REFERENCES labs(id),
--   file_key      text NOT NULL,
--   status        text CHECK (status IN ('pending','processed','error')) NOT NULL DEFAULT 'pending',
--   parsed_data   jsonb,
--   uploaded_at   timestamptz DEFAULT now()
-- );

-- -- 2. Trigger to populate is_abnormal

-- CREATE OR REPLACE FUNCTION set_biomarker_abnormal()
-- RETURNS trigger
-- LANGUAGE plpgsql AS $$
-- BEGIN
--   NEW.is_abnormal :=
--     ( NEW.value <  (SELECT normal_low  FROM biomarker_types WHERE id = NEW.type_id) )
--  OR ( NEW.value >  (SELECT normal_high FROM biomarker_types WHERE id = NEW.type_id) );
--   RETURN NEW;
-- END;
-- $$;

-- DROP TRIGGER IF EXISTS biomarker_abnormal_trigger ON biomarkers;
-- CREATE TRIGGER biomarker_abnormal_trigger
--   BEFORE INSERT OR UPDATE ON biomarkers
--   FOR EACH ROW
--   EXECUTE FUNCTION set_biomarker_abnormal();

-- -- 3. Enable RLS and create policies (with UUID casts)

-- -- Biomarkers RLS
-- ALTER TABLE biomarkers ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY select_biomarkers ON biomarkers
--   FOR SELECT USING (lab_id = (auth.jwt() ->> 'lab_id')::uuid);
-- CREATE POLICY insert_biomarkers ON biomarkers
--   FOR INSERT WITH CHECK (lab_id = (auth.jwt() ->> 'lab_id')::uuid);
-- CREATE POLICY update_biomarkers ON biomarkers
--   FOR UPDATE USING (lab_id = (auth.jwt() ->> 'lab_id')::uuid);

-- -- PDF Reports RLS
-- ALTER TABLE pdf_reports ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY select_reports ON pdf_reports
--   FOR SELECT USING (lab_id = (auth.jwt() ->> 'lab_id')::uuid);
-- CREATE POLICY insert_reports ON pdf_reports
--   FOR INSERT WITH CHECK (lab_id = (auth.jwt() ->> 'lab_id')::uuid);
-- CREATE POLICY update_reports ON pdf_reports
--   FOR UPDATE USING (lab_id = (auth.jwt() ->> 'lab_id')::uuid);

-- -- Users RLS (so each lab sees only its own users)
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY select_users ON users
--   FOR SELECT USING (lab_id = (auth.jwt() ->> 'lab_id')::uuid);
-- CREATE POLICY insert_users ON users
--   FOR INSERT WITH CHECK (lab_id = (auth.jwt() ->> 'lab_id')::uuid);
-- CREATE POLICY update_users ON users
--   FOR UPDATE USING (lab_id = (auth.jwt() ->> 'lab_id')::uuid);

-- -- 4. Seed biomarker_types
-- INSERT INTO biomarker_types (name, unit, normal_low, normal_high)
-- VALUES
--   ('Glucose',    'mg/dL',  70,    120),
--   ('WBC count',  '/mm³',  4000,  12000),
--   ('Hemoglobin', 'g/dL',   12,    18)
-- ON CONFLICT (name) DO NOTHING;












-- Enable RLS (idempotent)
-- ALTER TABLE biomarkers     ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE pdf_reports   ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE users         ENABLE ROW LEVEL SECURITY;

-- -- Biomarkers policies
-- DROP POLICY IF EXISTS select_biomarkers ON biomarkers;
-- DROP POLICY IF EXISTS insert_biomarkers ON biomarkers;
-- DROP POLICY IF EXISTS update_biomarkers ON biomarkers;

-- CREATE POLICY select_biomarkers ON biomarkers
--   FOR SELECT
--   USING ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- CREATE POLICY insert_biomarkers ON biomarkers
--   FOR INSERT
--   WITH CHECK ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- CREATE POLICY update_biomarkers ON biomarkers
--   FOR UPDATE
--   USING ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- -- PDF Reports policies
-- DROP POLICY IF EXISTS select_reports ON pdf_reports;
-- DROP POLICY IF EXISTS insert_reports ON pdf_reports;
-- DROP POLICY IF EXISTS update_reports ON pdf_reports;

-- CREATE POLICY select_reports ON pdf_reports
--   FOR SELECT
--   USING ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- CREATE POLICY insert_reports ON pdf_reports
--   FOR INSERT
--   WITH CHECK ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- CREATE POLICY update_reports ON pdf_reports
--   FOR UPDATE
--   USING ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- -- Users policies
-- DROP POLICY IF EXISTS select_users ON users;
-- DROP POLICY IF EXISTS insert_users ON users;
-- DROP POLICY IF EXISTS update_users ON users;

-- CREATE POLICY select_users ON users
--   FOR SELECT
--   USING ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- CREATE POLICY insert_users ON users
--   FOR INSERT
--   WITH CHECK ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );

-- CREATE POLICY update_users ON users
--   FOR UPDATE
--   USING ( lab_id = (SELECT lab_id FROM public.users WHERE id = auth.uid()) );





-- If you haven’t already made domain unique, add the constraint:
-- ALTER TABLE labs
-- ADD CONSTRAINT labs_domain_unique UNIQUE(domain);
-- INSERT INTO labs (name, domain)
-- VALUES
--   ('Demo Lab', 'demo.myhealthapp.com')
-- ON CONFLICT (domain) DO NOTHING;
-- SELECT id, name, domain
-- FROM labs;

-- 75efd085-f7b8-4d18-a540-fadaead3637d
-- UPDATE users
-- SET role  = 'lab_admin',
--     lab_id = '75efd085-f7b8-4d18-a540-fadaead3637d'
-- WHERE email = 'kethavathajaykumar2002@gmail.com';

-- 1. Insert a new lab (if it doesn't already exist)
-- INSERT INTO labs (name, domain)
-- VALUES
--   ('Demo Lab', 'demo.myhealthapp.com')
-- ON CONFLICT (domain) DO NOTHING;

-- -- 2. Verify and copy the new lab’s UUID
-- SELECT * from labs;
-- -- WHERE domain = 'demo.myhealthapp.com';

-- -- 3. Update your user to be that lab’s admin
-- --    Replace <PASTE_UUID_HERE> with the id you copied above.
-- UPDATE users
-- SET
--   role   = 'lab_admin',
--   lab_id = '75efd085-f7b8-4d18-a540-fadaead3637d'
-- WHERE email = 'kethavathajaykumar2002@gmail.com';


-- select * from biomarker_types;




-- 1. Drop any existing users policies
-- DROP POLICY IF EXISTS select_users  ON users;
-- DROP POLICY IF EXISTS insert_users  ON users;
-- DROP POLICY IF EXISTS update_users  ON users;

-- -- 2. Turn RLS off on users
-- ALTER TABLE users DISABLE ROW LEVEL SECURITY;



-- create table user_roles (
--   user_id uuid primary key,
--   email text not null,
--   role text check (role in ('full', 'readonly')) not null,
--   lab_id uuid references labs(id)
-- );


-- insert into user_roles (user_id, email, role, lab_id)
-- values (
--   '522a6ccf-5c85-4d5d-9a15-55cede53054b',
--   'kethavathajaykumar2002@gmail.com',
--   'full',
--   null
-- );

-- update user_roles
-- set user_id = '522a6ccf-5c85-4d5d-9a15-55cede53054b'
-- where email = 'kethavathajaykumar2002@gmail.com';


-- select * from user_roles;

-- select * from biomarkers;


-- Enable RLS on the table (if not already enabled)
-- alter table pdf_files enable row level security;

-- -- Drop existing insert policy if it exists
-- drop policy if exists "Allow insert for owner" on pdf_files;

-- create policy "Allow insert for owner"
-- on pdf_files
-- for insert
-- with check (auth.uid() = user_id);

-- alter table pdf_files disable row level security;

-- -- Insert manually using a valid user_id
-- insert into pdf_files (user_id, file_path, file_name)
-- values (
--   '522a6ccf-5c85-4d5d-9a15-55cede53054b',
--   'uploads/test.pdf',
--   'test.pdf'
-- );

-- -- Re-enable RLS after testing
-- alter table pdf_files enable row level security;

-- select * from pdf_files limit 5;

select * from biomarkers order by date desc;

```

> **Note:**
>
> * Supabase Auth will create a `users` schema automatically. We store extra metadata (email, role, lab\_id) in `user_roles`.
> * Make sure RLS (Row-Level Security) is configured to allow only logged-in users to read/write their own biomarker rows. For admin pages, temporarily disable strict policies (or configure a separate “admin” role).

---

## 🔧 Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/bio-trackr.git
   cd bio-trackr
   ```

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   # .venv\Scripts\activate    # Windows
   ```

3. **Install Python dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up `.streamlit/secrets.toml`**
   Copy the template below into `.streamlit/secrets.toml` at the project root. Replace each placeholder with your actual keys:

   ```toml
   SUPABASE_URL = "https://<your-supabase-project>.supabase.co"
   SUPABASE_KEY = "<your-supabase-anon-or-service-role-key>"

   HF_API_TOKEN = "<your-huggingface-token-(if needed)>"
   OPENAI_API_KEY = "<your-openai-or-freeGPT-key>"

   [free_api]
   key = "<your-freeGPT-API-key>"
   base_url = "https://free.yunwu.ai/v1"
   default_model = "gpt-4o-mini"
   ```

   * **`SUPABASE_URL`** & **`SUPABASE_KEY`**: from Supabase → Settings → API
   * **`HF_API_TOKEN`** & **`OPENAI_API_KEY`**: only needed if you extend the AI chatbot further
   * The `[free_api]` section is used by the “Doctor Chatbot” page.

5. **Verify Supabase Tables & Storage**

   * In Supabase → Table Editor → Ensure that you have created the tables exactly as shown in “Database Schema.”
   * In Supabase → Storage → Buckets → Create a bucket named `reports`. Set it to **Private** so that only authenticated users can view/download.

6. **Configure Environment Variables** (optional)
   If you prefer using a `.env` file instead of `.streamlit/secrets.toml`, you can store:

   ```env
   SUPABASE_URL=https://<your-supabase-project>.supabase.co
   SUPABASE_KEY=<your-supabase-anon-or-service-role-key>
   HF_API_TOKEN=<your-huggingface-token-(if needed)>
   OPENAI_API_KEY=<your-openai-or-freeGPT-key>
   ```

   The code in `utils/auth.py` will first check `st.secrets`, then `os.getenv`.

7. **Run the App**
   From the repository root:

   ```bash
   streamlit run app.py
   ```

   * Visit `http://localhost:8501` in your browser.
   * If the page doesn’t load, ensure your virtual environment is activated and you have no port conflicts.

---

## 🏃‍♂️ Usage

1. **Sign Up / Login**

   * Go to **Login / Sign Up** page.
   * New users receive a confirmation email (via Supabase Auth).
   * By default, new signups are assigned the `readonly` role—email addresses in your `full_access_emails` list (in `utils/auth.py`) become `full` by default.

2. **Lab Onboarding**

   * “Lab Onboarding” (top-level sidebar link) is available to any `full` user.
   * Enter Lab Name, (optional) Logo URL, Brand Color, Custom Domain → “Create Lab.”

3. **Assigning Users to Labs & Roles**

   * Navigate to **Admin Panel → Manage Users** (only for `role="full"`).
   * Select a role (full | readonly) and a lab for each user, then click “✅ Update.”

4. **Manual Data Entry**

   * Go to **Data Entry**.
   * Choose biomarker from dropdown (units auto-populate), enter value & date, then click ➕ Submit.
   * Data is inserted into the `biomarkers` table under your `user.id`.

5. **Uploading PDFs**

   * Go to **Upload PDF**. Select a PDF file, click “Upload & Extract.”
   * The file is saved to Supabase Storage under the path `{user.id}/{uuid}.pdf`.
   * Raw text is displayed in a text area. Parsed biomarker values (date, value, unit) appear below. Click “💾 Save Extracted Data” to insert them into the DB.

6. **Viewing Dashboards**

   * Go to **Dashboard**.
   * Choose which biomarkers to display (Glucose, WBC count, Hemoglobin).
   * A combined line chart with points is rendered (Altair), flagged in red for any out-of-range values.
   * Below, per-biomarker detailed tables show ✅ (normal) / ❌ (abnormal) next to each entry.

7. **Admin Dashboard & Metrics**

   * Users with `role="full"` see **Admin Dashboard** in the sidebar (labeled “Admin Dashboard | Biomarker Tracker”).
   * Metrics displayed: total labs, total users, uploaded PDFs, biomarker entries.
   * Below metrics, each lab’s details (name, domain, primary color, assigned users) are listed.

8. **Admin Data Entry for Patients**

   * Available only to `role="full"`.
   * Navigate to **Upload for Patient**.
   * Enter patient’s phone number (used as `user_id`), select biomarker, value, date → click “Submit Data” to save under that patient’s account.

9. **AI Doctor Chatbot**

   * Navigate to **👩‍⚕️ AI Doctor**.
   * Type a medical question; GPT-free API replies in streaming format.
   * All chat history is preserved in Streamlit’s session state.

---

## 📋 Environment & Configuration Details

* **Streamlit Configuration**

  * `app.py` sets the initial sidebar menu based on `get_user_role()`.
  * Each page calls `get_user()` and `get_user_role()` to enforce access control.
  * The sidebar only shows pages that the logged-in user has permission to view.

* **Supabase Client**

  * In `utils/auth.py`, `get_supabase_client()` is cached with `@st.cache_resource`.
  * All CRUD operations use `supabase.table(...).insert(...)`, `.select(...).eq(...)`, or `.update(...).eq(...)`.

* **PDF Parsing & OCR**

  * `utils/pdf_parser.py` first attempts `pdfminer_extract_text`. If empty or fails, it converts each page with `pdf2image.convert_from_bytes` → runs `pytesseract.image_to_string` on each image.
  * `extract_biomarkers()` uses regex patterns (case-insensitive) for “glucose,” “wbc,” and “hemoglobin” followed by numeric values and optional units.
  * Dates are extracted by scanning for formats (`DD/MM/YYYY`, `YYYY-MM-DD`, `D Month YYYY`)—fallback to today’s date if none found.

* **Roles & Permissions**

  * `get_user_role(user_id)` queries `user_roles` table.
  * Only `role="full"` can access Admin pages, Lab onboarding, Admin Data Entry. `role="readonly"` can view Dashboard only.
  * In future, you may extend to `role="admin"` for superuser privileges.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** this repository.
2. **Create a new branch** (`git checkout -b feature/your-feature-name`).
3. **Make your changes** and commit them (`git commit -m "Add <feature>"`).
4. **Push to your branch** (`git push origin feature/your-feature-name`).
5. Open a **Pull Request** describing your changes.

### Guidelines

* Keep code style consistent (PEP8 for Python).
* Write meaningful commit messages.
* If you add new dependencies, update `requirements.txt`.
* If you alter database schema, update the “Database Schema” section in this README.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE). You may modify or redistribute under the same terms. (Create a `LICENSE` file if you choose MIT.)

---

## 🙏 Acknowledgments

* [Supabase](https://supabase.com/) for the managed Postgres, Auth, and Storage.
* [Streamlit](https://streamlit.io/) for making rapid UI prototyping extremely easy.
* [pdfminer.six](https://github.com/pdfminer/pdfminer.six) & [pytesseract](https://github.com/madmaze/pytesseract) for PDF text extraction.
* [Altair](https://altair-viz.github.io/) for declarative charting.
* [free.yunwu.ai](https://free.yunwu.ai/) for the open GPT-based medical chatbot endpoint.

---

**Ready to get started?**

1. Fork & clone this repo.
2. Fill in your Supabase secrets.
3. Run `streamlit run app.py` and begin tracking biomarkers securely in BioTrackr!
