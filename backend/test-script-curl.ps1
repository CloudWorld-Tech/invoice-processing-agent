$body = '{"folder_path": "sample_invoices"}'
curl.exe -N -X POST http://localhost:8000/runs/stream -H "Content-Type: application/json" -d $body