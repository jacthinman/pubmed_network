"""
Structure and Dynamics of Complex Networks Final Project

Lily Pratt & Erik Islo
25 November 2013

Begins by querying Entrez/Medline databases through the Bio python module.
From this data, a JSON file is created. Subsequent runs of the program
append to the existing JSON file, excluding duplicates.

Authors are stored as a dictionary with keys as Author names and values
as a Counter object with all linked authors and their respective connection
weights.
"""

import sys, json
from collections import Counter
from Bio import Entrez, Medline

def authorWeight(coauthors):
  """
  Defines an edge weight for coauthors of a given paper.
  Determined so that the more authors on a paper the weaker their weight.
  """
  coauth = {}
  num_authors = len(coauthors) + 1        # doesn't include current author being updated
  weight = 1.0/(float(num_authors) - 1.0) # each author on paper given same link weight

  for a in coauthors:
    coauth.update({a: weight})

  # returns a dictionary of linked authors and respective edge weights
  return coauth


def addAuthor(authors, author, coauthors):
  if coauthors == []:
    authors.update({author : {}})
  else:
    authors.update({author : authorWeight(coauthors)})

  return authors


def updateAuthor(authors, author, coauthors):
  if coauthors == []:
    pass
  else:
    authors[author] = dict(Counter(authors[author]) + Counter(authorWeight(coauthors)))

  return authors 

#-------------------------------------------------------------------------#
#                END author network updating functions                    #
#-------------------------------------------------------------------------#

def writeToJSON(obj_to_write, file_name):
  # Put Paper Information in a JSON file
  with open(file_name, 'w') as f:
     json.dump(obj_to_write, f, sort_keys=True, indent=4, separators=(',', ': '))
     f.closed

def makeAdjList(authors, file_name="pubmed_authors.txt"):
  with open(file_name, 'w') as f:
    for a in authors:
      au = a.replace(' ','_')
      for co in authors[a]:
        coau = co.replace(' ','_')
        f.write(au + ' ' + coau + ' ' + str(authors[a][co]) + '\n')
  f.close()

# TODO check about adding weights for multiple occurence of same paper
# TODO handle cycles between authors?  Might be cytoscape/nx parsing

def gatherData(search_term, email="lwrpratt@gmail.com"):
  """
  Queries pubmed for papers with the given search_term using the BioPython
  toolkit's Entrez and Medline modules.

  Saves each paper's authors in a dict with all connected authors and
  their repsective connection strength
  """
  
  # Import Existing Author & Paper data
  try:
    with open('authors.json', 'r') as auths:
      authors = json.load(auths)
      auths.closed
  except IOError:
    print "no old data to import, creating new authors dict"
    authors = {}
  try:
    with open('papers.json', 'r') as paps:
      papers = json.load(paps)
      paps.closed
  except IOError:
    print "no old data to import, creating new papers dict"
    papers = {}

  # NCBI identification
  Entrez.email = email

  # See how many papers match this query
  handle = Entrez.esearch(db='pubmed', term=search_term, usehistory='y')
  result = Entrez.read(handle)
  handle.close()
  num_papers = int(result['Count'])
  print str(num_papers) + " papers found with esearch."

  # Get info on these papers, persistent session info
  ids = result['IdList']
  #assert num_papers == len(ids)
  webenv = result["WebEnv"]
  qkey = result["QueryKey"]

  batch = 30
  records = {}

  for p in range(0, num_papers, batch):
    fhandle = Entrez.efetch(db='pubmed', rettype='medline', retmode='text',
                                 retstart=p, retmax=batch,
                                 webenv=webenv, query_key=qkey)
    records = Medline.parse(fhandle)

    for r in records:
      if r:
        idnum = r.get('PMID', '?') 

        if idnum in papers:
          print "Already have %s" % str(idnum)
          pass # Already have this paper

        else:
          papers.update({idnum:{"Title" : r.get('TI', '?'), "Authors" : r.get('AU','?'),"Keywords":r.get('MH','?')}})

          au = r.get('AU', '?')
          if type(au) == str:
            au = [au]
          au.sort()
          for a in au:
            if a in authors:
              au.remove(a)
              authors = updateAuthor(authors, a, au)
              au.append(a) # TODO this is gross and should not stay this way
              au.sort()
            else:
              au.remove(a)
              authors = addAuthor(authors, a, au)
              au.append(a)
              au.sort()
    fhandle.close()
    print "one more done"

  return (authors, papers)

      

#-------------------------------------------------------------------------#
#                          Script starts here                             #
#-------------------------------------------------------------------------#
if __name__ == '__main__':

  print "ARGUMENTS: 1-search term, 2-filename\n"
  search_term = sys.argv[1]
  # fname = sys.argv[2]
  print "gathering data..."
  (Authors, Papers)  = gatherData(search_term)
  print "Total Papers: %s" % len(Papers)
  print "Total Authors: %s" % len(Authors)

  # save data structures for future runs of gatherData()
  writeToJSON(Authors, 'authors.json')
  writeToJSON(Papers, 'papers.json')

  # create file for networkx or cytoscape to read in as network
  makeAdjList(Authors)
