import sys, os, json
from genshi.template import MarkupTemplate
DOCROOT = os.path.dirname(__file__)
sys.path[:0] = [os.path.join(DOCROOT, "../data")]
import pymongo as pm
import api
from bson.objectid import ObjectId
con = pm.Connection()
mong = con.mong

seqTypes = (type([]), type(()))
stringTypes = (type(''), type(u''))

def underfirst(a, b):
    if (a.lower() > b.lower()):
        return 1
    return -1 

letter_keys = ["Author", "Source", "Recipient", "Destination", "DateRaw", "Archive_ID", "_id"]
person_keys = ["First", "Last", "BirthDate", "Archive_ID", "_id"]

def buildHeader(rec, items):
    global keys
    if "Author" in rec.keys():
        keys = letter_keys
    else:
        keys = person_keys
    line = []
    for key in keys:
        line.append(key)
    items.append(line)

def buildRecord(rec, items):
    line = []
    for key in keys:
        val = rec[key]
        if val == None:
            val = "null"
        try:
            val = int(val)
            val = str(val)
        except:
            pass
        if '[' in val:
            query = 'index.py?action=query&q={"_id":"%s"}&collection=["Person","Group","Letter","Location","Archive"]' % val
            link = "<a href='%s' style='text-decoration:none'>%s</a>" % (query, val)
            line.append(link)
        else:
            line.append("%s" % val)
    items.append(line)

def application(environ, start_response):
    output = api.mongoApi(environ)
    records = json.loads(output)['result']
    items = []
    if type(records) in seqTypes:
        if len(records):
            items.append(str(len(records)) + " records")
            buildHeader(records[0], items)
            for rec in records:
                buildRecord(rec, items)
        else:
            items.append("no records found")
    else:
        items.append("<i>count:</i> " + str(records))
    print >> sys.stderr, "DEBUG VIEW items:", items

    template = "/template/record_tab.html"
    f = open(DOCROOT + template)
    tmpl = MarkupTemplate(f)
    f.close()
    stream = tmpl.generate(DOCROOT=DOCROOT, items=items)

    output = stream.render('xhtml')

    status = '200 OK'
    response_headers = [('Content-type', 'text/html'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
