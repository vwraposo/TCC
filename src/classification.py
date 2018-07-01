from sklearn import svm, preprocessing
from sklearn.cluster import KMeans
import numpy as np
import psycopg2
import sys

try:
    conn = psycopg2.connect(dbname="snakesdb",  user="fox", password="senha")
except:
    print("Error: It was not possible to connect to the database")
    sys.exit(1)

cur = conn.cursor()


eat = dict()
try:
    cur.execute("SELECT * FROM eating;")
except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

for tup in cur: 
    eat[tup[0]] = list(tup[2:])

geo = dict()
try:
    cur.execute("SELECT * FROM geography;")
except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

for tup in cur: 
    if tup[0] not in geo:
        geo[tup[0]] = []
    geo[tup[0]].append(tup[1])

try:
    cur.execute("SELECT DISTINCT loc FROM geography;")
except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        print("Rollback complete")

tmp = [tup[0] for tup in cur]
places = []
for p in tmp:
    insert = True
    for q in tmp:
        if q != p and p in q[-2:]:
            insert = False

    if (insert):
        places.append(p)

records = eat.copy()
for r in records:
    records[r] = records[r] + [0] * len(places)
    for p in geo[r]:
        if p in places:
            records[r][places.index(p)+6] = 1
        else:
            for l in places:
                if p in l[-2:]:
                    if r == 'erythromelas':
                        print(p + " " + l)
                    records[r][places.index(l)+6] = 1

X = [ 
     records['jararaca'], records['insularis'], records['jararacussu'], records['moojeni']
    ]
X = preprocessing.scale(X)

kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
print("K-means result: " + str(kmeans.labels_))

#Clustering Hierarquico
sn = ['jararaca', 'insularis', 'jararacussu', 'moojeni']
print((15*' ')  + str(sn))
for r in sn:
    d = list(map(lambda x: np.abs(np.linalg.norm(np.array(records[x]) - np.array(records[r]))), sn))
    d = list(map(lambda x: "{0:.2f}".format(x), d))
    print(r + ((15 - len(r))* ' ')  + str(d))

cur.close()
conn.close()
