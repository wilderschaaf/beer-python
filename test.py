from download import descs,login,get_reviews
from descriptorgettor import get_blinks_from_bid,get_all_bids
import requests
from pprint import pprint

# rev = "an impressive example of the style here, very well made beer, seemingly of an even high quality than most of the rest of their lineup, just excellent stuff, on tap at the brewery yesterday at a considerably higher abv than what is listed here. i had the heaven hill barrel aged edition as well, and while that is certainly excellent beer, the beer needs no barrel to be great or complex. its frothy headed from the tap and near black in the glass, although less visually viscous than many. it smells a touch sweet, but with a lot of close to burnt dark roast behind it. i get notes of sweet corn and molasses, as well as dark drip coffee and toasted bread. i also think i get a hint of rye malt or something, much like in the barrel aged version, there is a little spice quality to this, earthy nuance, not sure its rye, but its unique in here to me. its very smooth and hides its strength better than the barrel aged one, good glide as they say, and a nice linger, slightly sweet, cocoa forward, and with a hint of raisin, prune, and smoke. i like this having a little english or scottish (or something) yeast character to it, and i like its level of refinement. great beer, i saw they had a cabernet barrel aged edition as well, i bet that is the best of the lot! dont miss this one when you are in!"
caldera =[1,3,9,1,1,2,2,5,7,66,0,210,1,1,89,47,493,286,8,6,0,60,0,43,0,16,14,241,1,4,4,11,0,1,2,388,40,0,6,0,0,2,22,0,2,10,104,57,48,36,4,2,7,0,8,125,94,85,3,0,33,8,1,6,36,92,77,1,0,28,274,63,0,14,1,4,76,493,5,30,38,5,0,35,658,0,10,1,0,8,0,0,3,1,46,185,0,0,2,14,5,0,21,43,1,2,0,0,0,7,4,2,0,0,26,0,0,2,0,0,24,3,4,0,2,0,1,28,81,28,10,5,15,0,2,8,20,0,4,3,5,71,16,10,0,2,50,0,85,0,198,11,0,9,12,71,46,68,20,0,0,0,1,4,1,4,15,4,11,2,9,0,19]
# counts = [0]*len(descs)
#
# # print(count_agg(counts, rev))
# s = requests.session()
# link = '/beer/profile/1075/130631/'
# login(s)
# # print(get_reviews(link,s))
# revs = get_reviews(link,s)
# # for rev in revs:
# #     count_agg(counts, rev)
# # print(counts)
# print(len(revs))
# for i in range(len(counts)):
#     if counts[i]>2:
#         print(descs[i])
#
# # print(len(get_blinks_from_state('AL')))
# print(get_all_bids()[0])
# print(get_blinks_from_bid(get_all_bids()[10])[0])
for i in range(len(caldera)):
    if caldera[i]>500:
        print(descs[i])
