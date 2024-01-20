import logging

from truefinals_api.wrapper import TrueFinals

logging.basicConfig(level="INFO")


tf = TrueFinals()
event1 = tf.getAllMatches("68d77a7eae4e49bf", weightclass="Plastic Ant")
event2 = tf.getAllMatches("e0b2a154ac3e44f4", weightclass="Ants")

combined = (
    event1.extend(event2)
    .withoutByes()
    .withFilter(lambda x: x["state"] == "done")
    .toFile("test.json")
)
