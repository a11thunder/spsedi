import csv
import os

def ReadCSV(filename):
	csvfile = open(filename, 'rb')
	csvbuffer = csv.reader(csvfile)
	datalist = []
	for line in csvbuffer:
		datalist.append(line)
	csvfile.close()
	headerlist = datalist[0]
	datalist.pop(0)
	return headerlist, datalist

# If Wave invoice file exists, match with order list.
Invoiced = False
if os.path.isfile('invoice_items.csv'):
	Invoiced = True

# Stores lookup
StoreLookup = False
if os.path.isfile('stores.csv'):
	StoreLookup = True
	storehdrlist, storelist = ReadCSV('stores.csv')
	colStoreLUID = storehdrlist.index('Store No.')
	colStoreLUCity = storehdrlist.index('City')
	colStoreLUState = storehdrlist.index('State')

# Process SPS PO export file
headerlist, datalist = ReadCSV('documentDownloads-2016-10-27_17-38.csv')
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
		storeID.append(int(line[colStoreID].strip()))
		storeCity.append(line[colStoreCity])
		storeState.append(line[colStoreState])
		itemcount.append(0)
	elif 'D' in line[colRecordType]:
		itemcount[-1] = itemcount[-1] + 1
		if line[colUPC] not in productlist:
			productlist.append(line[colUPC])
			productname.append(line[colProductName])
			pricelist.append(float(line[colUnitPrice]))

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

ordertotal = len(orderlist) * [0.0]
itemtally = len(productlist) * [0]
for iorder in range(len(orderlist)):
	tempsum = 0.0
	for iprod in range(len(productlist)):	
		tempsum = tempsum + itemizedqty[iorder][iprod] * pricelist[iprod]
		itemtally[iprod] = itemtally[iprod] + itemizedqty[iorder][iprod]
	ordertotal[iorder] = tempsum

print '\n'+' === Products Ordered ===\n'	
for iprod in range(len(productlist)):
	print '   ' + productname[iprod] + ': ' + str(itemtally[iprod])

print
print ' Total Orders: ' + str(len(orderlist))
print

if Invoiced:
	headerlist, invoicelist = ReadCSV('invoice_items.csv')
	colInvoiceNum = headerlist.index('invoice_num')
	colInvoicePO = headerlist.index('po_so')
	colInvoiceDate = headerlist.index('invoice_date')
	colInvoiceDue = headerlist.index('due_date')
	csvfile = open('invoiced.csv','wb')
	csvwrite = csv.writer(csvfile)
	csvbuffer = []
	csvbuffer.append('Invoice Date')
	csvbuffer.append('Due Date')
	csvbuffer.append('PO Number')
	csvbuffer.append('Invoice Number')
	csvbuffer.append('Amount')
	listprocessed = []
	csvwrite.writerow(csvbuffer)
	for line in invoicelist:
		if line[colInvoicePO] in orderlist and line[colInvoicePO] not in listprocessed:
			listprocessed.append(line[colInvoicePO].strip())
			orderindex = orderlist.index(line[colInvoicePO].strip())
			csvbuffer = []
			csvbuffer.append(line[colInvoiceDate])
			csvbuffer.append(line[colInvoiceDue])
			csvbuffer.append(orderlist[orderindex])
			csvbuffer.append(line[colInvoiceNum])
			csvbuffer.append("%.2f" % round(ordertotal[orderindex],2))
			csvwrite.writerow(csvbuffer)
	csvfile.close()
	print ' Total Order Invoiced: ' + str(len(listprocessed))
	print

csvfile = open('orders.csv','wb')
csvwrite = csv.writer(csvfile)
csvbuffer = []
if Invoiced:
	csvbuffer.append('Status')
csvbuffer.append('PO Number')
for product in productname:
	csvbuffer.append(product)
csvbuffer.append('Total')
csvbuffer.append('Store ID')
csvbuffer.append('City')
csvbuffer.append('State')
csvwrite.writerow(csvbuffer)
for iorder in range(len(orderlist)):
	csvbuffer = []
	if Invoiced:
		if orderlist[iorder] in listprocessed:
			csvbuffer.append('Invoiced')
		else:
			csvbuffer.append('---')
	csvbuffer.append(orderlist[iorder])
	for iprod in range(len(productlist)):
		csvbuffer.append(str(itemizedqty[iorder][iprod]))
	csvbuffer.append("%.2f" % round(ordertotal[iorder],2))
	csvbuffer.append(str(storeID[iorder]))
	if StoreLookup:
		for astore in storelist:
			if storeID[iorder] == int(astore[colStoreLUID]):
				csvbuffer.append(astore[colStoreLUCity])
				csvbuffer.append(astore[colStoreLUState])
	else:
		csvbuffer.append(storeCity[iorder])
		csvbuffer.append(storeState[iorder])
	csvwrite.writerow(csvbuffer)
csvfile.close() 
