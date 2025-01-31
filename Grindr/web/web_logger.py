import json
import time
import typing
from pathlib import Path
from typing import TypedDict, Any

import curl_cffi.requests

if typing.TYPE_CHECKING:
    from Grindr.web.web_client import GrindrWebClientAuthSession


class GrindrHTTPLogRequest(TypedDict):
    id: int
    method: str
    url: str
    params: dict
    headers: dict
    kwargs: dict


class GrindrHTTPLogResponse(TypedDict):
    status_code: int
    content: str
    headers: dict
    cookies: dict
    elapsed: float


class GrindrHTTPLog(TypedDict):
    request: GrindrHTTPLogRequest
    response: GrindrHTTPLogResponse


class GrindrWebFileLogger:

    def __init__(
            self,
            log_dir: Path,
            web_session: "GrindrWebClientAuthSession"
    ):
        self._log_dir: Path = log_dir
        self._request_id: int = 0
        self._create_time = time.strftime("%d_%m_%Y-%H_%M_%S")
        self._web_session = web_session

        # Set up the base directory
        base_request_dir = Path(self._log_dir)
        if not base_request_dir.exists():
            base_request_dir.mkdir()

    def log(
            self,
            response: curl_cffi.requests.Response,
            headers: dict[str, str],
            params: dict[str, str],
            kwargs: dict[str, Any]
    ) -> None:
        entry: GrindrHTTPLog = {
            "request": {
                "id": self._request_id,
                "method": response.request.method,
                "url": response.request.url,
                "params": params,
                "headers": dict(headers.items()),
                "kwargs": {k: v for k, v in kwargs.items() if k != 'content'}  # Exclude binary content
            },
            "response": {
                "status_code": response.status_code,
                "content": response.content.decode("utf-8", errors="replace"),
                "headers": dict(response.headers.items()),
                "cookies": dict(response.cookies.items()),
                "elapsed": response.elapsed
            }
        }

        profile_request_dir = self._log_dir.joinpath(f'./{self._web_session.session_data.profile_id if self._web_session.session_data else 'anonymous'}')
        if not profile_request_dir.exists():
            profile_request_dir.mkdir()

        # Request file path
        request_fp = profile_request_dir.joinpath(f'./{self._create_time}.json')
        if not request_fp.exists():
            with open(request_fp, "w") as f:
                f.write("[]")

        # Write the new data
        with open(request_fp, "r+") as f:
            file_data = json.load(f)
            file_data.append(entry)
            f.seek(0)
            f.write(json.dumps(file_data, indent=2))
            f.truncate()

        self._request_id += 1
