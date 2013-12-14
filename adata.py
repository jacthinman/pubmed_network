"""
Provides author search functionality for through a json collection
of papers.  Returns Keywords and Title of papers co-authored by the
queried author.

Requires a papers.json file created with get_data.py in the same directory
"""

import json

def writeToJSON(obj_to_write, file_name):
  # Put Paper Information in a JSON file
  with open(file_name, 'w') as f:
     json.dump(obj_to_write, f, sort_keys=True, indent=4, separators=(',', ': '))
     f.closed





def authorKeywords(papers, author):
  authkey = {}

  for i in papers:
    if author in papers[i]['Authors']:
      if author not in authkey:
        print "found %s" % author
        titletemp = papers[i]['Title']
        keytemp = papers[i]['Keywords']
        
        authkey[author] = {"Paper IDs" : [i], "Titles" : [titletemp], "Keywords":[keytemp]}
      else:
        #print "updating %s" % author
        titemp = papers[i]['Title']
        ktemp = papers[i]['Keywords']

        authkey[author]['Paper IDs'].extend([i])
        authkey[author]['Titles'].extend([titemp])
        authkey[author]['Keywords'].extend(ktemp)

  if authkey == {}:
    print "No Author by given name found."
  return authkey




go = True
split = "="*65
# read in the papers dict
with open('papers.json', 'r') as pap:
  papers = json.load(pap)
  pap.closed


while go == True:
  au = raw_input('Author Name & last initial (type "done" to exit): ')
  if au == 'done':
    go = False
  else:
    keys = authorKeywords(papers, au)

    # output to command line
    print "\n" + split + "\n\n"
    for a in keys:
      for entry in keys[a]:
        if entry != "Paper IDs":
          for t in keys[a][entry]:
            print "%s: %s" % (entry, t)
          print "\n"

    #print "Author Queried by: %s"
    #print "%s papers and %s keywords" % (str(), str(len()))
    print split + "\n"
