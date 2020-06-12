# %%
import requests
import pandas as pd
import xml.etree.ElementTree as et
pd.set_option('display.float_format', lambda x: '%.3f' % x)
import json

# %%
t = et.fromstring(requests.get('https://www.smscr.cz/kalkulacka/rud/resources/data_2020.xml').text)

# %%
def unp(row):
    out = {}
    for val in row:
        out[val.tag] = val.text
    return out

d = pd.DataFrame.from_dict(list(map(lambda x: unp(x), t)))

# %%
d.head(2)

# %%
d[[e for e in d.columns if e not in ['n','Okres', 'Kraj','kod']]] = d[[e for e in d.columns if e not in ['n','Okres', 'Kraj','kod']]].applymap(float)

# %%
d.kod = d.kod.apply(lambda x: x.replace(' ', ''))
d.n = d.n.apply(lambda x: x.split(' (')[0])

# %%
# dsn2
d['komp_balicek'] = d.pob * 1200

# %%
# ztrata csr_20
dph_20 = 111700000000
dppo_20 = 44600000000
dpfo_20 = 64800000000
zc_20 = 55400000000
priznani_20 = 1100000000
srazka_20 = 4800000000
zamestnanci_20 = 3500000000
bonus_kraje = 4014000000
danovy_balicek_obce=7500000000
danovy_balicek_kraje=2830000000

def csr(k1, k2):
    kk1 = k1/100
    kk2 = k2/100

    sm = (dph_20 + dppo_20 + zc_20 + priznani_20 + srazka_20)*kk1 + zamestnanci_20*kk2

    return sm*0.8 - sm + (-675000000*kk2 - 10611000000*kk1) - 7215480000*kk1

d['celk_ztrata'] = d.apply(lambda row: csr(row.k1, row.k2), axis=1)

# %%
# odhadovany prijem c1
def c1(k1, k2):
    kk1 = k1/100
    kk2 = k2/100

    return (dph_20 + dppo_20 + zc_20 + priznani_20 + srazka_20)*kk1 + zamestnanci_20*kk2

d['celk_prijem_20'] = d.apply(lambda row: c1(row.k1, row.k2), axis=1)

# %%
with open('./obce.geojson', encoding='utf-8') as f:
    gjs = json.load(f)

# %%
out = []
for ftr in gjs['features']:
    try:
        tmp = list(d[d.kod == ftr['properties']['KOD_OBEC']].to_dict(orient='index').values())[0]

        out.append([
            tmp['n'], 
            tmp['Okres'],
            round(tmp['komp_balicek']), 
            round(tmp['celk_ztrata']*-1.0), 
            round(tmp['celk_prijem_20']), 
            int(tmp['pob'])])
    except:
        print(ftr['properties']['KOD_OBEC'])
   
# %%
with open('mapa.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(out, ensure_ascii=False))
# %%
d.columns


# %%
(d.celk_ztrata / d.pob).max()

# %%
