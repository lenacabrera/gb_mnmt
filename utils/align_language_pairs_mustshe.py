import csv
import pandas as pd
import numpy as np

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
# id_df = pd.read_csv('MULTILINGUAL_v1.2.csv')
es = pd.read_csv('MONOLINGUAL.es_v1.2.csv', sep=';')
fr = pd.read_csv('MONOLINGUAL.fr_v1.2.csv', sep=';')
it = pd.read_csv('MONOLINGUAL.it_v1.2.csv', sep=';')

es_ordered_all = []
fr_ordered_all = []
it_ordered_all = []

es_ordered = []
fr_ordered = []
it_ordered = []

headers = es.columns
# print(list(headers))

with open('MULTILINGUAL_v1.2.csv', newline='', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
    # skip header (IT;FR;ES;CATEGORY)
    csv_reader.__next__()
    for row in csv_reader:
        it_id = row[0].split(';')[0]
        fr_id = row[0].split(';')[1]
        es_id = row[0].split(';')[2]

        if it_id != 'NULL':
            it_ordered_all.append(it.loc[it['ID'] == it_id])
        else:
            it_ordered_all.append(pd.Series("", index=headers))

        if fr_id != 'NULL':
            fr_ordered_all.append(fr.loc[fr['ID'] == fr_id])
        else:
            fr_ordered_all.append(pd.Series("", index=headers))

        if es_id != 'NULL':
            es_ordered_all.append(es.loc[es['ID'] == es_id])
        else:
            es_ordered_all.append(pd.Series("", index=headers))

        if it_id == 'NULL' or fr_id == 'NULL' or es_id == 'NULL':
            continue
        else:
            it_ordered.append(it.loc[it['ID'] == it_id])
            fr_ordered.append(fr.loc[fr['ID'] == fr_id])
            es_ordered.append(es.loc[es['ID'] == es_id])


it_ = pd.concat(it_ordered_all, sort=False)
it_ = it_[headers]
it_.to_csv("it_all.csv", index=False, sep=';')

fr_ = pd.concat(fr_ordered_all, sort=False)
fr_ = fr_[headers]
fr_.to_csv("fr_all.csv", index=False, sep=';')

es_ = pd.concat(es_ordered_all, sort=False)
es_ = es_[headers]
es_.to_csv("es_all.csv", index=False, sep=';')


it_ = pd.concat(it_ordered, sort=False)
it_ = it_[headers]
it_.to_csv("it.csv", index=False, sep=';')

fr_ = pd.concat(fr_ordered, sort=False)
fr_ = fr_[headers]
fr_.to_csv("fr.csv", index=False, sep=';')

es_ = pd.concat(es_ordered, sort=False)
es_ = es_[headers]
es_.to_csv("es.csv", index=False, sep=';')
