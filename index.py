import sys, os, json
from genshi.template import MarkupTemplate
DOCROOT = os.path.dirname(__file__)
sys.path[:0] = [os.path.join(DOCROOT, "../data")]
import pymongo as pm
import api
con = pm.Connection()
mong = con.mong
from pprint import PrettyPrinter
pprint = PrettyPrinter(indent=3, width=100)

seqTypes = (type([]), type(()))
stringTypes = (type(''), type(u''))

def underfirst(a, b):
    if (a.lower() > b.lower()):
        return 1
    return -1 

def buildRecord(rec, items):
##    items.append(str(type(rec)).replace("<","|"))
##    return
    keys = rec.keys()
    keys.sort(cmp=underfirst)
    line = "<ul>\n"
    for key in keys:
        line += "<li>"
        val = rec[key]
        if val == None or val == "":
            continue
        try:
            val = float(val)
            if val == int(val):
                val = int(val)
            val = str(val)
        except:
            pass
        line += "<i>" + key + ":</i> "
        if key == "DictionaryEntry":
            val = str(type(val)).replace("<","|")
        if (type(val) in seqTypes) or (type(val)==type({}) and len(val)>6):
##                val = "<pre>" + pprint.pformat(val) + "</pre>"
##            val = "***"
            pass
        else:
##            if key != "DictionaryEntry" and '[' in val and ']' in val and val.rfind(']') - val.rfind('[') == 5:
##                query = '?action=query&q={"_id":"%s"}&collection=["Person", "Letter", "Archive", "MPerson", "MPlace", "Event"]' % val
##                link = "<a href='%s' style='text-decoration:none'>%s</a>" % (query, val)
##                line += link
            pass
        line += "%s|%s" % (str(type(val)).replace("<","|"), val)
        line += "</li>\n"
    line += "</ul>\n"
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
        else:
            items.append("no records found")
    else:
        items.append("<i>count:</i> " + str(records))
    print >> sys.stderr, "DEBUG VIEW records:", records

    template = "/template/record.html"
    f = open(DOCROOT + template)
    tmpl = MarkupTemplate(f)
    f.close()
    stream = tmpl.generate(DOCROOT=DOCROOT, items=items, seqTypes=seqTypes)
    output = stream.render('xhtml')

    status = '200 OK'
    response_headers = [('Content-type', 'text/html'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
