# Blurb Forum
A Simple Web Forum built using Flask and Vue.JS

# Prerequisites
- Python 3.13
- Node v24.22.2

# Running the app
Copy `.env.example` to `.env` and set variables accordingly.

- `SECRET_KEY` can be generated via:
```sh
python -c "import secrets; print(secrets.token_urlsafe())"
```

- `SECURITY_PASSWORD_SALT` can be generated via:
```sh
python -c "import secrets; print(secrets.SystemRandom().getrandbits(128))"
```

## Manually (without docker)
### Backend Server
```sh
cd ./backend
uv sync
uv run python app.py
```

