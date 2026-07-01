# MedNXT HHRM - Phase 1 (Modules 1-3)

This repository contains the production-ready code for Phase 1 of the MedNXT Hospital Human Resource Management (HHRM) module.

## Features Completed
1. **Department Management**: CRUD operations, search, pagination, multi-tenant isolation.
2. **Designation Management**: CRUD operations, grade management, search, multi-tenant isolation.
3. **Employee Management**: Comprehensive employee registration covering personal, employment, and professional details. Automatic `EMP-XXXX` code generation.
4. **Architecture**: FastAPI, PostgreSQL, Docker, Multi-tenant DB isolation (`X-Tenant-ID` header).

## How to Deploy to Railway

1. **Push to GitHub**:
   Initialize a git repository in this folder, commit all files, and push to a new GitHub repository.
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Phase 1 Modules 1-3"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to [Railway.app](https://railway.app/).
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Select your newly created repository.
   - Railway will automatically detect the `Dockerfile` and start building the application.

3. **Add PostgreSQL Database in Railway**:
   - In your Railway project, click **New** -> **Database** -> **Add PostgreSQL**.
   - Once provisioned, copy the `DATABASE_URL` from the PostgreSQL variables.
   - Go to your FastAPI service variables in Railway, and add `DATABASE_URL` with the copied value.
   - Add `DEFAULT_TENANT_ID` variable (e.g., `00000000-0000-0000-0000-000000000001`).
   
4. **Access the API**:
   - Railway will generate a public domain (e.g., `https://mednxt-hhrm-production.up.railway.app`).
   - Go to `https://<your-domain>/docs` to view and interact with the Swagger API documentation.

## Local Testing (Docker Compose)
To run the application locally for testing:
```bash
docker-compose up --build
```
- API Docs: http://localhost:8000/docs
- Frontend: Open `frontend/index.html` in your browser.
