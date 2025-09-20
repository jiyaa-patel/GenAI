# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Backend integration (Django + FastAPI)

Create a `.env` file in `frontend2/` with:

```
VITE_DJANGO_BASE_URL=http://localhost:8000
VITE_FASTAPI_BASE_URL=http://localhost:8001
```

The React app calls:
- Django (auth endpoints) at `${VITE_DJANGO_BASE_URL}/api/...`
- FastAPI (documents/chat) at `${VITE_FASTAPI_BASE_URL}/api/...`

Run the backends from `backEnd`:

```
# Django (users auth, JWT, media)
cd ../backEnd
python manage.py runserver 0.0.0.0:8000

# FastAPI (document upload, chat)
cd geniai
python run_fastapi.py
```

Then start the frontend:

```
cd ../frontend2
npm run dev
```
