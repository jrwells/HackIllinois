import datetime, json, urllib2, MySQLdb
from summarize import *

def resetDB():
	query = "UPDATE `games` SET `finished` = 0;"
	cur.execute(query)

# return a list of game IDs for games that aren't finished
def getUnfinishedGames():
	# get games that have started and haven't finished
	query = "SELECT `game_id` FROM `games` WHERE `start_time` < NOW() AND `finished` = 0;"
	cur.execute(query)

	gameQueue = []
	for row in cur.fetchall():
		gameQueue.append(row[0])
	return gameQueue


def generateSummary(gameData):
	# start with who won and the score
	summary = Summarize.get_winner(gameData)

	blurbs = []

	# notable things - no hitters, perfect games, etc.
	blurbs.append(Summarize.get_no_hitter(gameData))

	# grand slams and home runs
	blurbs.append(Summarize.get_home_runs(gameData))

	# errors
	blurbs.append(Summarize.get_errors(gameData))

	# perfect game
	blurbs.append(Summarize.get_perfect_game(gameData))

	# mvp batter
	blurbs.append(Summarize.get_mvp_batter(gameData))

	# winning pitcher
	blurbs.append(Summarize.get_winning_pitcher(gameData))

	# get top 3 blurbs
	blurbs.sort()
	blurbs.reverse()

	for i in range(0, len(blurbs)):
		if blurbs[i][0] > 0:
			summary = summary + ' {' + str(blurbs[i][0]) + '} ' + blurbs[i][1]

	return summary

def generateTeaserText(gameData):
	return ""

# initialize db connection
db = MySQLdb.connect(
		host="box650.bluehost.com",
		user="colorap5_unclec",
		passwd="zLoV$&mF*M#w",
		db="colorap5_unclec")

cur = db.cursor()

root = 'http://gd2.mlb.com/components/game/mlb/'
current_date = datetime.datetime.now()
day, month, year = current_date.day, current_date.month, current_date.year

url = '%syear_%s/month_%02d/day_%02d/master_scoreboard.json' % (root, year, int(month), int(day))

resetDB()
queue = getUnfinishedGames()

if queue:
	# master_scoreboard = json.load(urllib2.urlopen(url))
	master_scoreboard = json.load(open("master_scoreboard.json"))
	loops = 0

	for record in master_scoreboard['data']['games']['game']:
		if record['id'] in queue:
			if record['status']['status'] == "Final":
				# fetch boxscore and coalesce
				root_dir = "http://gd2.mlb.com" + record['game_data_directory'] + '/boxscore.json'
				boxscore = json.load(urllib2.urlopen(root_dir))['data']['boxscore']
				record['boxscore'] = boxscore

				summary = generateSummary(record)
				teaserText = generateTeaserText(record)

				query = "UPDATE `games` SET `finished` = 1, `full_summary` = '%s', `teaser_text` = '%s' WHERE `game_id` = '%s' LIMIT 1;" % (summary, teaserText, record['id'])
				cur.execute(query)

				loops = loops + 1

	print "Updated %d game(s)" % loops
else:
	print "No missing data ;)"
