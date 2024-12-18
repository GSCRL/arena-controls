import logging

# Text type is VarChar without limit, probably fine?
from time import time

from piccolo.columns import JSON, UUID, BigInt, Boolean, Text
from piccolo.engine.sqlite import SQLiteEngine

# ORM Test, ty Devyn.
from piccolo.table import Table

from truefinals_api.api import makeAPIRequest

lru_DB = SQLiteEngine(path="tf_lru.sqlite")

"""
The true ratelimit of TrueFinals is 10 requests in 10 seconds, 
unsure of interval of observation.  However, this neglects the
 reality that the web frontend ALSO counts towards this reque-
 st limit.  
 
As such, our limit is half of the rated one by default, and as 
well is accomodating of the need for some requests that may 
not be done yet, and or still result in rate-limiting.

TrueFinals also returns the rate limit information in headers like so:

X-RateLimit-Limit: Maximum number of requests allowed within a window (10s).
X-RateLimit-Remaining: How many requests the user has left within the current window.
X-RateLimit-Reset: Unix timestamp in milliseconds when the limits are reset.

They are stored below, so we should look for the last response overall to 
validate rate limiting, and remove ones past their expiry most likely, 
rather than keeping them in perpetuity.

"""


def are_rate_limited() -> bool:
    requests_thing = (
        TrueFinalsAPICache.select()
        .where((time() - 10) > TrueFinalsAPICache.last_requested)
        .run_sync()
    )
    if (
        len(requests_thing) >= 5
    ):  # half of calls can be API due to web panel causing headaches.
        return True
    return False


class TrueFinalsAPICache(Table, db=lru_DB):
    id = UUID(primary_key=True)
    response = JSON()
    last_requested = BigInt()
    api_path = Text()
    successful = Boolean()
    resp_code = BigInt()
    resp_headers = JSON()


# Need to assert that the table exists first, or else it fails horridly.
TrueFinalsAPICache.create_table(if_not_exists=True).run_sync()


def getAPIEndpointRespectfully(api_endpoint: str, expiry=60):
    logging.info(f"expiry is {expiry} while calling {api_endpoint}")

    find_response = (
        TrueFinalsAPICache.select(
            TrueFinalsAPICache.api_path,
            TrueFinalsAPICache.last_requested,
            TrueFinalsAPICache.response,
            TrueFinalsAPICache.resp_code,
        )
        .where(TrueFinalsAPICache.api_path == api_endpoint)
        .where(TrueFinalsAPICache.successful == True)
        .where((TrueFinalsAPICache.last_requested + expiry > time()))
        .order_by(TrueFinalsAPICache.last_requested, ascending=False)
    )

    find_response = find_response.run_sync()

    # Key is not present.
    if len(find_response) == 0:
        print(f"No valid keys, adding new request for {api_endpoint}")
        query_remote = makeAPIRequest(api_endpoint)
        # print(query_remote.headers)
        insert_query = TrueFinalsAPICache.insert(
            TrueFinalsAPICache(
                response=query_remote.json(),
                successful=(
                    (query_remote.status_code >= 200)
                    and (query_remote.status_code < 500)
                ),
                last_requested=time(),
                api_path=api_endpoint,
                resp_code=query_remote.status_code,
                resp_headers=query_remote.headers,
            )
        ).run_sync()

        TrueFinalsAPICache.update(force=True)
        # save_query = TrueFinalsAPICache.select().limit(1).run_sync()
        # save_query.save()
    else:
        logging.info(f"Valid keys found, not requesting {api_endpoint}.")


# Below are the stubs we hope to use to use the above APICache antics we've made.

# They are rough analogues to the original as made in api.py, and should be used
# instead whenever possible, as the originals may be deprecate at any point.  The
# below functions are "synthetic view" functions, where it uses the most up to date
# version of any endpoint, but also tries to get the new result if it doesn't exist.
# If there's truly no version inside of it, we should probably just... block until
# we'll become unblocked I guess.

# That's a long ten seconds.


def getEventInformation(tournamentID: str) -> dict:
    return getAPIEndpointRespectfully(f"/v1/tournaments/{tournamentID}")


def getAllGames(tournamentID: str) -> list[dict]:
    return getAPIEndpointRespectfully(
        f"/v1/tournaments/{tournamentID}/games", expiry=30
    )


def getAllPlayersInTournament(tournamentID: str) -> list[dict]:
    return getAPIEndpointRespectfully(
        f"/v1/tournaments/{tournamentID}/players", expiry=(5 * 60)
    )


def getEventLocations(tournamentID: str) -> list[dict]:
    return getAPIEndpointRespectfully(
        f"/v1/tournaments/{tournamentID}/locations", expiry=(60 * 60)
    )


# DO NOT USE LIGHTLY.  THIS EMPTIES THE FILE.
def purge_API_Cache(timer_passed=3600):
    TrueFinalsAPICache.delete().where(
        (TrueFinalsAPICache.last_requested + timer_passed < time())
    ).run_sync()
