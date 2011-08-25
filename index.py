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

def buildRecord(rec, items):
    keys = rec.keys()
    keys.sort(cmp=underfirst)
    for key in keys:
        val = rec[key]
        if val == None:
            val = "null"
        try:
            val = int(val)
            val = str(val)
        except:
            pass
        line = "<i>" + key + ":</i> "
        if '[' in val and ']' in val and val.rfind(']') - val.rfind('[') == 5:
            query = '?action=query&q={"_id":"%s"}&collection=["Person","Group","Letter","Place","Archive","MPerson", "MPlace", "Event"]' % val
            link = "<a href='%s' style='text-decoration:none'>%s</a>" % (query, val)
            line += link
        else:
            line += "%s" % val
        line += "<br/>"
        items.append(line)

def application(environ, start_response):
    output = api.mongoApi(environ)
    records = json.loads(output)['result']
    items = []
    if type(records) in seqTypes:
        if len(records):
            for rec in records:
                if type(rec) in stringTypes:
                    items.append(rec)
                else:
                    buildRecord(rec, items)
                items.append("<br/>")
        else:
            items.append("no records found")
    else:
        items.append("<i>count:</i> " + str(records))
    print >> sys.stderr, "DEBUG VIEW records:", records

    template = "/template/record.html"
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
