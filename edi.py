import csv


# Process SPS PO export file
csvfile = open('documentDownloads-2016-10-27_17-38.csv', 'rb')
csvbuffer = csv.reader(csvfile)
datalist = []
for line in csvbuffer:
	datalist.append(line) 
csvfile.close()

headerlist = datalist[0]
datalist.pop(0)
colRecordType = headerlist.index('Record Type')
colPONum = headerlist.index('PO Number')
colUPC = headerlist.index('UPC/EAN')
colStoreID = headerlist.index('Ship To Location')
colStoreCity = headerlist.index('Ship To City')
colStoreState = headerlist.index('Ship To State')
colUnitPrice = headerlist.index('Unit Price')
colQty = headerlist.index('Qty Ordered')
colProductName = headerlist.index('Vendor Style')

orderlist = []
productlist = []
productname = []
pricelist = []
itemcount = []
storeID = []
storeCity = []
storeState = []
for line in datalist:
	if 'H' in line[colRecordType]:
		orderlist.append(line[colPONum])
		storeID.append(line[colStoreID])
		storeCity.append(line[colStoreCity])
		storeState.append(line[colStoreState])
		itemcount.append(0)
	elif 'D' in line[colRecordType]:
		itemcount[-1] = itemcount[-1] + 1
		if line[colUPC] not in productlist:
			productlist.append(line[colUPC])
			productname.append(line[colProductName])
			pricelist.append(line[colUnitPrice])

# Initialize item quantity count 2D table
itemizedqty = [len(productlist)*[0] for i in range(len(orderlist))]

# Count quantities for each product per order
for line in datalist:
	if 'H' in line[colRecordType]:
		iorder = orderlist.index(line[colPONum])
		continue
	elif 'D' in line[colRecordType]:
		for i in range(len(productlist)):
			if line[colUPC] == productlist[i]:
				itemizedqty[iorder][i] = int(line[colQty].strip())

itemtally = len(productlist) * [0]
for iprod in range(len(productlist)):
	for iorder in range(len(orderlist)):
		itemtally[iprod] = itemtally[iprod] + itemizedqty[iorder][iprod]

print '\n'+' === Products Ordered ===\n'	
for iprod in range(len(productlist)):
	print '   ' + productname[iprod] + ': ' + str(itemtally[iprod])

print
print ' Total Orders: ' + str(len(orderlist))
print


csvfile = open('order.csv','wb')
csvwrite = csv.writer(csvfile)
csvbuffer = []
csvbuffer.append('PO Number')
for product in productname:
	csvbuffer.append(product)
csvbuffer.append('Store ID')
csvbuffer.append('City')
csvbuffer.append('State')
csvwrite.writerow(csvbuffer)
for iorder in range(len(orderlist)):
	csvbuffer = []
	csvbuffer.append(orderlist[iorder])
	for iprod in range(len(productlist)):
		csvbuffer.append(str(itemizedqty[iorder][iprod]))
	csvbuffer.append(storeID[iorder])
	csvbuffer.append(storeCity[iorder])
	csvbuffer.append(storeState[iorder])
	csvwrite.writerow(csvbuffer)

csvfile.close()



