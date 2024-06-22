import asyncio
import math
import os
from typing import Tuple, List

from Grindr import GrindrClient
from Grindr.client.web.routes.fetch_cascade import FetchCascadeRoute, FetchCascadeRouteResponse, FetchCascadeRouteParams

client = GrindrClient()


def calculate_density(distances: List[float]) -> float:
    """
    Calculate the density of users in the grid

    :param distances: The distances of the users
    :return: The density of users in the grid

    """

    max_distance = max(distances)  # Maximum distance from you
    area = math.pi * max_distance ** 2  # Area of the circle with radius equal to max distance
    density = len(distances) / area  # Number of points per unit area

    return density


async def get_density(
        lat: float,
        lon: float,
        kms: int = 30
) -> Tuple[float, float, int]:
    """
    Calculate the density of Grindr users at a given longitude & latitude.
    Output is the # of datapoints per square km.

    :param lat: Target latitude
    :param lon: Target longitude
    :param kms: The distance to stop at. Values above will be discarded
    :return: (Density per square KM, Square KM measured, # of profiles measured)

    """

    current_page: int = 1
    distances: List[float] = []
    checked_profiles: List[float] = []
    distance_reached: bool = False

    while not distance_reached:
        response: FetchCascadeRouteResponse = await client.web.fetch_cascade(
            params=FetchCascadeRouteParams(
                geohash=FetchCascadeRoute.generate_hash(lat, lon),
                pageNumber=current_page
            )
        )

        for profile in response.items:
            if profile.data.profileId in checked_profiles:
                continue

            distance = (profile.data.distanceMeters or 0) / 1000

            # If the distance is greater than the target distance, skip
            # Set distance_reached to True so we don't continue to the next page since we hit our distance
            if distance > kms:
                distance_reached = True
                continue

            checked_profiles.append(profile.data.profileId)
            distances.append(distance)

        current_page += 1

    return calculate_density(distances), max(distances), len(distances)


async def run_client():
    # Target to check
    lat, lon = 43.664334, -79.380432

    # Log into Grindr
    await client.login(email=os.environ['G_EMAIL'], password=os.environ['G_PASSWORD'])

    density, measure_distance, measured_profiles = await get_density(lat, lon, kms=6371)
    print(f"Measured a user density of {density:.2f} users per square kilometer over {measure_distance:.2f} km with a total of {measured_profiles} users.")


if __name__ == '__main__':
    asyncio.run(run_client())
