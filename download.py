import json
import logging
import os
from pathlib import Path
from urllib.request import urlopen, Request
import requests
from html.parser import HTMLParser
import re
from pprint import pprint

descs = ['accessible','acidic','aggressive','alcoholic','almondlike/almond/almondy','apple/applelike','artificial','assertive','astringent','backbone','bacony/bacon','balance/balanced','bananalike/banana','barnyard',
'big','biscuity/biscuit','bitter/bitterness','body/bodied','bold','boozy/booze','bourbonlike/bourbon/bourbony','bready/bread','Brettanomyces/brett/bretty','bright','bubblegum/bubblegummy','burnt','buttery/butter','caramely/caramel',
'catty','chalky/chalk','cheesy/cheese','chewy','Chlorophenolic','chocolaty/chocolate/chocolatey','cigarlike/cigar','citrusy/citrus','clean','clovelike/clove/clovey','cloying','coconut/coconutty','coffeelike/coffee','colorful',
'complex','corked/cork/corky','cornlike/corn','crackerlike/cracker/crackery','creamy/cream','crisp/crispy','dark','deep','delicate','Diacetyl','dirty/dirt','dissipate','doughy/dough','fruity/fruit','dry',
'earthy/earth','estery/ester','farmlike/farm/farmy','fine','firm','flat','flowery/flower','fluffy/fluff','foamy/foam','fresh','gassy/gas','Geraniol','grainy/grain','grapefruity/grapefruit',
'grassy/grass','greasy/grease','green','harmonious','harsh','hazy/haze','head','hearty','heavy','herbal','highlights','hollow','honeylike/honey','hoppy/hops','horselike/horse/horsey','hot','husky',
'inky/ink','intense','jammy/jam','Lactobacillus','leathery/leather','legs/leggy','lemony/lemon','light','lightstruck','linalool','medicinal/medicine','mellow','melonlike/melon/melony','Mercaptan','metallic/metal','mild',
'milky/milk','minerally/mineral','molasses','moldy/mold','moussy','musty','nutty/nuts','oaky/oak','oatmeal','oat/oaty','oily/oil','Chlorophenol','oxidation','oxidized','papery/paper',
'peaty/peat','peppery/pepper','perfumy/perfume','persistent','phenolic','powerful','rancid','refined','refreshing','resinous/resin/resiny','rich','roasted/roast/roasty','robust','rocky','saccharine','salty/salt/salted',
'sediment/sedimenty','sharp','sherrylike/sherry','silky/silk','skunky/skunked/skunk','smoky/smoke/smoked','smooth','soapy/soap','soft','solventlike/solvent/solventy','sour/soured','spicy/spice/spiced','stale/staled','sticky','sulfidic/sulfide/sulfitic','sweet','syrupy/syrup','tannic/tannins/tannin','tart','texture/textured','thick','thin','toasty/toast/toasted','toffee','nonenal','treacle','turbid','vanilla','vegetal','viscous',
'warming','watery/water','winelike/winey/wine','woody/wood','worty/wort','yeasty/yeast','young','zesty/zest']

ld = len(descs)

class BeerHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.counter = 0
        self.btag = False
        self.tottag = False
        self.links = []
        self.num = 20000
        self.p = re.compile(r'(of) (\d+)')
        self.exit = False
        self.rcount = -500

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.rcount+=1
            for attr in attrs:
                if attr[0] == 'colspan' and not attr[1]=='2':
                    return
                if attr[0] == 'align' and not attr[1]=='left':
                    return
            self.counter+=1
            self.btag = True
            self.rcount = 0
        elif self.btag and tag == 'a':
            self.links.append(attrs[0][1])
        elif tag == 'span':
            for attr in attrs:
                if attr[0] == 'style':

                    if str(attr[1][0:5]) == 'color':
                        self.tottag = True


    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        return None

    def handle_data(self, data):
        if self.btag:
            #print("Encountered some data  :", data)
            self.btag = False
        elif self.tottag:
            # print(data)
            #
            # print(self.p.search(data).group(2))
            self.tottag = False
            self.num = int(self.p.search(data).group(2))
        elif self.rcount == 2:
            if data == '-':
                self.exit = True
        return None

