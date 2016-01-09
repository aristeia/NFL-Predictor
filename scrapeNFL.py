import os, sys, requests, re, math, random, json, io
from random import shuffle
from time import sleep, time
from Levenshtein import ratio
from statistics import mean, pstdev
from scipy.stats import norm


tableheads = re.compile('<th')
tableheade = re.compile('<\/\w*>')

tablebodys = re.compile("<tbody>")

tablecells = re.compile('<td[\s\w="]*>\s*')
tablecellm = re.compile(".*<\/td>")
tablecelle = re.compile("\s*<\/td>")

alinks = re.compile('<a href="[^"]*">')
alinke = re.compile('<\/a>')

badChars = re.compile("[A-Za-z\s\+]")

categories = {
  # 'statisticPositionCategory': [
  #   "Quarterback",
  #   "Running Back",
  #   "Wide Receiver",
  #   "Tight End",
  #   "Defensive Lineman",
  #   "Linebacker",
  #   "Defensive Back",
  #   "Kickoff Kicker",
  #   "Kick Returner",
  #   "Punter",
  #   "Punt Returner",
  #   "Field Goal Kicker"],
  'offensiveStatisticCategory': [
    "Game Stats",
    "Total Yards",
    "Passing",
    "Rushing",
    "Receiving",
    "Kicking",
    "Field Goals",
    "Kick Returns",
    "Punting",
    "Scoring",
    "Touchdowns",
    "Offensive Line"],
  'defensiveStatisticCategory': [
    "Game Stats",
    "Total Yards",
    "Passing",
    "Rushing",
    "Receiving",
    "Sacks",
    "Scoring",
    "Touchdowns",
    "Tackles",
    "Interceptions"]
}

options = {
  'role' : {
    'statisticPositionCategory': None,
    'offensiveStatisticCategory': "TM",
    'defensiveStatisticCategory': "OPP"
  },

  'tabSeq' : {
    'statisticPositionCategory': '1',
    'offensiveStatisticCategory': '2',
    'defensiveStatisticCategory': '2'
  }
}

perGameStats = {
  "offensiveStatisticCategory": {
      "Game Stats": [
        "Pen", 
        "Pen Yds", 
        "FUM ", 
        "Lost ",
      ],

      "Passing": [
        "TD",
        "Int",
        "Sck"

      ],

      "Rushing": [
        "TD"
      ],

      "Offensive Line": [
        "QB Hits"
      ]
    },

  'defensiveStatisticCategory': {
      "Game Stats": [
        "Pen",
        "Pen Yds",
      ],

      "Passing": [
        "Td",
        "Int"
      ],

      "Rushing":[
        "TD"
      ],

      "Sacks":[
        "Sck",
        "PDef",
        "FF",
        "Rec"
      ],

      "Touchdowns":[
        "Def"
      ]

    }
  }


data = {}


