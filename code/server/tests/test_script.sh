#!/usr/bin/env bash

curl -X POST 'http://localhost:5000/create_record/alice' -H "Content-Type: application/json" -d '{"description": "Visit 1"}'
curl -X POST 'http://localhost:5000/create_record/alice' -H "Content-Type: application/json" -d '{"description": "Visit 2"}'

curl -X POST 'http://localhost:5000/create_record/bob' -H "Content-Type: application/json" -d '{"description": "Visit 1"}'
curl -X POST 'http://localhost:5000/create_record/bob' -H "Content-Type: application/json" -d '{"description": "Visit 2"}'
curl -X POST 'http://localhost:5000/create_record/bob' -H "Content-Type: application/json" -d '{"description": "Visit 3"}'

sleep 1

curl -X POST 'http://localhost:5000/change_record/bob/5045b47712e8e1d411e9d2f3d11e2b4a' -H "Content-Type: application/json" -d '{"description": "Visit 1"}'