import pandas as pd

from django.contrib.auth.models import User


URL = 'https://www.utoptify.com/cards/'

usernames = User.objects.filter(card__region='AME').values('username', 'first_name', 'last_name', 'email')
df = pd.DataFrame(list(usernames))
df['URL'] = df['username'].apply(lambda u: URL + u)
df.drop('username', inplace=True, axis=1)
df.to_csv('./americas_cards.csv')