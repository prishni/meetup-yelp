import pickle
import paragraph_vec
import venue_map_category
import numpy as np
from scipy import spatial
#import para_vector
# g_id = 1187853     
#event_id = 12812863
#event_id = '12527964'
#g_id=153288
event_id = '15561401'
g_id = 209983
SuperListEvent =[]
f = open('valuableEvent.txt','r')
for each in f:
    SuperListEvent.append(str(each.strip()))
    
f.close()
#print SuperListEvent
#print type(SuperListEvent[0])
final = pickle.load(open('final1.txt','r'))
event_description = open('eventVec.txt','r')
c=0
for group_id in final:
    if group_id == g_id:
        event_dictionary = final[group_id][3]
        for key in event_dictionary:
            #print type(key)
            if str(key) not in SuperListEvent:
                continue
            if str(key) == event_id:
                meet_venueId = event_dictionary[key][2]
                print meet_venueId
                yelp_venueId,category,review = venue_map_category.main1(['Chicago',str(meet_venueId), 'CH_venues_experimental.json', 'output_merged.json',  'review_dump_unique_sorted.json', 'apikeys.txt'])
                print yelp_venueId
                break
##print review
##print category
review = ' '.join(review)
review_vec= paragraph_vec.main1(review)
print review_vec

var = 0
for line in event_description:
    c = c+1
    if c%2 == 1:
        '''if str(line.strip()) not in SuperListEvent:
            continue'''
        #print line.strip()
        if str(line.strip()).strip() == str(event_id).strip():
            var = 1
            continue
    if var ==1:
        break
if var == 1:
    event_vec_str = line.strip()
    var =0
            

event_vec = event_vec_str.split(',')
event_vec.pop()
print event_vec

a = np.array(review_vec,dtype = float)
b = np.array(event_vec,dtype = float)
result = 1 - spatial.distance.cosine(a,b)
print result

event_description.close()

#12527964,153288
            
            
