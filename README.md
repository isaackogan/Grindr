Grindr
==================
A silly little library to connect to Grindr's mobile services.

![Stars](https://img.shields.io/github/stars/isaackogan/Grindr?style=flat&color=0274b5)
![Forks](https://img.shields.io/github/forks/isaackogan/Grindr?style=flat&color=0274b5)
![Issues](https://img.shields.io/github/issues/isaackogan/Grindr)

## If You Work at Grindr

- Send me a message `info@isaackogan.com` for any questions/concerns.
- If you are hiring, send an e-mail. Let's chat :)!


## Table of Contents

- [Getting Started](#getting-started)
- [Licensing](#license)
- [Contributors](#contributors)

## Getting Started

1. Install the module via pip from the [PyPi](https://pypi.org/project/Grindr/) repository

```shell script
pip install Grindr
```

2. Create your first chat connection

```python
from Grindr import GrindrClient
from Grindr.events import ConnectEvent, MessageEvent

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

## Contributors

* **Isaac Kogan** - *Creator, Primary Maintainer, and Reverse-Engineering* - [isaackogan](https://github.com/isaackogan)

See also the full list of [contributors](https://github.com/isaackogan/Grindr/contributors) who have participated in
this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
