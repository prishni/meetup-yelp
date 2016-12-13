import pickle
from scipy import spatial
import numpy as np
import venue_map_category
import paragraph_vec
# g_id - 1187853
#event_id = 12812863
##event_id = '12527964'
##g_id = 153288
#event_id = '12441000'
#g_id = 1461767
event_id = '15561401'
g_id = 209983
SuperListEvent =[]
f = open('valuableEvent.txt','r')
for each in f:
    SuperListEvent.append(str(each.strip()))
    
f.close()

final = pickle.load(open('final1.txt','r'))
event_description = open('eventVec.txt','r')

c=0
successful_events=[]
unsuccessful_events=[]
similarityList =[]
similar_events =[]
similar_group = []
similar_event_venu_meet =[]
similar_event_venu_yelp =[]
def ExtractVID_meetup(event_id):
    for grp in similar_group:
        try:
            dic = final[grp][3]
            if dic.has_key(event_id):
                return dic[event_id][2]
        except:
            return -1

for group_id in final:
    if final[group_id][0] == final[g_id][0]:  #comparing categories
        similar_group.append(group_id)
print similar_group

for each_group in similar_group:
    event_dictionary = final[each_group][3]
    for event in event_dictionary:
        if str(event) not in SuperListEvent:
            continue
        try:
            value=float(event_dictionary[event][1])/float(event_dictionary[event][0])
        except:
            continue
            
        if value>.7:
            successful_events.append(event)
        else:
            unsuccessful_events.append(event)
print successful_events


var = 0
for line in event_description:
    c = c+1
    if c%2 == 1:
        if str(line.strip()) not in SuperListEvent:
            continue
        #print line.strip()
        if str(line.strip()).strip() == str(event_id).strip():
            var = 1
            continue
    if var ==1:
        break
if var == 1:
    event_vec_str = line.strip()
    var =0
            

event_vec1 = event_vec_str.split(',')
event_vec1.pop()

#print event_vec1
print '################################################################'
event_description.seek(0,0)

for eventId in successful_events:
    var = 0
    if eventId == event_id:
        continue
    for line in event_description:
        c = c+1
        if c%2 == 1:
            #print line.strip()
            if str(line.strip()).strip() == str(eventId).strip():
                var = 1
                continue
        if var ==1:
            break
    if var == 1:
        event_vec_str = line.strip()
        var =0

        event_vec = event_vec_str.split(',')
        event_vec.pop()
        
        event_vec1 = np.array(event_vec1,dtype = float)
        event_vec = np.array(event_vec,dtype = float)
        result = 1 - spatial.distance.cosine(event_vec1, event_vec)
        similarityList.append(result)
        print("value is", result)
        #print event_vec
    event_description.seek(0,0)
    
event_description.seek(0,0)



index=-1
threshold = 0.6  #for finding similar events
for sim in similarityList:
    index=index+1
    if sim > threshold:
        # gives all similar successful events
        similar_events.append(successful_events[index])

print '2222222222222222222222222222222222222222222222222222'
print similar_events       
print '2222222222222222222222222222222222222222222222222222'

for each in similar_events:
    venu = ExtractVID_meetup(each)
    if venu!= -1:
        similar_event_venu_meet.append(venu)
print similar_event_venu_meet
print '2222222222222222222222222222222222222222222222222222'

unique_similar_event_venue_meet=[]
for each in similar_event_venu_meet:
    if each not in unique_similar_event_venue_meet:
        unique_similar_event_venue_meet.append(each)
print unique_similar_event_venue_meet
print '111111111111111111111111111111111111111111111'

reviews_vec_list = []
for each in unique_similar_event_venu_meet:
    venu ,category,reviews = venue_map_category.main1(['Chicago',str(each), 'CH_venues_experimental.json', 'output_merged.json',  'review_dump_unique_sorted.json', 'apikeys.txt'])
    similar_event_venu_yelp.append(venu)
    reviews = ' '.join(reviews)
    reviews_vec= paragraph_vec.main1(reviews)
    reviews_vec_list.append(reviews_vec)
print similar_event_venu_yelp
    
###find meet up venue1 id for our event and yelp venue id
temp_dict = final[g_id][3]
venuID_meetUp_e1 = temp_dict[event_id][2]
print venuID_meetUp_e1 

venuID_yelp_e1,category,review = venue_map_category.main1(['Chicago',str(venuID_meetUp_e1), 'CH_venues_experimental.json', 'output_merged.json',  'review_dump_unique_sorted.json', 'apikeys.txt'])
review = ' '.join(review)
review_vec= paragraph_vec.main1(review)
print review_vec

print  '##################'
print venuID_yelp_e1
similarityVal_venue = []
#find similarity between venue1 and diff venues
for i in range(0,len(reviews_vec_list)):
    a = np.array(reviews_vec_list[i],dtype = float)
    result = 1 - spatial.distance.cosine(a,review_vec)
    similarityVal_venue.append(result)

print similarityVal_venue


#find similarity between venue1 and diff venues
#for each in similar_event_venu_yelp:
        
    

event_description.close()

