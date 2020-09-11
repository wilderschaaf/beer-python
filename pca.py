from db import establish_connection, create_cursor, close_connection
from sklearn.decomposition import TruncatedSVD
from sklearn.utils import check_array
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier
from math import sqrt
length = 20000
dim = 9

styledict = {"German Bock":"Bock",
            "German Doppelbock":"Bock",
            "German Eisbock":"Bock",
            "German Maibock":"Bock",
            "German Weizenbock":"Bock",
            "American Brown Ale":"Brown Ale",
            "English Brown Ale":"Brown Ale",
            "English Dark Mild Ale":"Brown Ale",
            "German Altbier":"Brown Ale",
            "American Black Ale" :"Dark Ale",
            "Belgian Dark Ale":"Dark Ale",
            "Belgian Dubbel":"Dark Ale",
            "German Roggenbier":"Dark Ale",
            "Scottish Ale":"Dark Ale",
            "Winter Warmer":"Dark Ale",
            "American Amber / Red Lager":"Dark Lager",
            "European Dark Lager":"Dark Lager",
            "Dark Lagers":"Dark Lager",
            "German Märzen / Oktoberfest":"Dark Lager",
            "German Rauchbier":"Dark Lager",
            "German Schwarzbier":"Dark Lager",
            "Munich Dunkel Lager":"Dark Lager",
            "Vienna Lager":"Dark Lager",
            "American Cream Ale":"Hybrid Beer",
            "Bière de Champagne / Bière Brut":"Hybrid Beer",
            "Braggot":"Hybrid Beer",
            "California Common / Steam Beer":"Hybrid Beer",
            "American Brut IPA":"India Pale Ale",
            "American Imperial IPA":"India Pale Ale",
            "American IPA":"India Pale Ale",
            "Belgian IPA":"India Pale Ale",
            "English India Pale Ale (IPA)":"India Pale Ale",
            "New England IPA":"India Pale Ale",
            "American Amber / Red Ale":"Pale Ale",
            "American Blonde Ale":"Pale Ale",
            "American Pale Ale (APA)":"Pale Ale",
            "Belgian Blonde Ale ":"Pale Ale",
            "Belgian Pale Ale":"Pale Ale",
            "Belgian Saison":"Pale Ale",
            "English Bitter":"Pale Ale",
            "English Extra Special / Strong Bitter (ESB)":"Pale Ale",
            "English Pale Ale":"Pale Ale",
            "English Pale Mild Ale":"Pale Ale",
            "French Bière de Garde":"Pale Ale",
            "German Kölsch":"Pale Ale",
            "Irish Red Ale":"Pale Ale",
            "American Adjunct Lager":"Pilseners and Pale Lager",
            "American Imperial Pilsner":"Pilseners and Pale Lager",
            "American Lager":"Pilseners and Pale Lager",
            "American Light Lager":"Pilseners and Pale Lager",
            "American Malt Liquor":"Pilseners and Pale Lager",
            "Bohemian Pilsener":"Pilseners and Pale Lager",
            "European Export / Dortmunder":"Pilseners and Pale Lager",
            "European Pale Lager":"Pilseners and Pale Lager",
            "European Strong Lager":"Pilseners and Pale Lager",
            "German Helles":"Pilseners and Pale Lager",
            "German Kellerbier / Zwickelbier":"Pilseners and Pale Lager",
            "German Pilsner":"Pilseners and Pale Lager",
            "American Imperial Porter":"Porter",
            "American Porter":"Porter",
            "Baltic Porter":"Porter",
            "English Porter":"Porter",
            "Robust Porter ":"Porter",
            "Smoke Porter":"Porter",
            "Chile Beer":"Specialty Beer",
            "Finnish Sahti":"Specialty Beer",
            "Fruit and Field Beer":"Specialty Beer",
            "Herb and Spice Beer":"Specialty Beer",
            "Japanese Happoshu":"Specialty Beer",
            "Japanese Rice Lager":"Specialty Beer",
            "Low Alcohol Beer":"Specialty Beer",
            "Pumpkin Beer":"Specialty Beer",
            "Russian Kvass":"Specialty Beer",
            "Rye Beer":"Specialty Beer",
            "Scottish Gruit / Ancient Herbed Ale":"Specialty Beer",
            "Smoke Beer":"Specialty Beer",
            "American Imperial Stout":"Stout",
            "American Stout":"Stout",
            "English Oatmeal Stout":"Stout",
            "English Stout":"Stout",
            "English Sweet / Milk Stout":"Stout",
            "Foreign / Export Stout":"Stout",
            "Irish Dry Stout":"Stout",
            "Russian Imperial Stout":"Stout",
            "American Barleywine":"Strong Ale",
            "American Imperial Red Ale":"Strong Ale",
            "American Strong Ale":"Strong Ale",
            "American Wheatwine Ale":"Strong Ale",
            "Belgian Quadrupel (Quad)":"Strong Ale",
            "Belgian Strong Dark Ale":"Strong Ale",
            "Belgian Strong Pale Ale":"Strong Ale",
            "Belgian Tripel":"Strong Ale",
            "English Barleywine":"Strong Ale",
            "English Old Ale":"Strong Ale",
            "English Strong Ale":"Strong Ale",
            "Scotch Ale / Wee Heavy":"Strong Ale",
            "American Dark Wheat Ale":"Wheat Beer",
            "American Pale Wheat Ale":"Wheat Beer",
            "Belgian Witbier":"Wheat Beer",
            "Berliner Weisse":"Wheat Beer",
            "German Dunkelweizen":"Wheat Beer",
            "German Hefeweizen":"Wheat Beer",
            "German Kristalweizen":"Wheat Beer",
            "American Brett":"Wild/Sour Beer",
            "American Wild Ale":"Wild/Sour Beer",
            "Belgian Faro":"Wild/Sour Beer",
            "Belgian Fruit Lambic":"Wild/Sour Beer",
            "Belgian Gueuze":"Wild/Sour Beer",
            "Belgian Lambic":"Wild/Sour Beer",
            "Flanders Oud Bruin":"Wild/Sour Beer",
            "Flanders Red Ale":"Wild/Sour Beer",
            "Leipzig Gose":"Wild/Sour Beer",
            "Wild/Sour Beers":"Wild/Sour Beer"}
