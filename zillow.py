# A script to query price info from zillow
# Author : Rajeev Thottathil

from xml.dom.minidom import parse,parseString
import xml.dom.minidom
import requests
import sys

l_zwsid='YourZillowWebServicesIdHere' 

def getElementValue(p_dom,p_element):
    if len(p_dom.getElementsByTagName(p_element)) > 0:
       l_value=p_dom.getElementsByTagName(p_element)[0]
       return(l_value.firstChild.data)
    else:
       l_value='NaN'
       return(l_value)

def printSummary():
        print('{0:<20s} :  {1:<20s}'.format('Zpid',zpid))
        print('{0:<20s} :  {1:<20s}'.format('Type',usecode))
        print('{0:<20s} :  {1:<20s}'.format('Street',street))
        print('{0:<20s} :  {1:<20s}'.format('ZipCode',zipcode))
        print('{0:<20s} :  {1:<20s}'.format('YearBuilt',yearbuilt))
        print('{0:<20s} :  {1:<20s}'.format('Finished SqFt',sqft))
        print('{0:<20s} :  {1:<20s}'.format('Bedrooms',bedrooms))
        print('{0:<20s} :  {1:<20s}'.format('Bathrooms',bathrooms))
        print('{0:<20s} :  {1:<20s}'.format('Total Rooms',totrooms))
        print('{0:<20s} :  {1:<20s}'.format('Tax Year',taxyear))
        print('{0:<20s} :  {1:<20s}'.format('Tax Assessed',tax))
        print('{0:<20s} :  {1:<20s}'.format('Zestimate',amt))
        print('{0:<20s} :  {1:<20s}'.format('Zestimate Low',low))
        print('{0:<20s} :  {1:<20s}'.format('Zestimate High',high))
        print('{0:<20s} :  {1:<20s}'.format('Last Sold Date',lastSale))
        print('{0:<20s} :  {1:<20s}'.format('Last Sale Price',lastPrice))

if len(sys.argv) >= 3:
   a_addr=sys.argv[1]
   a_zip=sys.argv[2]
else:
   print('Syntax : zillow2.py','address','zipcode')
   exit(1)

l_url='http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id='+l_zwsid+'&address='+a_addr+'&citystatezip='+a_zip
xml=requests.get(l_url)
dom=parseString(xml.text)

responses=dom.getElementsByTagName('response')

zpid=getElementValue(dom,'zpid')
usecode=getElementValue(dom,'useCode')
taxyear=getElementValue(dom,'taxAssessmentYear')
tax=getElementValue(dom,'taxAssessment')
yearbuilt=getElementValue(dom,'yearBuilt')
sqft=getElementValue(dom,'finishedSqFt')
lotsize=getElementValue(dom,'lotSizeSqFt')
bathrooms=getElementValue(dom,'bathrooms')
bedrooms=getElementValue(dom,'bedrooms')
totrooms=getElementValue(dom,'totalRooms')
lastSale=getElementValue(dom,'lastSoldDate')
lastPrice=getElementValue(dom,'lastSoldPrice')

for response in responses:
    addresses=response.getElementsByTagName('address')
    for addr in addresses:
        street=getElementValue(addr,'street')
        zipcode=getElementValue(addr,'zipcode')

    zestimates=response.getElementsByTagName('zestimate')
    for zest in zestimates:
        amt=getElementValue(zest,'amount')
        lastupdate=getElementValue(zest,'last-updated')
        valranges=zest.getElementsByTagName('valuationRange')
        for val in valranges:
            low=getElementValue(val,'low')
            high=getElementValue(val,'high')

printSummary()

l_url2='http://www.zillow.com/webservice/GetDeepComps.htm?zws-id='+l_zwsid+'&zpid='+zpid+'&count=10'
xml2=requests.get(l_url2)
dom2=parseString(xml2.text)

print ("{dashes}".format(dashes='-'*160))
print('{0:<10s} {1:<20s} {2:<15s} {3:<5s} {4:<5s} {5:<10s} {6:<10s} {7:<10s} {8:<5s} {9:<10s} {10:<10s} {11:<10s} {12:<10s} {13:<10s}'.format('Zpid','Street','City','Zip','Built','Sqft','LotSize','Baths','Beds','LstSale','LstPrice','PerSqft','TaxYear','TaxAmt'))
print ("{dashes}".format(dashes='-'*160))

comparables=dom2.getElementsByTagName('comp')
for comparable in comparables:

    zpid=getElementValue(comparable,'zpid')
    yearbuilt=getElementValue(comparable,'yearBuilt')
    sqft=getElementValue(comparable,'finishedSqFt')
    lotsize=getElementValue(comparable,'lotSizeSqFt')
    bathrooms=getElementValue(comparable,'bathrooms')
    bedrooms=getElementValue(comparable,'bedrooms')
    taxyear=getElementValue(comparable,'taxAssessmentYear')
    tax=getElementValue(comparable,'taxAssessment')
    lastSale=getElementValue(comparable,'lastSoldDate')
    lastPrice=getElementValue(comparable,'lastSoldPrice')

    addresses=comparable.getElementsByTagName('address')

    for addr in addresses:
        street=getElementValue(addr,'street')
        city=getElementValue(addr,'city')
        zipcode=getElementValue(addr,'zipcode')

    print('{0:<10s} {1:<20s} {2:<15s} {3:<5s} {4:<5s} {5:<10s}  {6:<10.2f} {7:<10s} {8:<5s} {9:<10s} {10:<10s} {11:<10.2f} {12:<10s} {13:<10s}'.format(zpid,street,city,zipcode,yearbuilt,sqft,round(float(lotsize)/43560,2),bathrooms,bedrooms,lastSale,lastPrice,float(lastPrice)/float(sqft),taxyear,tax))
