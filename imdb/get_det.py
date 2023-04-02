import requests

class imdb:
    def get_from_api(self,url):
        r = requests.get(url).json()
        names = []
        images = []
        ratings = []
        year = []
        
        for d in r['results']:
            try:
                names.append(d['original_name'])
            except:
                names.append(d['original_title'])
            try:
                images.append("https://www.themoviedb.org/t/p/w440_and_h660_face"+d['poster_path'])
            except:
                pass
            try:
                ratings.append(d['vote_average'])
            except:
                ratings.append("-")
            try:
                year.append(d['release_date'].split("-")[0])
            except:
                year.append(d['first_air_date'].split("-")[0])
            
        return zip(names, images,ratings,year)
       
    
    def get_movie_show(self,name,year):
    
        url = f"http://www.omdbapi.com/?apikey=42c20a9c&t={name}+&plot=full&y={year}"
        result = requests.get(url).json()
        
        all_items = {
            "title" : result["Title"],
            "year" : result["Year"][0:4],
            "poster" : result["Poster"],
            "genre" : result["Genre"],
            "director" : result["Director"],
            "plot" : result["Plot"],
            "metascore": result["Metascore"]+"%",
            "imdb_rating" : result["imdbRating"],
            "awards" : result["Awards"],
        }

    
        return all_items
        
    def search_sugg(self,q):
        url = f"http://www.omdbapi.com/?apikey=42c20a9c&s={q}"
        r = requests.get(url).json()
        titles = []
        posters = []
        years = []
        
        try:
            for d in r['Search']:
                titles.append(d['Title'])
                posters.append(d['Poster'])
                years.append(d['Year'][0:4])
        except:
            titles.append("No Results found") 

        all_items = {
            "titles" : titles,
            "posters" : posters,
            "years" : years,
        }
        return all_items
    