vals = [t for t in set([el for el in styledict.values()])]

def get_info(cur):
    cur.execute("""SELECT count(*) AS ct
        , min(beerid)  AS min_id
        , max(beerid)  AS max_id
        , max(beerid) - min(beerid) AS id_span
        FROM beers;""")
    print(cur.fetchone())

def grab_rand_data(cur, ds):
    data = [None]*ds
    style = [None]*ds
    try:
        cur.execute("""SELECT descs,style
        FROM  (
        SELECT DISTINCT 39000 + trunc(random() * 239000)::integer AS beerid
        FROM   generate_series(1, %s) g
        ) r
        JOIN beers USING (beerid)
        LIMIT %s;""",(ds*5,ds*3))
    except Exception as e:
        print(e)
    else:
        # f = open("beerdata",'w')
        i = 0
        for d in cur.fetchall():
            if i >= ds:
                break
            if not d[0]:
                continue
            nd = norm_list(d[0])
            if nd:
                data[i] = nd
                style[i] = d[1]
                i+=1
        return (data,style)
        # f.close()

def norm_list(l):
    s = sqrt(sum([n*n for n in l]))
    return [item/s for item in l] if s!= 0 else False

def test_clf(clf1,clf2,data,labels):
    cor = 0
    count = 0
    guess1 = better_predict(clf1,clf2,data)
    for i in range(len(labels)):
        if guess1[i] == labels[i]:
            cor+=1
        count+=1
    return cor/count
def better_predict(clf1,clf2,data):
    prob1 = clf1.predict_proba(data)
    prob2 = clf2.predict_proba(data)
    pre1 = clf1.predict(data)
    pre2 = clf2.predict(data)
    result = [None]*len(data)
    for i in range(len(prob1)):
        if max(prob1[i])>max(prob2[i]):
            result[i] = pre1[i]
        else:
            result[i] = pre2[i]
    return result

if __name__ == "__main__":

    conn = establish_connection()
    cur = create_cursor(conn)
    data,style = grab_rand_data(cur,length)
    svd = TruncatedSVD(n_components=dim, n_iter=7, random_state=42)
    print(len(data))
    # print(vals)
    # print(len(data[999]))
    data = check_array(data,accept_sparse = True)
    # print("d1: ",data[0])
    svd.fit(data)
    d = svd.fit_transform(data)
    # print("d1: ",data[0])
    #DummyClassifier(strategy='most_frequent').fit(d,[styledict[s] for s in style])
    # classifier1 = MLPClassifier(random_state=1,max_iter=1000).fit(d,[styledict[s] for s in style])
    classifier = GradientBoostingClassifier(n_estimators=100,init=MLPClassifier(max_iter=1000)).fit(d,[styledict[s] for s in style])
    if type(classifier)==type(GaussianNB()):
        classifier.partial_fit(d,[styledict[s] for s in style],classes=vals)
        for i in range(3):
            data,style = grab_rand_data(cur,length)
            data = svd.fit_transform(data)
            classifier.partial_fit(data,[styledict[s] for s in style])
    elif type(classifier)==type(MLPClassifier()):
        pass

    test_size = 50000
    # print(cur.fetchone())
    data,style = grab_rand_data(cur,test_size)
    print(classifier.score(svd.fit_transform(data),[styledict[s] for s in style]))
    # print(classifier1.score(svd.fit_transform(data),[styledict[s] for s in style]))
    # print(test_clf(classifier,classifier1,svd.fit_transform(data),[styledict[s] for s in style]))
    # print(test_clf(classifier,svd.fit_transform(data[0:test_size]),[styledict[s] for s in style[0:test_size]]))
    # print(classifier.predict(d[456:467]))
    # print([styledict[s] for s in style[456:467]])
    print(svd.explained_variance_ratio_)
    # print(svd.components_)
    print(svd.singular_values_)
    print(svd.explained_variance_ratio_.sum())
    f = open("beerdata.csv",'w')
    i = 0
    for dp in d:
        line = ""
        for i in range(dim):
            line+=str(dp[i])+','
        line = line[:-1]+'\n'
        f.write(line)
    for s in style:
        f.write(styledict[s]+'\n')
    for c in svd.components_:
        for n in c:
            f.write(str(n)+',')
        f.write('\n')
    f.close()
    # print(data[1],data[700])
    close_connection(conn,cur)
