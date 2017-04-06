import datetime
from sys import maxint
import time

import musicbrainzngs as mbz
import numpy as np
import pandas as pd

df = pd.read_csv('artists.csv', usecols=['artist'])
df.columns = ['id']
print 'imported ids'

mbz.set_useragent('CS 181 fetcher', '1', 'nwolfe@college.harvard.edu')
mbz.set_rate_limit()

df['Person'] = \
    df['Group'] = \
    df['Male'] = \
    df['Female'] = \
    df['years old'] = \
    df['number of releases'] = \
    df['years since first release'] = \
    df['years since last release'] = \
    df['years since average release'] = np.zeros(len(df), dtype=int)

df['years since average release'] = \
    df['releases live percentage'] = np.zeros(len(df), dtype=float)
df['releases album percentage'] = np.ones(len(df), dtype=float)

current_year = datetime.date.today().year

for (idx, mbz_id) in enumerate(df['id']):
    try:
        data = mbz.get_artist_by_id(
            mbz_id,
            includes=['release-groups', 'tags']
        )['artist']
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
            df.loc[idx, 'years old'] = (current_year
                                        - int(data['life-span']['begin'][:4]))

    if 'release-group-count' in data:
        df.loc[idx, 'number of releases'] = data['release-group-count']

    if 'release-group-list' in data:
        year_count = 0
        first = None
        last = None
        year_total = 0
        
        type_count = 0
        albums = 0
        lives = 0
        
        for release in data['release-group-list']:
            if 'first-release-date' in release:
                if len(release['first-release-date']) >= 4:
                    year_count += 1
                    year = int(release['first-release-date'][:4])
                    year_total += year
                    if first is None or year < first:
                        first = year
                    if last is None or year > last:
                        last = year
            if 'primary-type' in release:
                type_count += 1
                if 'Live' in release.get('secondary-type-list', []):
                    lives += 1
                elif release['primary-type'] == 'Album':
                    albums += 1

        if year_count > 0:
            df.loc[idx, 'years since first release'] = current_year - first
            df.loc[idx, 'years since last release'] = current_year - last
            df.loc[idx, 'years since average release'] = (
                current_year - (year_total * 1.0 / year_count)
            )
        if type_count > 0:
            df.loc[idx, 'releases album percentage'] = albums * 1.0 / type_count
            df.loc[idx, 'releases live percentage'] = lives * 1.0 / type_count

    if 'country' in data:
        country = data['country']
        if 'country ' + country not in df:
            df['country ' + country] = np.zeros(len(df), dtype=int)
        df.loc[idx, 'country ' + country] = 1

    if 'tag-list' in data:
        for tag in data['tag-list']:
            if int(tag['count']) > 0:
                if tag['name'] not in df:
                    df[tag['name']] = np.zeros(len(df), dtype=int)
                df.loc[idx, tag['name']] = 1

    if (idx + 1) % 50 == 0:
        print idx + 1

for (idx, label) in enumerate(df.columns):
    if df[label].sum() <= 1:
        df = df.drop(label, axis=1)
        continue
    try:
        df = df.rename(columns={label: str(label)})
    except UnicodeEncodeError:
        df = df.rename(columns={label: idx})
df.to_csv('artist features.csv')
