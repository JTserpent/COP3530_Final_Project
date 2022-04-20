#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import random
import pandas as pd

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id='9f9ca718dfae4c37b9ae7d1ad4024938',
                                    client_secret='470f28d7a5eb4c6eb38c61b7d46a3425',redirect_uri="https://open.spotify.com"))

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





