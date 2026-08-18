# Job Application Form — Forms, Validation & Real User Feedback

## Structure
- `backend/` — Flask API with server-side validation, SQLite storage, file upload handling
- `frontend/` — Plain HTML/CSS/JS form with client-side validation

## Fields (7 total, meets 6+ requirement)
1. Full Name — text
2. Email — text (regex validated)
3. Phone Number — text (regex validated)
4. Department — **dropdown/select**
5. Date of Birth — **date input**
6. Bio — textarea (optional, max 500 chars)
7. Profile Photo — **file/image input**

## How to run

### Backend
```
cd backend
pip install -r requirements.txt --break-system-packages
python app.py
```
Runs on `http://localhost:5000`

### Frontend
Just open `frontend/index.html` in a browser, or serve it:
```
cd frontend
python -m http.server 8080
```
Then visit `http://localhost:8080`

## Validation layers
- **Client-side** (`script.js`): checks required fields, email/phone regex, age from DOB (16-100), file type/size, bio length — with field-specific error messages, and un-marks errors as user types.
- **Server-side** (`app.py`): re-validates everything independently (never trusts frontend) — same rules, plus checks actual uploaded file extension and size on disk. Returns `400` with per-field `errors` object on failure.

## UX requirements covered
- Success/error banners after submission
- Submit button disabled + spinner shown while request is in-flight
- Server-side field errors get mapped back onto the same input fields as client errors

## For your video/LinkedIn submission
1. Fill the form correctly → submit → show success banner.
2. Fill it incorrectly (e.g. bad email, no photo, underage DOB) → show client-side errors blocking submission.
3. Optionally, temporarily comment out the `validateForm()` check in `script.js`, submit bad data, and show the **server** rejecting it with its own error messages — proves the backend doesn't trust the frontend.
