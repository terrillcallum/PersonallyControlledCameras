import requests

x = requests.get('https://docs.google.com/spreadsheets/d/1JVpGrSsblszaP8G7RmjzyXm71bsxlPGo_ayK8gjQeUo/gviz/tq?tqx=out:json&tq&gid=0')

print(x.text)