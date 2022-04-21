import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import random
import pandas as pd
from queue import Queue

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id='9f9ca718dfae4c37b9ae7d1ad4024938',
                                    client_secret='470f28d7a5eb4c6eb38c61b7d46a3425',redirect_uri="https://open.spotify.com"))

quit = False

print("Welcome to our Spotify recommendation project.")

while not quit:
    lloyd = False
    tree = False

    print("Please select an algorithm to explore:")
    print("1. Lloyd's Algorithm")
    print("2. Organized tree using Breadth First Search")
    response = input("Type 1 or 2: ")

    if (int(response) == 1):
        lloyd = True
        tree = False
    elif (int(response) == 2):
        tree = True
        lloyd = False
    else:
        print("Invalid input.")

    while lloyd:
        results = sp.current_user_saved_tracks()
        for idx, item in enumerate(results['items']):
            track = item['track']
            print(idx, track['artists'][0]['name'], " – ", track['name'])
        print(results['items'][0]['track']['uri'])
        selection = input("Enter the number corresponding to the song you want to find similar songs of: ")

        songURI = results['items'][int(selection)]['track']['uri']
        songName = results['items'][int(selection)]['track']['name']
        features=sp.audio_features(songURI)[0]
        chosenTrack= [songURI,songName, 
               features['valence'], features['energy'],features['speechiness'],features['acousticness']]


        #first you would insert
        def startCentroids(data, n):
            ret = []
            while(len(ret)<n):
                ret.append( data.iloc[random.randint(0,len(data)-1)].values.tolist())
            return ret
        def updateClusterMeans(centroids, clusters):
            converged = True
            for centroid, cluster in zip(centroids, clusters):
                sumEnergy  =0
                sumValence =0
                sumSpeechiness=0
                sumAcousticness=0
                for track in cluster:
                    sumValence+= float(track[2])
                    sumEnergy+=float(track[3])
                    sumSpeechiness+=float(track[4])
                    sumAcousticness+=float(track[5])
                if(sumValence/len(clusters) !=centroid[2]):
                    centroid[2]=sumValence/len(clusters)
                    converged=False
                if(sumEnergy/len(clusters) !=centroid[3]):
                    centroid[3]=sumEnergy/len(clusters)
                    converged=False
                if(sumSpeechiness/len(clusters) !=centroid[4]):
                    centroid[4]=sumSpeechiness/len(clusters)
                    converged=False
                if(sumAcousticness/len(clusters) !=centroid[5]):
                    centroid[5]=sumAcousticness/len(clusters)
                    converged=False
                return converged
        def findBestCluster(row,centroids, clusters):
  
            minDistance = 1000
  
            bestCluster =-1
            distance = 0 
            for i in range(len(centroids)):
                for j in range(len(centroids[0])):
                    try:
                        distance += (float(row[j])-float(centroids[i][j])) ** 2
        
                    except:
                        pass
                if(distance<minDistance):
                    minDistance = distance  
                    bestCluster = i
                distance=0
            clusters[bestCluster].append(row)
            return bestCluster

        data = pd.read_csv('Complete Dataset.csv')
        data = data.loc[abs(data['energy'] -chosenTrack[3])<.05]
        centroids = startCentroids(data,len(data)/50)
        clusters = [[] for i in range(len(centroids))]
        result = [findBestCluster(row,centroids, clusters) for row in 
                  data[['uri','name','valence', 'energy','speechiness','acousticness']].to_numpy()]
        while(updateClusterMeans(centroids, clusters)):
            clusters = [[] for i in range(len(centroids))]
            for row in data[['uri','name','valence', 'energy','speechiness','acousticness']].to_numpy():
                findBestCluster(row,centroids, clusters)
        simTracks = clusters[findBestCluster(chosenTrack, centroids, clusters)]
        similarSongURIs = [track[0] for track in simTracks]
        resultURIs =set()
        for i in range(25):
            resultURIs.add(similarSongURIs[random.randint(0, len(similarSongURIs)-1)])
        results = sp.tracks(resultURIs)

        for track in results['tracks'][:10]:
            print(track['name']," – ", track['artists'][0]['name'])
            try:
                print('audio: ' + track['preview_url'])
            except:
                print("no sample :(")
            print("--"*20)

        lloyd = False

    while tree:
        def add_edge(v1, v2, e):
            global graph
            global nameDict
            global noVertices

            if nameDict.get(v1) == None:
                nameDict[v1] = noVertices
                noVertices += 1
            if nameDict.get(v2) == None:
                nameDict[v2] = noVertices
                noVertices += 1

            if nameDict[v1] not in graph:
                graph[nameDict[v1]] = []
            if nameDict[v2] not in graph:
                graph[nameDict[v2]] = []
    
            temp = [nameDict[v2], e]
            graph[nameDict[v1]].append(temp)

        def buildGraph(type):
            global rowList
            clear_graph()
            print("Building graph, no Vertices = ", noVertices)

            for list in rowList:
                for iter in rowList:
                    if list[0] == iter[0]:
                        continue
                    value = list[type] - iter[type]
                    if abs(value) <= 0.001:
                        add_edge(list[0], iter[0], abs(value))
    
            print("Graph built, no Vertices = ", noVertices)

        def print_graph():
            global graph
            for vertex in graph:
                for edges in graph[vertex]:
                    print(vertex, " -> ", edges[0], " edge weight: ", edges[1])

        def clear_graph():
            global graph
            global nameDict
            global noVertices
            graph = {}
            nameDict = {}
            noVertices = 0

        def BFS(src):
            global graph
            global noVertices
            global nameDict
            global suggestions

            iter = 0

            visited = [False] * noVertices
            q = Queue(maxsize = 0)
            q.put(src)
            visited[src] = True

            while iter < 25:
                iter += 1
                curr = q.get()
                suggestions.append(curr)
                for edges in graph[curr]:
                    if visited[edges[0]] == False:
                        q.put(edges[0])
                        visited[edges[0]] = True
                if q.empty():
                    break


        graph = {}
        nameDict = {}
        noVertices = 0

        shouldExit = False
        while not shouldExit:
            song = input("Enter your favorite song: ")
            print("Search similar songs by 1. Valence, 2. Energy, 3. Speechiness, 4. Acousticness")
            print("Or enter any other key to exit.")
            key = int(input("Option: "))

            if not key == 1 and not key == 2 and not key == 3 and not key == 4:
                print("Exit called\n")
                tree = False
                break

            data = pd.read_csv('Data.csv')
            rowList = []
            suggestions = []

            temp = []

            for index, rows in data.iterrows():
                if rows.Name == song:
                    temp = [rows.Name, rows.Valence, rows.Energy, rows.Speechiness, rows.Acousticness]
                    break

            threshold = float(temp[key])

            if threshold <= 0.05:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) <= 0.05:
                        rowList.append(row)
            elif threshold <= 0.1:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.05 and float(row[key]) <= 0.1:
                        rowList.append(row)
            elif threshold <= 0.2:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.1 and float(row[key]) <= 0.2:
                        rowList.append(row)
            elif threshold <= 0.3:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.2 and float(row[key]) <= 0.3:
                        rowList.append(row)
            elif threshold <= 0.4:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.3 and float(row[key]) <= 0.4:
                        rowList.append(row)
            elif threshold <= 0.5:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.4 and float(row[key]) <= 0.5:
                        rowList.append(row)
            elif threshold <= 0.6:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.5 and float(row[key]) <= 0.6:
                        rowList.append(row)
            elif threshold <= 0.7:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.6 and float(row[key]) <= 0.7:
                        rowList.append(row)
            elif threshold <= 0.8:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.7 and float(row[key]) <= 0.8:
                        rowList.append(row)
            elif threshold <= 0.9:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.8 and float(row[key]) <= 0.9:
                        rowList.append(row)
            else:
                for index, rows1 in data.iterrows():
                    row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness]
                    if float(row[key]) > 0.9:
                        rowList.append(row)
    
            buildGraph(key)

            song = temp[0]
            ID = nameDict[song]
            print("\nSelected song: ", song)

            BFS(ID)

            print("Here is a list of similar songs you may enjoy:\n")
            for i in suggestions:
                for j in nameDict:
                    if nameDict[j] == i:
                        print(j)
    
            loop = input("\nTry again with another song? Y/n: ")
            if loop == 'Y':
                shouldExit = False
            else:
                print("Exit called")
                shouldExit = True
                tree = False