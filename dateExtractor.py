import unirest
import json
def getReleaseDate(movie) :
        req = "https://movie-database-imdb-alternative.p.rapidapi.com/?page=1&r=json&type=movie&s=" + movie.replace(' ','+')
        # "https://movie-database-imdb-alternative.p.rapidapi.com/?page=1&r=json&type=movie&s=Casino+Jack"
        # print(req)
        response = unirest.get(req,
                        headers={
                                "X-RapidAPI-Host": "movie-database-imdb-alternative.p.rapidapi.com",
                                "X-RapidAPI-Key": "25ee4b6ce2mshb44bbe000e78fbfp18613fjsn229b35fa0d8d"
                        }
                        )
        # print(response.raw_body)
        di = json.loads(response.raw_body)
        # print(di)
        arr = list(di['Search'])
        found = False
        for x in arr :
                if x['Title'] == movie :
                        found = True
                        imdbID = x['imdbID']

        if not found :
                print("Movie not found")
                return None
        print(imdbID)
        req = "https://movie-database-imdb-alternative.p.rapidapi.com/?i="+imdbID+"&r=json"
        response = unirest.get(req,
                        headers={
                                "X-RapidAPI-Host": "movie-database-imdb-alternative.p.rapidapi.com",
                                "X-RapidAPI-Key": "25ee4b6ce2mshb44bbe000e78fbfp18613fjsn229b35fa0d8d"
                        }
                        )
        di = json.loads(response.raw_body)
        print(di["Title"])
        print(di["Released"])
        return di["Released"]

# movie = "Interstellar"
# getReleaseDate(movie)

di = {}
with open('MovieDetails.json') as f:
    di = json.loads(f.read())
movies = list(di.keys())

releaseDateInfo = {}
for i in range(len(movies)) :
        name, url = movies[i].split("||")
        # print(name, url)
        date = getReleaseDate(name)
        releaseDateInfo[name] = date

with open("releaseDates.json", "w+") as f :
        json.dump(releaseDateInfo, f)