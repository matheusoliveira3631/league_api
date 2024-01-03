from threading import ThreadError
from mysql import connector
from mysql.connector import cursor

from .config import Config;
from .data import ChampionData;



class DataBase:
	def __init__(self, db_name) -> None:
		creds : dict = Config.getCredentials();
		self.conn = connector.connect(**creds);
		self.cursor : cursor.MySQLCursor = self.conn.cursor();
		self.InitialSetup(db_name);		

		return

	def InitialSetup(self, db_name) -> None:
		#done if this is the first ever the code runs
		#creates database, tables and populate them
		self.createDatabase(db_name);
		self.populateDatabase();
		self.conn.commit();

	
	def createDatabase(self,db_name):
		createDb : str = f"CREATE DATABASE IF NOT EXISTS {db_name}";

		try:
			self.cursor.execute(createDb);
			self.conn.database=db_name;
		except Exception:
			raise Exception

		createTable : str = '''CREATE TABLE IF NOT EXISTS champion_bans (
							    champion_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
							    name VARCHAR(20),
							    id INT NOT NULL,
							    total_bans INT NOT NULL
							    );'''

		try:
			self.cursor.execute(createTable);
		except Exception:
			raise Exception;

	def populateDatabase(self) -> None:
		self.cursor.execute("SELECT COUNT(*) FROM champion_bans");
		result = self.cursor.fetchone();
		if result[0]>0:
			return;
		else:
			championDataTuples : list = ChampionData.getChampions();
			query:str="INSERT INTO champion_bans (name, id,total_bans) values (%s, %s, %s)";

			self.cursor.executemany(query, championDataTuples);

	def increaseBans(self,champion_id, qtd):
		query=f'''
			UPDATE champion_bans
			SET total_bans = total_bans + {qtd} 
			WHERE id = {champion_id};
			'''

		self.cursor.execute(query);
		self.conn.commit();


	


