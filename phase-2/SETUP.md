# Phase 2 - Todo App Setup & Usage

## 🚀 Quick Start

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Start server (from repo root)
cd phase-2
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- Backend runs on **http://localhost:8000**
- API docs at **http://localhost:8000/docs** (Swagger UI)

### Frontend
```bash
# Install dependencies
npm install
cd frontend

# Start dev server
npm run dev
```
- Frontend runs on **http://localhost:3000**
- Open in browser: **http://localhost:3000**

---

## 🔐 Authentication Flow

1. **Go to login page:** http://localhost:3000/login
2. **Create account:**
   - Enter email & password
   - Click "Create Account"
   - Session saved locally in `localStorage`
3. **Redirects to tasks page** with Bearer token
4. **All API calls include `Authorization: Bearer <token>`**

---

## 📝 Features

### Frontend
- ✅ Sign Up / Sign In page with form validation
- ✅ Protected `/todos` route (redirects to login if not authenticated)
- ✅ Add tasks
- ✅ Toggle task completion
- ✅ Delete tasks
- ✅ Progress bar
- ✅ Logout button

### Backend
- ✅ JWT-based authentication (7-day expiry)
- ✅ Password hashing with bcrypt
- ✅ User model in database (email + password_hash)
- ✅ Task CRUD endpoints (all require valid JWT)
- ✅ User-scoped task queries (users only see their own tasks)

---

## 🗄️ Database

- **Default:** SQLite (`dev.db`) for local development
- **Production:** Set `DATABASE_URL` in `.env` for Neon/Postgres

```bash
# Example .env for Neon
DATABASE_URL=postgresql://user:password@host:5432/dbname
BETTER_AUTH_SECRET=your-secret-key
```

See `.env.example` for template.

---

## 🔌 API Endpoints

### Auth
- `POST /api/auth/sign-up` → Create account
- `POST /api/auth/sign-in` → Login
- `POST /api/auth/sign-out` → Logout
- `GET /api/auth/session` → Get current session (no auth required)

### Tasks (all require `Authorization: Bearer <token>`)
- `GET /api/tasks` → Get all tasks for current user
- `POST /api/tasks` → Create task
- `GET /api/tasks/{id}` → Get single task
- `PUT /api/tasks/{id}` → Update task
- `DELETE /api/tasks/{id}` → Delete task
- `PATCH /api/tasks/{id}/complete` → Mark complete

---

## 🧪 Testing

### Sign up & create tasks:
```bash
curl -X POST http://localhost:8000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Get tasks (with token):
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your_token_here>"
```

---

## 📦 Tech Stack

**Backend:**
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- JWT (PyJWT)
- Bcrypt (password hashing)
- Uvicorn

**Frontend:**
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS

---

## 🐛 Troubleshooting

### Backend won't start
- Check if `requirements.txt` is installed: `pip list | grep fastapi`
- Ensure port 8000 is free: `netstat -an | findstr :8000`

### Frontend can't reach backend
- Ensure backend is running on 8000
- Check `NEXT_PUBLIC_API_URL` env var (defaults to `http://localhost:8000`)

### Auth fails
- Check `BETTER_AUTH_SECRET` is set (or uses default)
- Verify user exists in DB (check `dev.db` for SQLite)

### Tasks not loading
- Ensure you're logged in (check localStorage for `auth_session`)
- Verify Bearer token is included in requests (check browser DevTools > Network tab)

---

## ✨ Next Steps

- [ ] Add email verification
- [ ] Add password reset
- [ ] Add task categories/labels
- [ ] Add due dates
- [ ] Add task sharing
- [ ] Deploy to production

