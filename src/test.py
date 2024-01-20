from truefinals_api.wrapper import TrueFinals

# logging.basicConfig(level="INFO")


tf = TrueFinals()
event1 = tf.getAllMatches("68d77a7eae4e49bf")
event2 = tf.getAllMatches("e0b2a154ac3e44f4")

combined = (
    event1.extends(event2)
    .withoutByes()
    .withFilter(lambda x: x["state"] == "done")
    .toFile("test.json")
)
