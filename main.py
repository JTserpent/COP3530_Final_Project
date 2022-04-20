from audioop import add
from cgi import test
from queue import Queue
from tkinter import Y
import pandas as pd

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

def addEdge(v1, v2):
    global graph
    if v1 not in graph:
        graph[v1] = []
    if v2 not in graph:
        graph[v2] = []
    temp = [v2, 0]
    graph[v1].append(temp)

def buildGraph(type):
    global rowList
    global rowList1
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
    print("Search similar songs by 1. Valence, 2. Energy, 3. Speechiness, 4. Acousticness, 5. Instrumentalness")
    print("Or enter any other key to exit.")
    key = int(input("Option: "))

    if not key == 1 and not key == 2 and not key == 3 and not key == 4 and not key == 5:
        print("Exit called\n")
        break

    data = pd.read_csv('Data2.csv')
    rowList = []
    suggestions = []

    temp = []

    for index, rows in data.iterrows():
        if rows.Name == song:
            temp = [rows.Name, rows.Valence, rows.Energy, rows.Speechiness, rows.Acousticness, rows.Instrumentalness]
            break

    threshold = float(temp[key])

    if threshold <= 0.1:
        for index, rows1 in data.iterrows():
            row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness, rows1.Instrumentalness]
            if float(row[key]) <= 0.1:
                rowList.append(row)
    elif threshold <= 0.2:
        for index, rows1 in data.iterrows():
            row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness, rows1.Instrumentalness]
            if float(row[key]) > 0.1 and float(row[key]) <= 0.2:
                rowList.append(row)
    elif threshold <= 0.4:
        for index, rows1 in data.iterrows():
            row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness, rows1.Instrumentalness]
            if float(row[key]) > 0.2 and float(row[key]) <= 0.4:
                rowList.append(row)
    elif threshold <= 0.6:
        for index, rows1 in data.iterrows():
            row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness, rows1.Instrumentalness]
            if float(row[key]) > 0.4 and float(row[key]) <= 0.6:
                rowList.append(row)
    elif threshold <= 0.8:
        for index, rows1 in data.iterrows():
            row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness, rows1.Instrumentalness]
            if float(row[key]) > 0.6 and float(row[key]) <= 0.8:
                rowList.append(row)
    else:
        for index, rows1 in data.iterrows():
            row = [rows1.Name, rows1.Valence, rows1.Energy, rows1.Speechiness, rows1.Acousticness, rows1.Instrumentalness]
            if float(row[key]) > 0.8:
                rowList.append(row)
    
    buildGraph(key)

    #print_graph()
    #print("Internal representation: ", graph)

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