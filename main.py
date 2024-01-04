from colorama import Fore, Style;


from Data import ApiCaller;
from Data import DataBase;
from Data import ChampionData;


class Main:
	def __init__(self) -> None:
		self.db=DataBase("league_api");
		self.api=ApiCaller();


	def setBans(self):
		bans:dict = self.api.getBannedChampions();

		print(Fore.BLUE + "Appending bans to DataBase" + Style.RESET_ALL);
		for champion in bans:
			self.db.increaseBans(champion, bans[champion])

if __name__ == '__main__':
	m=Main();
	m.setBans();