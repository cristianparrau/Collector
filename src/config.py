import configparser
import os


class ConfigManager:

  def __init__(self, filepath="config.ini"):
    self.filepath = filepath
    self.config = configparser.ConfigParser()
    self.load_config()

  def load_config(self):
    if os.path.exists(self.filepath):
      self.config.read(self.filepath)
    else:
      self.config["DEFAULT"] = {
          "api_url": "https://jsonplaceholder.typicode.com/users",
          "timeout": "10",
          "retries": "3",
          "backoff_factor": "1",
          "output_filename": "usuarios_paginados_procesados.json",
          "max_records": "0",
      }
      self.config["DATABASE"] = {
          "db_url": "postgresql://postgres:postgres@localhost:5432/datacollector_db"
      }

  @property
  def api_url(self):
    return self.config.get(
        "DEFAULT",
        "api_url",
        fallback="https://jsonplaceholder.typicode.com/users",
    )

  @property
  def timeout(self):
    return self.config.getint("DEFAULT", "timeout", fallback=10)

  @property
  def retries(self):
    return self.config.getint("DEFAULT", "retries", fallback=3)

  @property
  def backoff_factor(self):
    return self.config.getint("DEFAULT", "backoff_factor", fallback=1)

  @property
  def max_records(self):
    return self.config.getint("DEFAULT", "max_records", fallback=0)

  @property
  def output_filename(self):
    return self.config.get(
        "DEFAULT",
        "output_filename",
        fallback="usuarios_paginados_procesados.json",
    )