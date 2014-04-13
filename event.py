""" Describes an event. """

class Event:
	def __init__(self, description, weight, team_name, event_type, event_owner, teaser, is_homerun, number_hrs, team_won=None):
		self.description = description
		self.weight = weight
		self.team_name = team_name
		self.team_won = team_won
		self.event_type = event_type
		self.event_owner = event_owner
		self.teaser = teaser
		self.is_homerun = is_homerun
		self.number_hrs = number_hrs

	def __str__(self):
		#return "The " + self.team_name + " " + self.description + "."
		if self.event_type <= 1:
			return self.team_name + " " + self.description + "."
		else:
			return self.description + "."