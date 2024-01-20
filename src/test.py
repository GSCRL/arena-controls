import logging

from truefinals_api.wrapper import TrueFinals

logging.basicConfig(level="INFO")


q = TrueFinals()
event1 = q.getAllMatches("68d77a7eae4e49bf")
event2 = q.getAllMatches("e0b2a154ac3e44f4")

combined = (
    event1.extends(event2)
    .withoutByes()
    .withFilter(lambda x: x["state"] == "done")
    .toFile("test.json")
)