#Need to update this to grab the brewery info at the top of the page
#and save it to a json object. Need to grab brewery name, address, (know state),
#avg beer rating. Then, the thread will need to insert this info into the
#database, snag the brewery id, and then insert all the beer info with the
#corresponding brewery id.
class BrewPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.avg = False
        self.avgc = 0
        self.intable = False
        self.keys = ['name','style','abv','ratings','avg','link']
        self.packet = {'name': None,'style': None,'abv': None,'ratings':None,'avg': None,'link':None}
        self.bavg = ""
        self.data = []
        self.datacount = 0
        self.f = True
        self.name = ""
        self.nameflag = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'tbody':
            # logger.info(attrs)
            self.intable = True
            # for attr in attrs:
            #     if attr == ('aria-live','polite'):
        elif tag == 'a' and self.intable:
            # logger.info(attrs)
            if self.f:
                self.packet['link'] = attrs[0][1]
                self.f =False
            else:
                self.f = True
        elif tag == 'dd':
            self.avg = True
        elif tag == 'div':
            for attr in attrs:
                if attr == ('class','titleBar'):
                    self.nameflag = 1
        elif tag == 'h1' and self.nameflag == 1:
            self.nameflag = 2
        return None


    def handle_endtag(self, tag):
        if tag == 'tbody' and self.intable:
            # logger.info(tag)
            self.intable = False
        elif tag == 'tr' and self.intable and self.datacount!=0:
            self.datacount = 0
            self.data.append(self.packet.copy())
        elif tag == 'dd':
            self.avg = False
        elif tag == 'div' and self.nameflag == 1:
            self.nameflag = 0
        elif tag == 'h1' and self.nameflag == 2:
            self.nameflag = 1
        return None

    def handle_data(self, data):
        if self.intable and self.datacount < 5:
            # logger.info(data)
            if self.datacount == 3:
                data = data.replace(",","")
            self.packet[self.keys[self.datacount]] = data
            self.datacount += 1
        if self.avg:
            self.avgc+=1
            # logger.info(data)
            if self.avgc == 8:
                self.bavg = data
        if self.nameflag == 2:
            # logger.info("bname: %s",data)
            self.name = data
        return None

class ReviewPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.uc = False
        self.rf = False
        self.c = 0
        self.dc = 0
        self.rev = ""
        self.revs = []
        self.exit = False

    def handle_starttag(self, tag, attrs):
        if tag == 'html':
            self.uc = False
            self.rf = False
            self.c = 0
            self.dc = 0
            self.rev = ""
            self.exit = False
        if tag == 'div':
            for attr in attrs:
                if attr == ('class','user-comment'):
                    self.dc+=1
                    # self.uc = True
                    self.c = 0
                    self.revs.append(self.rev)
                    self.rev = ""
        if tag == 'br' and self.c<3:
            self.c+=1
        # if tag == 'i' and self.rf:
        #     self.rf = False
        if tag != 'br' and self.c == 3:
            self.c = 4
        return None


    def handle_endtag(self, tag):
        # if tag == 'div' and self.uc and self.c == 2:
        #     self.uc = False
        #     self.c = 0
        # if tag == 'div' and self.uc:
        #     self.c+=1
        if tag == 'html':
            if self.dc == 0:
                self.exit = True
            self.revs.append(self.rev)

        return None

    def handle_data(self, data):
        if self.c==3:
            # logger.info("Review: %s",data)
            self.rev+= (data if data!='\n' else "")
            # logger.info("Review: %s",self.rev)
        return None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# types = {'image/jpeg', 'image/png'}

###HELPER FUNCTIONS
def p_to_f(content):
    f = open("test.html","a")
    f.write(content)
    f.close()


def login(session):
    url = 'https://www.beeradvocate.com/community/login/login'
    login_data = {'login':'deweyd123', 'password':'12ddewey3'}
    r = session.post(url, data=login_data)

def get_reviews(link, session):
    url = 'https://www.beeradvocate.com'+link
    counter = 0
    parser = ReviewPageParser()
    while not parser.exit:
        url2 = url+'?view=beer&sort=&start='+str(counter)
        r = session.get(url2)
        parser.feed(r.text)
        # logger.info(parser.dc)
        counter+=25
    return(parser.revs)

def get_links(state, session):
    #headers = {'Authorization': 'Client-ID {}'.format(client_id)}
    links = []
    counter = 0

    parser = BeerHTMLParser()
    while(parser.counter <= parser.num and not parser.exit):
        brewurl = 'https://www.beeradvocate.com/place/list/?start='+str(counter)+'&c_id=US&s_id=' + state + '&brewery=Y&sort=ratings'
        r2 = session.get(brewurl)
        parser.feed(r2.text)

        counter+=20

    return parser.links

def download_link(link, session):
    parser = BrewPageParser()
    url = "https://www.beeradvocate.com" + link

    r = session.get(url)

    parser.feed(r.text)
    # if len(parser.data)>0:
    #     # pprint(link)
    #     # pprint(parser.data[0])
    # else:
    #     'check here'
    # if len(parser.data)>0:
        # logger.info('Object: %s',str(parser.name))
    # else:
        # logger.info('no beer here: %s',url)
    # logger.info('Downloaded %s', url)
    return ({'name': parser.name, 'beerrating': float(parser.bavg), 'link':url},parser.data)

def setup_download_dir():
    download_dir = Path('images')
    if not download_dir.exists():
        download_dir.mkdir()
    return download_dir
