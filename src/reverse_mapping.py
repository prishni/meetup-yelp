import pickle
import csv
final = pickle.load(open('final1.txt','r'))

reversed_dict = {}
f= open("reversedDict.txt",'w')

for group_id in final:
    event_dictionary = final[group_id][3]
    for event in event_dictionary:
        #print "#####  " +str(key)
        venue = event_dictionary[event][2]
        #print event
        #print venue
        #print '--------------'
        if venue is None:
            #print 'detected\n'
            continue
        if reversed_dict.has_key(venue):
            #print '#####################################'
            abc=reversed_dict[(venue)]
            abc.append(event)
            reversed_dict[(venue)] = abc
        else:
            reversed_dict[(venue)] = [event]
    
   
#print reversed_dict
for each in reversed_dict:
    f.write(str(each)+',' + str(reversed_dict[each])+'\n')
f.close()

##with open ('reversed_Dict.txt',mode = 'r') as infile:
##    reader = csv.reader(infile)
##    
##    reversed_dict = {rows[0]:rows[1] for rows in reader}

listVenue = []
listEvent =[]
##if reversed_dict.has_key(1043835):
##    print reversed_dict[1043835]
    #print str(reversed_dict.get(1043835,None))
#print reversed_dict['1043835']
f = open('meetup_ids.txt','r')
for line in f:
    line=int(line.strip())
    listVenue.append(line)
f.close()
f = open('valuableVenueEvent.txt','w')
f1 = open('valuableEvent.txt','w')
for each in listVenue:
    #try:
    item = reversed_dict[int(each)]
    print item
    #except:
    #   continue
    for ite in item:
        #listEvent.append(ite)
        f.write(str(each)+','+str(ite)+'\n')
        f1.write(str(ite)+'\n')
f.close()
