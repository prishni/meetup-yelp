import pickle
final = pickle.load(open('final1.txt','r'))

def ExtractVID_meetup(event_id,g_id):
    try:
        dic = final[g_id][3]
        return dic[event_id][2]
    except:
        return -1
f = open("venuId.txt",'w')

for group_id in final:
    print group_id
    event_dictionary = final[group_id][3]
    for key in event_dictionary:
        #print "#####  " +str(key
        f.write (str(key)+','+str(group_id)+','+str(ExtractVID_meetup(key,group_id))+'\n')
        
f.close()
    
#12527964,153288 ----- 1182815