teams = {
  "Jacksonville Jaguars": "Jacksonville Jaguars",
  "Cardinals": "Arizona Cardinals",
  "49ers": "San Francisco 49ers",
  "Bears": "Chicago Bears",
  "Bengals": "Cincinnati Bengals",
  "CIN": "Cincinnati Bengals",
  "SD": "San Diego Chargers",
  "Bills": "Buffalo Bills",
  "New York Jets": "New York Jets",
  "Packers": "Green Bay Packers",
  "DET": "Detroit Lions",
  "Patriots": "New England Patriots",
  "Giants": "New York Giants",
  "PIT": "Pittsburgh Steelers",
  "Houston Texans": "Houston Texans",
  "Buffalo Bills": "Buffalo Bills",
  "MIA": "Miami Dolphins",
  "SF": "San Francisco 49ers",
  "Cleveland Browns": "Cleveland Browns",
  "STL": "St. Louis Rams",
  "Baltimore Ravens": "Baltimore Ravens",
  "CLE": "Cleveland Browns",
  "New York Giants": "New York Giants",
  "Colts": "Indianapolis Colts",
  "DAL": "Dallas Cowboys",
  "Falcons": "Atlanta Falcons",
  "Saints": "New Orleans Saints",
  "Redskins": "Washington Redskins",
  "Browns": "Cleveland Browns",
  "KC": "Kansas",
  "CAR": "Carolina Panthers",
  "NO": "New Orleans Saints",
  "Jaguars": "Jacksonville Jaguars",
  "ARI": "Arizona Cardinals",
  "BUF": "Buffalo Bills",
  "Green Bay Packers": "Green Bay Packers",
  "New Orleans Saints": "New Orleans Saints",
  "Carolina Panthers": "Carolina Panthers",
  "Denver Broncos": "Denver Broncos",
  "BAL": "Baltimore Ravens",
  "Jets": "New York Jets",
  "Rams": "St. Louis Rams",
  "CHI": "Chicago Bears",
  "Tampa Bay Buccaneers": "Tampa Bay Buccaneers",
  "ATL": "Atlanta Falcons",
  "Lions": "Detroit Lions",
  "Miami Dolphins": "Miami Dolphins",
  "Cincinnati Bengals": "Cincinnati Bengals",
  "HOU": "Houston Texans",
  "Raiders": "Oakland Raiders",
  "Arizona Cardinals": "Arizona Cardinals",
  "Cowboys": "Dallas Cowboys",
  "Buccaneers": "Tampa Bay Buccaneers",
  "Pittsburgh Steelers": "Pittsburgh Steelers",
  "Seahawks": "Seattle Seahawks",
  "San Diego Chargers": "San Diego Chargers",
  "WAS": "Washington Redskins",
  "NYJ": "New York Jets",
  "Ravens": "Baltimore Ravens",
  "Detroit Lions": "Detroit Lions",
  "Atlanta Falcons": "Atlanta Falcons",
  "New England Patriots": "New England Patriots",
  "Minnesota Vikings": "Minnesota Vikings",
  "Oakland Raiders": "Oakland Raiders",
  "St. Louis Rams": "St. Louis Rams",
  "TEN": "Tennessee Titans",
  "IND": "Indianapolis Colts",
  "Philadelphia Eagles": "Philadelphia Eagles",
  "Washington Redskins": "Washington Redskins",
  "SEA": "Seattle Seahawks",
  "Vikings": "Minnesota Vikings",
  "DEN": "Denver Broncos",
  "OAK": "Oakland Raiders",
  "Broncos": "Denver Broncos",
  "GB": "Green Bay",
  "NYG": "New York Giants",
  "Dallas Cowboys": "Dallas Cowboys",
  "NE": "New England Patriots",
  "Texans": "Houston Texans",
  "Chicago Bears": "Chicago Bears",
  "Dolphins": "Miami Dolphins",
  "Chiefs": "Kansas City Chiefs",
  "JAC": "Jacksonville Jaguars",
  "Titans": "Tennessee Titans",
  "PHI": "Philadelphia Eagles",
  "Seattle Seahawks": "Seattle Seahawks",
  "Eagles": "Philadelphia Eagles",
  "Kansas City Chiefs": "Kansas City Chiefs",
  "Tennessee Titans": "Tennessee Titans",
  "TB": "Tampa Bay Buccaneers",
  "Indianapolis Colts": "Indianapolis Colts",
  "Chargers": "San Diego Chargers",
  "Panthers": "Carolina Panthers",
  "San Francisco 49ers": "San Francisco 49ers",
  "Steelers": "Pittsburgh Steelers",
  "MIN": "Minnesota Vikings"}

def addToTeams(t):
  if t not in teams.keys():
    bestTeam = max(list(teams.keys()), key=lambda x: ratio(x,t))
    teams[t] = teams[bestTeam]


minFields = {}
meanFields = {}

def getDict(ref, *args):
  if len(args)==0:
    return ref
  if args[0] not in ref:
    ref[args[0]] = {}
  return getDict(ref[args[0]],*args[1:])


# if len(sys.argv)>1:
#   if '-h' in sys.argv or '--help' in sys.argv:
#     print("I would help you...") 
#   elif '-s' in sys.argv or '--start' in sys.argv:
    

minYear = 2000
maxYear = 2014

seasons = range(maxYear, minYear-1, -1)

seasonType = "REG"

conference = "null"

base_url = "http://www.nfl.com/stats/categorystats?"

queryKeys = ["conference", "seasonType", "season"]
queryVals = [conference, seasonType]


