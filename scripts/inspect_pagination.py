import os
import sys
from pathlib import Path
# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogapp.settings')
import django
django.setup()
from django.test import Client
import re
c = Client()
r = c.get('/blog/', HTTP_HOST='127.0.0.1')
s = r.content.decode('utf-8', 'ignore')
m = re.search(r'(<div[^>]*class="pagination".*?</div>)', s, re.S)
if m:
	print(m.group(1))
else:
	print('NOT_FOUND')

# Also check for the debug banner
if 'DEBUG PAGE' in s:
	i = s.find('DEBUG PAGE')
	start = max(0, i-120)
	end = min(len(s), i+120)
	print('\n--- DEBUG SNIPPET ---')
	print(s[start:end])
else:
	print('\nDEBUG BANNER NOT FOUND')
