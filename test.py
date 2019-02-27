import requests, re, json, time, shutil, os
from tkinter import filedialog, Tk, BOTH
from lxml import etree


apikey = "f875e798c9312f187fa54d982079111fd02adfa72d5b4ad4157c5ec6374e283b"
headers= {"accept" : "application/json"}
rootdir = (os.environ['USERPROFILE']+"Kodi/Game/")
xmldir = (os.environ['USERPROFILE']+"/Kodi/Game/xmls/")
games = []
game_ids = []
root = Tk()
root.withdraw()
directory = filedialog.askdirectory()
dev_list = []
c = 0

genres=['Action', 'Adventure', 'Construction and Management Simulation', 'Role-Playing', 'Puzzle', 'Strategy', 'Racing', 'Shooter', 'Life Simulation', 'Fighting', 'Sports', 'Sandbox', 'Flight  Simulator', 'MMO', 'Platform', 'Stealth', 'Music', 'Horror', 'Vehicle Simulation']

b_url = "https://api.thegamesdb.net/"
image_url = (b_url+"Games/Images?apikey="+apikey+"&games_id=")
s_url = (b_url+"/Games/ByGameName?apikey="+apikey+"&name")

dev_resp = requests.get(b_url+"Developers?apikey="+apikey, headers=headers)
prsd_dev = json.loads(dev_resp.text)


def urlify(s):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a %20
    s = re.sub(r"\s+", '+', s)

    return s

# This scrapes 'thegamesDB' for the gameIDs (you need those to search for 
# fanart) and most of the text info such as genres title etc.
def scrape(game):
	gameDevs = []
	genreNames = [] 
	search = (s_url+game+"&fields=publishers%2Cgenres%2Coverview&filter%5Bplatform%5D=1")
	response = requests.get(search, headers=headers)
	parsed_response = json.loads(response.text)
	if(parsed_repsonse['data']['count']>0):
		game_D = parsed_response['data']['games'][0]
		game_ids.append(game_D['id'])
		name = game_D['game_title']
		year_rlsd = game_D['release_date'][:4]
		genres = game_D['genres']
		for genreID in genres:
			genreNames.append(genres[genresID-1])
		devIDs = game_D['developers']
		for ID in devIDs:
			ID = str(ID)
			gameDevs.append(prsd_dev['data']['developers'][ID]['name'])
		plot = game_D['overview']
	else:
		game_ids.append([])
	return name, year_rlsd, genreNames, gameDevs, plot
#I may add one or two other scrapers here for icons/trailers if thegamesdb
#doesnt add them
#def icon_scr(game)
#def trailer_scr(game)
	
#This one generates the needed xml 
def generatexml(game):
	root = etree.Element("advanced_emulator_launcher_configuration")
	cat	= etree.Element("category")
	root.append(cat)
	catname=etree.Element("name")
	catname.text = 'PC'
	cat.append(catname)
	launcher = etree.Element("launcher")
	name = etree.Element("name")
	category = etree.Element("category")
	year_released = etree.Element("year")
	genres = etree.Element("genre")
	developers = etree.Element("developer")
	rating = etree.Element("rating")
	plot = etree.Element("plot")
	platform = etree.Element("platform")
	application = etree.Element("application")
	# icon = tobeadded
	fanart = etree.Element("s_fanart")
	banner = etree.Element("s_banner")
	poster = etree.Element("s_poster")
	clearlogo = etree.Element("s_clearlogo")
	trailer = etree.Element("s_trailer")
	boxfront = etree.Element("path_boxfront")
	boxback = etree.Element("path_boxback")
	
	application.text=(directory+"/"+game+".lnk")
	
	fields = scrape(game)
	xmlfields = [name, year_released, genres, developers, plot]
	

	i=0
	for field in fields:
		if type(field) is list:
			xmlfields[i].text = ",".join(field)
		elif type(field) is float:
			xmlfields[i].text = str(int(field))
		elif type(field) is not str:
			xmlfields[i].text = str(field)
		else:
			xmlfields[i].text = re.sub(r"–", '-', field)
		launcher.append(xmlfields[i])
		i+=1
	
	category.text = "PC"
	platform.text = "Microsoft Windows"
	launcher.insert(1, category)
	launcher.insert(7, platform)
	launcher.insert(8, application)
	# working_file = open(field[0]+".xml","w+")
	if game_ids[c]:
		gamedir = str(rootdir+urlify(games[c]))
		if not os.path.exists(gamedir):
			os.mkdir(gamedir)
		i_url = (image_url+str(game_ids[c]))
		i_resp = requests.get(i_url, headers=headers)
		i_p = json.loads(i_resp.text)
		i_urls = []
		f=s=fbox=bbox=cl=ba=p=0
		for url in i_p['data']['images'][str(game_ids[c])]:
			img_req = requests.get(i_p['data']['base_url']['original']+url['filename'], headers=headers, stream=True)
			if url['type'] == 'fanart':
				open(gamedir+'/fanart'+str(f)+'.jpg', 'wb').write(img_req.content)
				fanart.text = str(gamedir)+'/fanart0.jpg'
				launcher.append(fanart)
				if f>0:
					poster.text = str(gamedir)+'/fanart1.jpg'
					launcher.append(poster)
				f += 1
			elif url['type'] == 'banner':
				open(gamedir+'/banner'+str(ba)+'.jpg', 'wb').write(img_req.content)
				banner.text = str(gamedir)+'/banner0.jpg'
				launcher.append(banner)
				ba += 1
			elif url['type'] == 'screenshot':
				open(gamedir+'/screenshots'+str(s)+'.jpg', 'wb').write(img_req.content)
				s += 1
			elif url['type'] == 'poster':
				open(gamedir+'/poster'+str(p)+'.jpg', 'wb').write(img_req.content)
				poster.text = str(gamedir)+'/poster0.jpg'
				launcher.append(poster)
				p +=1
			elif url['type'] == 'boxart':
				if url['side'] == 'front':
					open(gamedir+'/front-boxart'+str(fbox)+'.jpg', 'wb').write(img_req.content)
					boxfront.text = str(gamedir+'/front-boxart0.jpg')
					launcher.append(boxfront)
					fbox += 1
				else:
					open(gamedir+'/back-boxart'+str(bbox)+'.jpg', 'wb').write(img_req.content)
					boxback.text = str(gamedir+'/back-boxart0.jpg')
					launcher.append(boxback)
					bbox += 1
			elif url['type'] == 'clearlogo':
				open(gamedir+'/clearlogo'+str(cl)+'.png', 'wb').write(img_req.content)
				clearlogo.text = str(gamedir)+'/clearlogo0.png'
				launcher.append(clearlogo)
				cl += 1
			else:
				open(gamedir+'/uncategorized_image'+str(c)+'.jpg', 'wb').write(img_req.content)
	
	root.append(launcher)
	return etree.tostring(root, encoding='utf-8').decode("utf-8") 


for root, dirs, files in os.walk(directory):
	for name in files:
		if name.endswith("lnk"):
			link = name.strip(".lnk")
			games.append(link)
#get list of shortcuts in directory
countGames = len(games)
for game in games:
	with open(xmldir+urlify(game)+".xml", "w+") as myfile:
		myfile.write(str(generatexml(game)))
	c+=1

