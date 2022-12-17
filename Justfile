set dotenv-load := true
export PATH := ".venv/bin:" + env_var('PATH')

help:
    just --list --unsorted

shell *ARGS:
    {{ARGS}}

run:
    python manage.py runserver

generate-schema:
    ./manage.py generateschema --file openapi.yaml
