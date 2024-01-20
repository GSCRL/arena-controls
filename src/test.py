import logging

from config import settings as arena_settings
from truefinals_api.wrapper import TrueFinals

logging.basicConfig(level="INFO")


q = TrueFinals()
test = q.getAllMatches("68d77a7eae4e49bf").withoutByes().toFile("./test.json")
print(type(test))
