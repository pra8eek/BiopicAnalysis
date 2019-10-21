import json
import xmltodict
import datetime
import requests
import time
import textstat
import mwparserfromhell

def getORES(revid): 
	'''
		Uses API to get the scores of a "batch of revisions", optimal batch size is 50
	'''
    url = "https://ores.wikimedia.org/v3/scores/enwiki/?revids=" + str(revid)
    page = requests.get(url)
    di = json.loads(page.text)
    return di

def getReadabilityMetrics(test_data) : 
	'''
		for a given article IN TEXT FORMAT, returns its readability metrics
		Uses textstat library, please install it
	'''
    metric = {"flesch_reading_ease" : textstat.flesch_reading_ease(test_data),
                "smog_index" : textstat.smog_index(test_data),
                "flesch_kincaid_grade" : textstat.flesch_kincaid_grade(test_data),
                "coleman_liau_index" : textstat.coleman_liau_index(test_data),
                "automated_readability_index" : textstat.automated_readability_index(test_data),
                "dale_chall_readability_score" : textstat.dale_chall_readability_score(test_data),
                "difficult_words" : textstat.difficult_words(test_data),
                "linsear_write_formula" : textstat.linsear_write_formula(test_data),
                "gunning_fog" : textstat.gunning_fog(test_data),
                "text_standard" : textstat.text_standard(test_data)}
    return metric

def getCounts(text) :
	'''
		for a given article in TEXT format, returns its wikilinks, references and 
		word count in a dictionary
	'''
    code = mwparserfromhell.parse(text)
    di = { "wikilinks" : len(code.filter_wikilinks()),
          "references" : text.count("<ref>"),
          "words" : text.count(" ")}
    return di

def dateDifference(APIDate, RevisionDate) :
	''' 
		The format of data we get from KnolML is different from the one
		we get using IMDB API, this function converts thm to a common
		format and calculates the difference.
		-30 means 30 days before release, +30 means 30 days after
	'''
    converter = {"Jan":'1', "Feb":'2', "Mar":'3', "Apr":'4', 
            "May":'5', "Jun":'6', "Jul":'7', "Aug":'8',
            "Sep":'9', "Oct":'10', "Nov":'11', "Dec":'12'}
    date = APIDate.split()
    date[1] = date[1].replace(date[1], converter[date[1]])
    date = list(map(int, date[::-1]))
    x = datetime.datetime(date[0], date[1], date[2])
    date = RevisionDate
    date = list(map(int, date.split('-')))
    y = datetime.datetime(date[0], date[1], date[2])
    return (y-x).days

def AnalyzeValidEdits(name, date):
	'''
		Valid edits means the ones within a period of 2 months
		For each valid edit, it does the following 3 tasks
		1) Get its ORES score
		2) Get its readability metrics
		3) Count wikilinks, references and number of words
	'''
    article = "./wiki/" + name.replace(' ','_') + ".xml"
    with open(article, 'r') as f :
        di = xmltodict.parse(f.read())
    
    revisions = [x for x in di['mediawiki']['page']['revision']] #list of all articles for a movie
    revs = [] #Batch of revisions for ORES Analysis
    allORES = {} #will store ORES scores for all revisions

    for i in range(len(revisions)) :
        diff = dateDifference(date ,revisions[i]['timestamp'].split('T')[0])
        if diff < -60 :
            continue
        if diff > 60 :
            allORES.update(getORES(revids))
            break

        metrics = getReadabilityMetrics(revisions[i]['text']['#text'])
        counts = getCounts(revisions[i]['text']['#text'])
        revs.append(revisions[i]['id'])
        
        if len(revs) >= 50 : #since ORES scores are to be calculated in batches of 50s
            revids = str(revs).replace(', ','|')[1:-1].replace("'","")
            revs = []
            allORES.update(getORES(revids))

def getEachArticle() :
    '''
    	This is the driver function, it gets the name of all biopics from MovieDetails.json
    	and their release dates from ReleaseDates from releaseDates.json. Both these files
    	are available in the repository.
    	For each biopic, it performs proper analysis
    '''
    with open("MovieDetails.json",'r') as f :
        movieDetails = json.loads(f.read())
    
    movieNames = [x for x in movieDetails.keys()]
    
    with open("releaseDates.json",'r') as f :
        dates = json.loads(f.read())
    
    for movie in movieNames :
        name, url = movie.split('||')
        date = dates[name] if name in dates else "--" 
        print(name, date)
        if date != "--" : #because we couldn't get all release dates using IMDB API
            AnalyzeValidEdits(name, date) #vaild means before and after 60 days
        break