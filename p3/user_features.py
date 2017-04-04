import numpy as np
import pandas as pd

df = pd.read_csv('profiles.csv')

df['Male'] = (df['sex'] == 'm').astype(int)
df['Female'] = (df['sex'] == 'f').astype(int)

df = pd.concat([df, pd.get_dummies(df['country'], prefix='country', prefix_sep=' ')], axis=1)
df = df.drop(['sex', 'country'], axis=1)

df.to_csv('user features.csv')
