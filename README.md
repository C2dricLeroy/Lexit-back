# 🔐 Lexit - Backend

A secure RESTful API for the **Lexit** application, built with **FastAPI**, using **JWT** for authentication, **SQLModel** for data access, and **SonarCloud** for static code analysis.

## 🧪 Code Quality

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=C2dricLeroy_Lexit-back)](https://sonarcloud.io/summary/new_code?id=C2dricLeroy_Lexit-back)

---

## 🚀 Features

- OAuth2 authentication with JWT
- Retrieve the current user from a secure token
- User account creation and management
- JWT decoding, validation, and expiration handling
- Clear separation of concerns (routes, security, models)
- Unit tests with `pytest` and `unittest.mock`
- Static code analysis via SonarCloud

---

## 🛠️ Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [PyJWT](https://pyjwt.readthedocs.io/)
- [SonarCloud](https://sonarcloud.io/)
- [pytest](https://docs.pytest.org/)

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/lexit-back.git
   cd lexit-back
   ```
2. **Configuration**
    Add a .env file at the root of the project with:
    ```
    JWT_SECRET_KEY=your-secret-key
    JWT_ALGORITHM=HS256
    DATABASE_URL=sqlite:///./lexit.db
    ```
3. **Install dependencies**
    ```
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
4. **Start the development server** 
    ```
    uvicorn app.main:app --reload
    ```
5. **Docker (optional)**
You can also run the project using Docker and make:
    ```
    make start
    ```
