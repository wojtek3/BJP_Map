import PySimpleGUI as sg
import os
from turtle import color
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
from branca.colormap import LinearColormap
from collections import defaultdict

working_directory = os.getcwd()

sg.theme('SystemDefault1')

logo_column = [[sg.Image('AGH.png', size=(80,80))]]

file_select_column = [[sg.Text("Wybierz plik z danymi:")],
            [sg.InputText(key="-FILE_PATH-"), 
            sg.FileBrowse(initial_folder=working_directory, file_types=[("TXT Files", "*.txt")])],
            [sg.Button('Submit'), sg.Exit()]
        ]

layout = [
    [sg.Column(logo_column),
     sg.VSeperator(),
     sg.Column(file_select_column),]
]

def generateHeatMap(path, priorityData):
    with open(str(path)) as f:
        headers = []
        data = []
        for line in f:
            try:
                data.append([float(i) for i in line.split(",")])
            except:
                headers.append([i for i in line.split(", ")])
      
    priorityIndex = headers[0].index(priorityData)

    mapObj = folium.Map([data[0][0], data[0][1]], zoom_start=12, max_zoom=19, control_scale = True)

    heatmapData = []
    for line in data:
        heatmapData.append([line[0],line[1],line[priorityIndex]])
    #print(heatmapData)

    HeatMap(heatmapData, radius = 40).add_to(mapObj)

    for line in data:
        dataLen = len(line)
        html = "<p><strong>Odczytane dane:</strong></p>\n\n<p>"
        for i in range(2,dataLen):
            html += str(headers[0][i]) + ": " + str(line[i]) + "<br/>"
        html += "</p>"
        iframe = folium.IFrame(html)
        popup = folium.Popup(iframe, min_width = 200, max_width = 200)
        folium.CircleMarker(location=(line[0], line[1]),radius=20, popup=popup, fill_color='transparent', color= 'transparent',tooltip = str(headers[0][priorityIndex]) + ": " + str(line[priorityIndex])).add_to(mapObj)

    mapObj.save("output.html")
    os.system("output.html")

def generateMarkerMap(path,priorityData,minScale,maxScale,Scaletype):
    with open(str(path)) as f:
        headers = []
        data = []
        for line in f:
            try:
                data.append([float(i) for i in line.split(",")])
            except:
                headers.append([i for i in line.split(", ")])
      
    #print(headers)
    priorityIndex = headers[0].index(priorityData)

    if(Scaletype == "WHO"):
        if(priorityData == "PM10" or priorityData == "PM10\n"):
            minScale = 0
            maxScale = 45
        if(priorityData == "PM25" or priorityData == "PM25\n"):
            minScale = 0
            maxScale = 15
        if(priorityData == "PM1" or priorityData == "PM1\n"):
            minScale = 0
            maxScale = 10
        if(priorityData == "TEMP" or priorityData == "TEMP\n"):
            minScale = 0
            maxScale = 30
        if(priorityData == "HUM" or priorityData == "HUM\n"):
            minScale = 0
            maxScale = 100
    if(Scaletype == "auto"):
        col = [column[priorityIndex] for column in data]
        maxScale = max(col)
        minScale = min(col)

    mapObj = folium.Map([data[0][0], data[0][1]], zoom_start=12, max_zoom=19, control_scale = True)

    linear = cm.LinearColormap(['blue', 'green', 'yellow', 'red'],vmin=int(minScale), vmax=int(maxScale))

    linear.caption = 'scale'
    linear.add_to(mapObj)

    for line in data:
        dataLen = len(line)
        html = "<p><strong>Odczytane dane:</strong></p>\n\n<p>"
        for i in range(2,dataLen):
            html += str(headers[0][i]) + ": " + str(line[i]) + "<br/>"
        html += "</p>"
        iframe = folium.IFrame(html)
        popup = folium.Popup(iframe, min_width = 200, max_width = 200)
        #folium.Marker(location=(line[0], line[1]), popup=popup,tooltip = str(headers[0][priorityIndex]) + ": " + str(line[priorityIndex]), icon=folium.Icon(color='#000000',icon_color='#000000')).add_to(mapObj)
        folium.CircleMarker(location=(line[0], line[1]),radius=20, popup=popup, fill_color=linear(line[priorityIndex]), color= linear(line[priorityIndex]),fill_opacity=0.9,tooltip = str(headers[0][priorityIndex]) + ": " + str(line[priorityIndex])).add_to(mapObj)

    mapObj.save("output.html")
    os.system("output.html")

window = sg.Window("Jakość powietrza AGH Solar Plane", layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif (event == "Submit" and values["-FILE_PATH-"] != ""):
        txt_address = values["-FILE_PATH-"]
        print(txt_address)
        with open(txt_address) as f:
            first_line = f.readline()
        vals = first_line.split(", ")[2:]
        # vals[-1] = vals[-1][0:-1]
            
        enterMinMaxLayout = [[sg.Checkbox('Tylko punkty', default = True, key='points')],
            [sg.Text('Typ skali')],
            [sg.HSeparator()],
            [sg.Radio("WHO", "scale", key = "WHO", default = True), sg.Radio("Własna", "scale", key = "own"), sg.Radio("Auto", "scale", key = "auto")],
            [sg.Text('Wartość minimalna'), sg.InputText(size = (10,1), key = "min")],
            [sg.Text('Wartość maksymalna'), sg.InputText(size = (10,1), key = "max")]]
        prioritySelectLayout = [[sg.Text("Wymierz daną do narysowania mapy")],
            [sg.Combo(vals,key='dest')],
            [sg.Button('Generate'), sg.Exit()]
        ]
        window1Layout = [[sg.Column(prioritySelectLayout), sg.VSeparator(),
                         sg.Column(enterMinMaxLayout)]]
        window1 = sg.Window("Jakość powietrza AGH Solar Plane", window1Layout)

        event1, values1 = window1.read()
        print(values1)
        if(values1["points"] == True):
            if(values1["WHO"]): scaleType = "WHO"
            if(values1["own"]): scaleType = "own"
            if(values1["auto"]): scaleType = "auto"
            generateMarkerMap(txt_address, values1["dest"], values1["min"], values1["max"], scaleType) 
            window1.close()
        else:
            generateHeatMap(txt_address, values1["dest"])  
            window1.close()
      
window.close()
