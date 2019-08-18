from datetime import datetime

file = open('sampletimes.txt')
secs = 20
curr_time = datetime.now().replace(microsecond=0)
useful_samples = []

for i in file:
        #print (i)
        dt = datetime.strptime(i.strip(), '%Y-%m-%d %H:%M:%S')
        seconds_delta = (curr_time - dt).seconds
	#print (str(curr_time) + '-' + str(dt) + '=' + str(seconds_delta))
        if seconds_delta <= secs:
                #print (seconds_delta)
                useful_samples.append(i)


print ("curr_time:")
print (str(curr_time))
print ("usefulsamples:")
print (useful_samples)
#for j in useful_samples:
#        print (j)
print ("no of samples in " +str(secs)+ " seconds = " + str(len(useful_samples)))
print ("sampling freq:")
samplingfreq = 0

if (len(useful_samples)==0):
        samplingfreq = 1
else:
        samplingfreq = secs/len(useful_samples)
print (samplingfreq)


#new
print('new code')
bucketfile = open('bucket.txt')
bucket_recs = []
for i in bucketfile:
        #print (i)
        list = i.split(',')
        timestamp = list[0]
        dt = datetime.strptime(timestamp.strip(), '%Y-%m-%d %H:%M:%S')
        seconds_delta = (curr_time - dt).seconds
        if seconds_delta <= secs:
                print (seconds_delta)
                bucket_recs.append(i)

samples_acc_to_samplingfreq = []
print('bucket data.. \n')
for i in range(len(bucket_recs)):
        samples_acc_to_samplingfreq.append(bucket_recs[i])
        i += samplingfreq
bucketfile.close()
print('printing samples..\n')
print(samples_acc_to_samplingfreq)


