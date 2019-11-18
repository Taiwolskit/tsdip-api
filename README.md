# tsdip-api

Taiwan Street Dance Information Platform API Server

## Setup

### PostgreSQL

#### Initial

`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`

Change migrations `alembic.ini`

`file_template = %%(year)d_%%(month).2d%%(day).2d%%(hour).2d%%(minute).2d%%(second).2d_%%(rev)s_%%(slug)s`
