import ssl
import reverse_geocoder
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic 
import time


def read_file(path, year):
    '''
    (str) -> list
    Return list of lines from file, filmed in the specific year.
    '''
    result = []
    f = open(path, encoding='utf-8', mode="r", errors='ignore')

    data = f.readline().strip("\n")

    while data != "==============":
        data = f.readline().strip("\n")

    while data != "--------------------------------------------------------------------------------":
        data = f.readline().strip("\n")
        data1 = data.replace("\t", "").replace('"', "")
        ind = (data1.find("{"), data1.find("}"))
        if ind[0] != -1:
            data1 = data1[:ind[0]] + data1[ind[1] + 1:]
        ind = (data1.find("("), data1.find(")"))
        result.append([data1[:ind[0] - 1], data1[ind[0] + 1:ind[1]],
                    data1[ind[1] + 1:].strip(" ")]) 
    del result[-1]

    dict_of_films = dict()
    year = str(year)
    i = 0
    for film in result:
        loc = film[2]
        index1 = loc.find("(")
        index2 = loc.find(")")
        if index1 != -1 and index2 != -1:
            new_loc = loc[:index1] + loc[index2+1:]
            film[2] = new_loc
        if film[1] == year:
            if film[0] not in dict_of_films:
                dict_of_films[film[0]] = film[2]
            else:
                dict_of_films[film[0]] += film[2]


    return dict_of_films

    
def create_map(dct, latitide, longitude, year, path):
    user_location =  (latitide, longitude)
    ssl._create_default_https_context = ssl._create_unverified_context
    my_map = folium.Map()
    geoloc = Nominatim(timeout=10, user_agent='my-app')
    dict_of_distances = dict()
    start = time.perf_counter()
    for el in dct:
        try:
            loc = geoloc.geocode(dct[el])
            location = (loc.latitude, loc.longitude)
            dict_of_distances[geodesic(location, user_location).km] = (dct[el], el, location)
        except BaseException as err:
            pass
        if time.perf_counter() - start > 100:
            break
    min_dist = dict()
    for i in range(2):
        min_distance = min(dict_of_distances)
        min_dist[min_distance] = dict_of_distances[min_distance]
        del dict_of_distances[min_distance]
    film_layer_1 = folium.FeatureGroup(name='Films that were shooted in {}'.format(str(year)))
    for dist in min_dist:
        film_layer_1.add_child(folium.Marker(location=min_dist[dist][2], popup=min_dist[dist][1]
                                + ', location: ' + min_dist[dist][0],
                                icon=folium.Icon(color='blue',
                                icon='cloud')))


    f = open(path, encoding='utf-8', mode="r", errors='ignore')
    result = []
    for line in f.readlines():
        line = line.split('—')
        result.append(line)
    del result[-1]
    capitals = list()
    for line in result:
        capitals.append(line[1][1:-1])
    
    film_layer_2 = folium.FeatureGroup(name='Capitals of the all countries.')
    try:
        for cap in capitals:
            loc = geoloc.geocode(cap)
            location = (loc.latitude, loc.longitude)
            film_layer_2.add_child(folium.Marker(location=location, icon=folium.Icon(color='red', icon='cloud')))
    except BaseException as err:
        pass

    my_map.add_child(film_layer_1)
    my_map.add_child(film_layer_2)
    my_map.add_child(folium.LayerControl())
    my_map.save('movies_map_.html')

    return 'Finished. Please have look at the map movies_map_.html'

    

if __name__ == "__main__":
    year = input('Please enter a year you would like to have a map for: ')
    location = input('Please enter your location (format: lat, long): ').split(',')
    print('Map is generating...')
    print('Please wait...')
    print(create_map(read_file('locations.list.txt', year), location[0], location[1], year, 'capitals.txt'))


