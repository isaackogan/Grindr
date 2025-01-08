try:
    from .client.web.tls_patch import tls_patch
except:
    raise
finally:
    from .client.client import GrindrClient
