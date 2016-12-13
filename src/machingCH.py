#list1 = [972344,1081272]
f=open('venueID.txt','r')
venueID = []
for line in f:
    line=line.strip()
    venueID.append(line)

f.close()
uniqueVenues = []
for item in venueID:
    if item not in uniqueVenues:
        uniqueVenues.append(item)
