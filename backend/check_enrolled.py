import urllib.request
import json

base = 'http://127.0.0.1:8000'

# Check health
req = urllib.request.Request(
    f'{base}/health',
    headers={'Content-Type': 'application/json'},
)

try:
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode())
        print('HEALTH:', data)
        enrolled = data.get('enrolled_subjects', [])
        print(f'Enrolled subjects: {enrolled}')
        print(f'Is browser-test-001 enrolled: {"browser-test-001" in enrolled}')
except Exception as e:
    print('ERROR:', e)
