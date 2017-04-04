import datetime
import time

import musicbrainzngs as mbz
import numpy as np
import pandas as pd

df = pd.read_csv('artists.csv', usecols=['artist'])
df.columns = ['id']
print 'imported ids'

mbz.set_useragent('CS 181 fetcher', '1', 'nwolfe@college.harvard.edu')
mbz.set_rate_limit()

df['Person'] = df['Group'] = df['Male'] = df['Female'] = df['years old'] = (
    np.zeros(len(df), dtype=int)
)

for (idx, mbz_id) in enumerate(df['id']):
    try:
        data = mbz.get_artist_by_id(mbz_id)['artist']
    except:
        continue
    if 'type' in data:
        if data['type'] == 'Person':
            df.loc[idx, 'Person'] = 1
            if 'gender' in data:
                df.loc[idx, data['gender']] = 1
        elif data['type'] == 'Group':
            df.loc[idx, 'Group'] = 1

    if 'life-span' in data:
        if 'begin' in data['life-span']:
            df.loc[idx, 'years old'] = (datetime.date.today().year
                                        - int(data['life-span']['begin'][:4]))
    if 'country' in data:
        country = data['country']
        if country not in df:
            df['country ' + country] = np.zeros(len(df), dtype=int)
        df.loc[idx, 'country ' + country] = 1

    if (idx + 1) % 50 == 0:
        print idx + 1

df.to_csv('artist features.csv')
