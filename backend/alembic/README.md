# Alembic workflow

## Create a revision

From the backend directory, run:

```bash
alembic revision --autogenerate -m "initial schema"
```

## Apply migrations

```bash
alembic upgrade head
```

## Roll back one revision

```bash
alembic downgrade -1
```

## Notes

- The migration environment uses the async SQLAlchemy engine.
- The migration metadata is driven by the shared declarative base in app/database/base.py.
- The domain models are imported through app.models.domain so autogenerate sees the full schema.
