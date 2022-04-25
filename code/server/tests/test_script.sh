#!/usr/bin/env bash

curl -X POST 'http://localhost:5000/create_record/alice' -H "Content-Type: application/json" -d '{"description": "Visit 1"}'
curl -X POST 'http://localhost:5000/create_record/alice' -H "Content-Type: application/json" -d '{"description": "Visit 2"}'

curl -X POST 'http://localhost:5000/create_record/bob' -H "Content-Type: application/json" -d '{"description": "Visit 1"}'
curl -X POST 'http://localhost:5000/create_record/bob' -H "Content-Type: application/json" -d '{"description": "Visit 2"}'
curl -X POST 'http://localhost:5000/create_record/bob' -H "Content-Type: application/json" -d '{"description": "Visit 3"}'

sleep 1