thisQueryKeys, thisQueryVals = queryKeys[:], queryVals[:]
for season in seasons:
  if season not in data:
    data[season] = {}
  for category, vals in categories.items():
    if category not in data[season]:
      data[season][category] = {}
    thisQueryVals.append(season)
    for k, v in options.items():
      if v[category] is not None:
        thisQueryKeys.append(k)
        thisQueryVals.append(v[category])
    for val in vals:
      if val not in data[season][category]:
        data[season][category][val] = {}
      try:
        res = requests.get(base_url, params = dict(zip(thisQueryKeys+[category], thisQueryVals+[val.upper().replace(' ','_')])), timeout=5)
        html = ' '.join(list(res.iter_lines(decode_unicode=True)))
        onTable = False
        head, body = tablebodys.split(html)
        fields = []
      except Exception:
        break
      try:
        for header in tableheads.split(head.split('<tr')[-1]):
          if '</th>' in header:
            fields.append(str(tableheade.split(header)[0].split('>')[-1]).strip())
            data[season][category][val][fields[-1]] = []
        if "Team" not in fields:
          print("Skipping "+category+val)
          break
        for thing in tablecells.split(body):
          if tablecellm.match(thing):
            word = tablecelle.sub('',thing)
            if '1' in word and not onTable:
              onTable = True
              i=0
            if onTable:
              if alinks.match(word):
                word = alinke.split(alinks.sub('',word))[0]
              currentVal = str(word).split('<')[0].strip(' +').replace(',','')
              if "Team" == fields[i]:
                addToTeams(currentVal)
                currentVal = teams[currentVal]
              else:
                if ":" in currentVal:
                  top = [int(d) for d in currentVal.split(':')]
                  while len(top) < 3:
                    top.insert(0,0)
                  currentVal = sum([top[t]*60**(t) for t in range(3)])
                else:
                  currentVal = badChars.sub('', currentVal)
                  if '-' in currentVal:
                    if all(c=='-' for c in currentVal):
                      currentVal = 0
                    elif currentVal[0] != '-':
                      g,b = [float(a) for a in currentVal.split('-')]
                      currentVal = (g/(g+b) if g+b>0 else 0)
                currentVal = float(currentVal) 
                if 0>currentVal:
                  if fields[i] not in minFields or -1*currentVal > minFields[fields[i]]:
                    minFields[fields[i]] = -1*currentVal
              data[season][category][val][fields[i]].append(currentVal)
              if alinks.match(word) or '</tbody>' in word:
                break
              elif '</tr>' in word:
                i=0
              else:
                i+=1
        for field in fields:
          if field != "Team":
            ref = getDict(meanFields,field,category,val)
            ref[season] = mean(data[season][category][val][field])
            if field in minFields:
              for j in range(len(data[season][category][val][field])):
                data[season][category][val][field][j] += minFields[field]
            if val in perGameStats[category] and field in perGameStats[category][val]:
              for i in range(len(data[season][category][val][field])):
                games = float(data[season][category][val]["G"][i]) if "G" in data[season][category][val] else 16
                data[season][category][val][field][i] = str(float(data[season][category][val][field][i]) / games)
      except Exception as e:
        print("Warning:")
        print(e)
        pass
        # if val in data[season][category]:
        #   data[season][category].pop(val)
    thisQueryKeys, thisQueryVals = queryKeys[:], queryVals[:]
  #   if len(data[season][category]) == 0:
  #     data[season].pop(category)
  # if len(data[season])==0:
  #   data.pop(season)
dim = 0


# print(meanFields)
for field, fields in meanFields.items():
  for category, categories in fields.items():
    for subcat, subcats in categories.items():
      dim+=1
      for season, mn in subcats.items():
        if abs(mn)<0.01:
          # fieldvals = [(data[stemp][category][subcat][field].count(d),d )
          #   for stemp in range(maxYear,minYear-1,-1)
          #   if stemp in data and field in data[stemp][category][subcat]
          #   for d in data[stemp][category][subcat][field] if type(d) is not str]
          # if len(fieldvals)>0 and abs(max(fieldvals)[1]) <0.01:
          available_newmins = sorted([
              ( (maxYear-minYear) - abs(s-season),
                meanFields[field][category][subcat][s]) 
              for s in meanFields[field][category][subcat].keys()
              if abs(meanFields[field][category][subcat][s])>0.01],
            reverse=True)
          if len(available_newmins)>0:
            for d in range(len(data[season][category][subcat][field])):
              data[season][category][subcat][field][d] = available_newmins[0][1]

print("Dimensions of available features:",dim)

exact_data = {}
scorediff = []
for fname in os.listdir("nfl_results"):
  if '.csv' in fname:
    year = int(''.join([c for c in fname if c.isdigit()]))
    if year>=minYear and year<=maxYear:
      exact_data[year] = []
      with open("nfl_results/"+fname) as f:
        f.readline()
        for line in f:
          ln = line.strip().split(',')
          exact_data[year].append([ln[3],ln[6],int(ln[4])-int(ln[5])])
          scorediff.append(exact_data[year][-1][-1])
          addToTeams(ln[3])
          addToTeams(ln[6])

score_mean = mean(scorediff)
score_stdev = pstdev(scorediff)
rvar = norm(scale=score_stdev, loc=score_mean)

for season, vals in exact_data.items():
  for i in range(len(vals)):
    vals[i] = (teams[vals[i][0]],
      teams[vals[i][1]],
      rvar.cdf(vals[i][2])*2.0 - 1.0 )


with io.open("nfl.json",'w',encoding='utf8') as dataFile:
  json.dump({
      'teams': teams,
      'data': data,
      'data_dims': dims,
      'exact_data': exact_data,
      'exact_metadata': {
        'mean': score_mean,
        'stdev': score_stdev
        }
      },
    dataFile, 
    ensure_ascii=False)

print("Wrote everything to nfl.json")

def printDataFound():
  for t in teams.keys():
    print(t)
  for s in data.keys():
    print(s)
    for c in data[s].keys():
      print('  '+c)
      for v in data[s][c].keys(): 
        print('      '+v)
        for f in data[s][c][v].keys():
          print('        '+f)
          for datum in data[s][c][v][f]:  
            print('          '+datum)
