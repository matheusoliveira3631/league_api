from dotenv import load_dotenv; load_dotenv();

import os;

MYSQL_HOST = os.getenv("MYSQL_HOST");
MYSQL_USER = os.getenv("MYSQL_USER");
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD");

class Config:
  class MissingNameException(Exception):
      def __init__(self, message):
          super().__init__(message)

  apiException = MissingNameException;

  def __init__(self):
    pass

  @staticmethod
  def getCredentials():
    return {
      'host':MYSQL_HOST,
      'user':MYSQL_USER,
      'password':MYSQL_PASSWORD
    }