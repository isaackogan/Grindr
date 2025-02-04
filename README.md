Grindr
==================
A silly little library to connect to Grindr's mobile services.

![Stars](https://img.shields.io/github/stars/isaackogan/Grindr?style=flat&color=0274b5)
![Forks](https://img.shields.io/github/forks/isaackogan/Grindr?style=flat&color=0274b5)
![Downloads](https://pepy.tech/badge/Grindr)
![Issues](https://img.shields.io/github/issues/isaackogan/Grindr)

## If You Work at Grindr

- Don't sue me
- Send me a message `info@isaackogan.com` for any questions/concerns.
- If you are hiring, send an e-mail. Let's chat :)!

## Table of Contents

- [Getting Started](#getting-started)
- [Licensing](#license)
- [Contributors](#contributors)
- [Usage Guide](#usage-guide)
- [Examples](#examples)

## Project Structure

1. `Grindr.web` - A standalone HTTP client for interacting with Grindr's REST services
2. `Grindr.ws` - A standalone WS client for interacting with Grindr's WebSocket services
3. `Grindr.client` - A high-level abstraction for interacting with Grindr's services (WS and REST)

## Getting Started

1. Install the module via pip from the [PyPi](https://pypi.org/project/Grindr/) repository

```shell script
pip install Grindr
```

2. Create your first chat connection

```python
from Grindr import GrindrClient
from Grindr.ws.events.events import ConnectEvent, MessageEvent

# Create the client
client: GrindrClient = GrindrClient()


# Listen to an event with a decorator!
@client.on(ConnectEvent)
async def on_connect(_: ConnectEvent):
    print(f"Connected to Grindr!")


# Or, add it manually via "client.add_listener()"
async def on_message(event: MessageEvent) -> None:
    if not event.type == "Text":
        return

    print(f"{event.senderId} -> {event.body.text}")


client.add_listener(MessageEvent, on_message)

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client.run(
        email="your@email.com",
        password="your_secure_password"
    )
```

### Helpful Tips

- Access all web-scraping methods with `client.web`
- Send messages with `await client.send(...)`
- Use proxies. Cloudflare WAF likes to ban IPs.

## Usage Guide

This section provides a comprehensive guide on how to use the code.

### Initializing GrindrClient with User Credentials

To initialize the `GrindrClient` with user credentials, you can use the following code:

```python
from Grindr import GrindrClient

client = GrindrClient()
client.login(email="your_email@example.com", password="your_password")
```

### Fetching Data

To fetch data using the `GrindrWebClient`, you can use the following code:

```python
from Grindr.web.web_client import GrindrWebClient

web_client = GrindrWebClient()
data = web_client.fetch_data(route="your_route", params={"param1": "value1"})
print(data)
```

### Setting Data

To set data using the `GrindrWebClient`, you can use the following code:

```python
from Grindr.web.web_client import GrindrWebClient

web_client = GrindrWebClient()
response = web_client.set_data(route="your_route", body={"key": "value"})
print(response)
```

## Examples

This section provides examples for common use cases.

### Example 1: Calculating User Density

The `examples/density.py` script calculates the density of Grindr users at a given location. It includes proper documentation, error handling, and a command-line interface to accept latitude, longitude, and distance.

```python
import asyncio
import os
import argparse
from Grindr import GrindrClient

client = GrindrClient()

async def run_client(lat, lon, kms):
    try:
        email = os.environ['G_EMAIL']
        password = os.environ['G_PASSWORD']
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        return

    await client.login(email=email, password=password)
    density, measure_distance, measured_profiles = await get_density(lat, lon, kms=kms)
    print(f"Measured a user density of {density:.2f} users per square kilometer over {measure_distance:.2f} km with a total of {measured_profiles} users.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate Grindr user density at a given location.")
    parser.add_argument("latitude", type=float, help="Latitude of the location")
    parser.add_argument("longitude", type=float, help="Longitude of the location")
    parser.add_argument("distance", type=int, help="Distance in kilometers to measure")

    args = parser.parse_args()
    asyncio.run(run_client(args.latitude, args.longitude, args.distance))
```

### Example 2: Fetching User Profiles

To fetch user profiles, you can use the following code:

```python
from Grindr import GrindrClient

client = GrindrClient()

async def fetch_profiles():
    await client.login(email="your_email@example.com", password="your_password")
    profiles = await client.web.fetch_profiles()
    for profile in profiles:
        print(profile)

if __name__ == '__main__':
    asyncio.run(fetch_profiles())
```

## Contributors

* **Isaac Kogan** - *Creator, Primary Maintainer, and Reverse-Engineering* - [isaackogan](https://github.com/isaackogan)

See also the full list of [contributors](https://github.com/isaackogan/Grindr/contributors) who have participated in
this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
