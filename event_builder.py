#Creates the events based on data from metrics
from event import *

#Arbitrary Constants
INNING_RUN_PERCENT_THRESHOLD = .4
INNING_RUN_TOTAL_THRESHOLD = 3
INNING_RUN_LOSS_MULTIPLIER = .75
IMPRESSIVE_AMOUNT_OF_INNINGS_PITCHED = 8

# Arbitrary Weights
INNING_RUN_MAX_WEIGHT = .7
STAR_PITCHER_BASE_WEIGHT = .4

from metrics import *
from summary_builder import *
from event import *
class EventBuilder:
	def __init__(self, gameData):
		if (int(gameData['linescore']['r']['home']) > int(gameData['linescore']['r']['away']) ):
			self.winning_team = "home"
		else:
			self.winning_team = "away"

		self.gameData = gameData

		self.build_events()

	def build_events(self):
		#inning runs total runs
		inning_runs = self.build_inning_events(Metrics.InningRunsTotalRuns(self.gameData))
		print inning_runs

		#walked in runs
		walked_runs = self.build_walks_events(Metrics.WalksAndBalks(self.gameData))
		print walked_runs

		#pitching changes
		pitching_changes = self.build_pitching_change_events(Metrics.PitchingChangeDistribution(self.gameData))
		print pitching_changes

		#Game batting ave
		game_batting_ave = self.build_batting_average_events(Metrics.GameBattingAvgVsSeason(self.gameData))
		print game_batting_ave

		#Lead changes
		lead_changes = self.build_lead_change_events(Metrics.LeadChanges(self.gameData))
		print lead_changes

		#RBI percentage
		rbi_percentage = self.build_rbi_events(Metrics.RBIDistribution(self.gameData))
		print rbi_percentage

		return (inning_runs + walked_runs + pitching_changes + game_batting_ave +
			lead_changes + rbi_percentage)

	def build_inning_events(self, inning_metrics):
		""" Builds the events for highest scoring innings, returns a list of
			events. """
		#Needed to look up team data and names
		team_names = (self.gameData['away_team_name'], self.gameData['home_team_name'])
		team_designation = ('away','home')
		team_index = 0
		team_desc = ''
		events = []
		for team in inning_metrics:
			#Runs the equation to determine the weight, dependant entirely on
			#constants at the start of the file
			weight = float(team[team_designation[team_index]+'_max']) * float(team[team_designation[team_index]+'_inning']) / float(self.gameData['status']['inning']) * min(1, INNING_RUN_PERCENT_THRESHOLD / float(team[team_designation[team_index]+'_max'])) * min(1, INNING_RUN_TOTAL_THRESHOLD / team[team_designation[team_index]+'_value']) * INNING_RUN_MAX_WEIGHT
			#If they lose, inflict a weight penalty
			if self.winning_team != team_designation[team_index]:
				weight = weight / float(self.gameData['linescore']['r']['diff']) * INNING_RUN_LOSS_MULTIPLIER

			#Crazy stuff to print ordinal numbers
			runs = int(team[team_designation[team_index]+'_value'])
			k = runs%10
			team_desc = "scored %s runs in the %s%s inning" % (team_names[team_index]), runs, "%d%s"%(runs,"tsnrhtdd"[(runs/10%10!=1)*(k<4)*k::4])
			team_index += 1

			#adds the new a event to the event list
			events.append(event(team_desc, weight,self.winning_team))

		return events

	def build_walks_events(self, walks_metrics):
		None

	def build_pitching_change_events(self, pitching_metrics):
		team_types = ["away", "home"]
		events = []

		for key in team_types:
			if pitching_metrics["first_sub_" + key] >= IMPRESSIVE_AMOUNT_OF_INNINGS_PITCHED:

				this_team_won = (self.winning_team == key)

				pitcher_name = pitching_metrics["name_" + key]
				strikeouts = pitching_metrics["strikeouts_" + key]
				innings = pitching_metrics["first_sub_" + key]

				pitcher_blurb = "%s pitched %s strikeouts in %s innings." % (pitcher_name, strikeouts, innings)
				event_weight = STAR_PITCHER_BASE_WEIGHT + (0.15 * strikeouts)

				events.append(event(pitcher_blurb, event_weight, this_team_won))

		return events

	def build_batting_average_events(self, batting_metrics):
		None

	def build_lead_change_events(self, lead_metrics):
		None

	def build_rbi_events(self, rbi_metrics):
		None

