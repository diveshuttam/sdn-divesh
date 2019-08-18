import sys

def main(argv):
	pollingFreq = 10
	partitionTime = 20
	lastPolled = 0
	totalPolls = 0
	diff = 37

	actualTraffic = []

	for line in open('traffic.txt', 'r').readlines():
		actualTraffic.append(int(line.split()[2]))

	sampledData = [None] * len(actualTraffic)

	totalPartitions = len(actualTraffic) // partitionTime
	print("Total partitions :", totalPartitions)

	for i in range(0, totalPartitions):
		if pollingFreq > partitionTime:
			pollingFreq = partitionTime

		if pollingFreq == 0:
			pollingFreq = 2

		start = partitionTime * i
		end = partitionTime * (i + 1) - 1
		sampledData[start] = actualTraffic[start]
		sampledData[end] = actualTraffic[end]

		poll = lambda m, n: [i*n//m + n//(2*m) + start for i in range(m)]
		poll = poll(pollingFreq, partitionTime)
		for j in poll:
			sampledData[j] = actualTraffic[j]
		totalPolls += len(poll)

		nonMissingValues = [x for x in range(start, end + 1) if sampledData[x] != None]

		for j in range(0, len(nonMissingValues) - 1):
			startData = sampledData[nonMissingValues[j]]
			endData = sampledData[nonMissingValues[j + 1]]

			for k in range(nonMissingValues[j], nonMissingValues[j + 1]):
				if sampledData[k] == None:
					sampledData[k] = (endData - startData) / (nonMissingValues[j + 1] - nonMissingValues[j]) * (k - nonMissingValues[j]) + startData

		newPollingFreq = 0
		for j in range(start, end + 1):
			if j > 0:
				percentageDiff = abs(sampledData[j] - sampledData[j - 1]) / sampledData[j] * 100
				if percentageDiff > diff:
					newPollingFreq += 1

		#Nyquist theorem
		newPollingFreq *= 2
		pollingFreq = newPollingFreq

	print(actualTraffic)
	print(sampledData)
	print(totalPolls)

	errorList = []

	for i in range(0, len(sampledData)):
		if (sampledData[i] != None):
			diff = abs(actualTraffic[i] - sampledData[i]) / actualTraffic[i] * 100
			errorList.append(diff)

	print("error% = ", sum(errorList)/len(errorList))

if __name__ == "__main__":
	main(sys.argv)
