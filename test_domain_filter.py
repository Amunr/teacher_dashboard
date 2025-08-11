import requests

# Test the API with domain filter
url = 'http://127.0.0.1:5000/api/dashboard-data'
params = {'domain': 'Mathematics'}

try:
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print('Domain filter test:')
        print(f'Domain scores: {len(data.get("domain_scores", []))} items')
        print(f'Subdomain scores: {len(data.get("subdomain_scores", []))} items')
        if data.get('subdomain_scores'):
            print('Subdomains found:', [s['subdomain'] for s in data['subdomain_scores'][:3]])
        print(f'School readiness: {data.get("school_readiness_percent", "N/A")}%')
        print(f'Average score: {data.get("average_score", "N/A")}%')
    else:
        print(f'API error: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')

# Also test without domain filter
print('\n' + '='*50)
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print('No filter test:')
        print(f'Domain scores: {len(data.get("domain_scores", []))} items')
        print(f'Subdomain scores: {len(data.get("subdomain_scores", []))} items')
        if data.get('domain_scores'):
            print('Domains found:', [s['domain'] for s in data['domain_scores'][:3]])
        print(f'School readiness: {data.get("school_readiness_percent", "N/A")}%')
        print(f'Average score: {data.get("average_score", "N/A")}%')
    else:
        print(f'API error: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')
