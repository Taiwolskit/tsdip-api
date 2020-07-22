# tsdip-api

Taiwan Street Dance Information Platform API Server

## Setup

### PostgreSQL

#### Initial

`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`

Change migrations `alembic.ini`

`file_template = %%(year)d%%(month).2d%%(day).2d%%(hour).2d%%(minute).2d%%(second).2d_%%(rev)s_%%(slug)s`

### Environment

| Variable                | Value                                                     |
| ----------------------- | --------------------------------------------------------- |
| API_TOKEN               | Admin API key                                             |
| FLASK_APP               | `flasky.py`                                               |
| FLASK_ENV               | `production`, `development`                               |
| JWT_SECRET_KEY          | JWT secret key                                            |
| SENDGRID_API_KEY        | SendGrid API key                                          |
| SQLALCHEMY_DATABASE_URI | `postgresql://{username}:{password}@{ip}:5432/{database}` |
| SYSTEM_SENDER           | Email from                                                |
