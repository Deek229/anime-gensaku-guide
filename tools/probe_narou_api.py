import gzip
import io
import json
import sys
from datetime import date, timedelta

import requests

sys.stdout.reconfigure(encoding='utf-8')

d = date.today()
for days_back in range(0, 5):
    target = d - timedelta(days=days_back)
    rtype = f"{target.strftime('%Y%m%d')}-d"
    url = f'https://api.syosetu.com/rank/rankget/?rtype={rtype}&out=json&gzip=5'
    r = requests.get(url, timeout=30)
    print('rank', rtype, r.status_code, len(r.content))
    if r.status_code != 200:
        continue
    data = json.loads(gzip.decompress(r.content))
    print('  structure:', type(data), len(data) if isinstance(data, list) else data.keys())
    if isinstance(data, list) and len(data) > 1:
        print('  item0:', data[0])
        print('  item1:', data[1][:5] if isinstance(data[1], list) else data[1])
        ncodes = [x[1] if isinstance(x, list) else x.get('ncode') for x in data[1:4]]
        print('  ncodes sample:', ncodes)
        ncodes = '-'.join(x['ncode'] for x in data[:5])
        nu = (
            'https://api.syosetu.com/novelapi/api/?out=json&gzip=5'
            f'&of=t-n-w-s-e-i-bg-g-k-gl&ncode={ncodes}'
        )
        nr = requests.get(nu, timeout=30)
        nd = json.loads(gzip.decompress(nr.content))
        print('  novel count', nd[0].get('allcount'), 'first', nd[1] if len(nd) > 1 else None)
        break
