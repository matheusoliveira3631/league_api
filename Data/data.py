import requests

class ChampionData:
	def __init__(self) -> None:
		#self.DDragonData=requests.get("https://ddragon.leagueoflegends.com/cdn/13.24.1/data/en_US/champion.json").json()['data'];
		pass

	@staticmethod
	def getChampions(detailed=False) -> list:
		data:list=[];
		request=requests.get("https://ddragon.leagueoflegends.com/cdn/13.24.1/data/en_US/champion.json").json()['data'];

		if detailed: return request;

		names = list(request.keys());
		for name in names:
			data.append((name, request[name]['key'],0));

		return data;