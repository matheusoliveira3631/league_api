from re import match
import datetime
import time
from dotenv import load_dotenv; load_dotenv();


import os;
import threading;

import requests;
from colorama import Fore;
from colorama import Style;

from .config import Config;


	

class ApiCaller:
	def __init__(self) -> None:
		self.API_KEY = os.getenv("RIOT_API_KEY");
		self.SPARE_KEY=os.getenv("SPARE_API_KEY");

		self.current_key = self.API_KEY;
		self.current_key_name = "Main";
		self.last_key_swap = datetime.datetime.now();
		self.match_list:list=[];

	def apiCall(self, uri:str, *customRoute,**params):
		
		baseUrl:str="https://br1.api.riotgames.com";
		headers:dict = {
		    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
		    "X-Riot-Token": self.current_key,
		}
		if(uri[0]!="/"):
			uri=f"/{uri}";
		if(customRoute):
			route=customRoute[0]+uri;
		else:
			route = baseUrl+uri;
		if(len(params)>0):
			route+="?";
			n=1;
			for param in params:
				route+=f"{param}={params[param]}"
				if n!=len(params):
					route+="&";
					n+=1;
		
		try:
			response = requests.get(route, headers=headers);
			if(response.status_code==429):
				raise Config.KeyLimitException();
		except Config.KeyLimitException:
			self.switchKeys();
			headers["X-Riot-Token"]=self.current_key;
			response = requests.get(route, headers=headers);


		#logging
		status=response.status_code
		if(status!=200):
			print(Fore.YELLOW + f"{self.current_key_name}: " + Fore.RED + f"URI: {uri} returned status code {response.status_code}" + Style.RESET_ALL)
		else:
			print(Fore.YELLOW + f"{self.current_key_name}: " + Fore.GREEN + f"URI: {uri} returned status code {response.status_code}" +Style.RESET_ALL)
		return response.json();

	def getRotationChampions(self):
		return self.apiCall("/lol/platform/v3/champion-rotations")["freeChampionIds"]

	def getSummonerData(self,summonerId:str) ->dict:
		return self.apiCall(f"/lol/summoner/v4/summoners/{summonerId}");


	def getTopSummoners(self, count=0) ->list:
		data:dict = self.apiCall("lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I", page=1);
		if count > 0:
			data = data[0:count]

		return [x["summonerId"] for x in data];


	def getPlayerMatches(self, puuid:str) ->None:
		for match in self.apiCall(f"/lol/match/v5/matches/by-puuid/{puuid}/ids","https://americas.api.riotgames.com", queue=420, start=0, count=20):
			self.match_list.append(match);

		return

	def getMatchBans(self, matchId:str) ->list:
		matchData:dict =self.apiCall(f"/lol/match/v5/matches/{matchId}", "https://americas.api.riotgames.com");
		teams:list = matchData['info']['teams'];
		bans:list=[];
		for i in teams:
			for ban in i["bans"]:
				bans.append(ban["championId"]);

		return [i for i in bans if i!=-1];

	
	def getBannedChampions(self) ->dict:
		playerIds:list = self.getTopSummoners();
		self.log(f"Fetched a total of {len(playerIds)} players");

		for player in playerIds:
			puuid = self.getSummonerData(player)["puuid"]
			self.getPlayerMatches(puuid);

		self.log(f"Fetched a total of {len(self.match_list)} matches")
		idList:list=[];
		idMap:dict={};

		
		self.threadedCalls(self.match_list, idList);

		#self.log(f"Parsed an amount of {n} matches")

		for i in idList:
			try:
				idMap[i]+=1;
			except:
				idMap[i]=1;

		return idMap;

	def switchKeys(self):
		time_delta = datetime.datetime.now() - self.last_key_swap;
		swap_seconds = time_delta.total_seconds();
		self.log(f"Time since last swap: {swap_seconds} seconds");
		if swap_seconds > 10:
			if swap_seconds<120:
				time.sleep(120-swap_seconds);
			self.log("API key Rate limit exceeded, switching keys");
			self.current_key = self.SPARE_KEY if self.current_key == self.API_KEY else self.API_KEY;
			self.current_key_name = "Spare" if self.current_key_name =="Main" else "Main"
			self.last_key_swap = datetime.datetime.now();
			return
		else:
			return

	def threadedCalls(self, matchIds:list, callBackList:list)->None:
		callList:list=[];
		chunk_size:int=int(len(matchIds)/3);
		while len(matchIds)>=chunk_size:
			l=[];
			for i in range(chunk_size):
				l.append(matchIds[-1]);
				matchIds.pop();
			callList.append(l);

		#insert remaining items
		if len(matchIds)>0:
			for i in range(len(matchIds)):
				callList[i].append(matchIds[i]);

		threads:list=[];
		for i in range(3):
			thread = threading.Thread(target=self.bulkCalls, args=(callList[i],callBackList,));
			threads.append(thread);
			thread.start();

		for thread in threads:
			thread.join();

		return;

		
	
	def bulkCalls(self, matchIds:list, l:list)->None:
		for mId in matchIds:
			m:list=self.getMatchBans(mId);
			for i in m:
				l.append(i);
			

	def log(self, msg):
		print(Fore.BLUE + msg + Style.RESET_ALL);

