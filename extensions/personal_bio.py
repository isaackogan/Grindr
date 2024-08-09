import asyncio
import json
import logging
import re
import traceback
from asyncio import Task
from datetime import datetime

import pytz
from pydantic import Field
from typing import Any

import spotipy
from pydantic import PrivateAttr
from spotipy.oauth2 import SpotifyOAuth

import os

from Grindr.client.extension import Extension
from Grindr.client.web.routes.set_profile_details import SetProfileDetailsRouteBody


class PersonalBioUpdate(Extension):
    CLIENT_ID: str = Field(default_factory=lambda: os.environ["SPOTIFY_CLIENT_ID"])
    CLIENT_SECRET: str = Field(default_factory=lambda: os.environ["SPOTIFY_CLIENT_SECRET"])
    REDIRECT_URI: str = Field(default_factory=lambda: os.environ["SPOTIFY_REDIRECT_URI"])
    TOKEN_FP: str = Field(default_factory=lambda: os.getenv("SPOTIFY_TOKEN_FP", "spotify_token.json"))
    BIO_PATH: str = Field(default_factory=lambda: os.getenv("BIO_PATH", "personal_bio.json"))
    UPDATE_INTERVAL: int = 60

    _spotify: spotipy.Spotify = PrivateAttr()
    _bio: SetProfileDetailsRouteBody = PrivateAttr()
    _update_task: Task = PrivateAttr(default=None)

    def __init__(self, /, **data: Any):
        super().__init__(**data)

        self._spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
                redirect_uri=self.REDIRECT_URI,
                scope="user-read-currently-playing",
                show_dialog=False,
                open_browser=False,
                cache_path=self.TOKEN_FP
            )
        )

        self._bio = SetProfileDetailsRouteBody(**json.loads(open(self.BIO_PATH, "r").read()))
        self._original_about_me = self._bio.aboutMe

    async def on_load(self) -> None:
        self._update_task = asyncio.create_task(self.update_task())

    async def on_unload(self) -> None:
        self._update_task.cancel()
        self._profiles.clear()

    async def get_dynamic_bio(self) -> str:
        currently_playing: dict = await asyncio.to_thread(self._spotify.currently_playing)

        max_line_length: int = 37
        current_artist: str = currently_playing['item']['artists'][0]['name'][:max_line_length] + ("..." if len(currently_playing['item']['artists'][0]['name']) > 20 else "")
        current_song: str = currently_playing['item']['name'][:max_line_length] + ("..." if len(currently_playing['item']['name']) > 20 else "")

        progress_char: str = "⏺️"
        progress_bar: str = "▬" * 11
        progress_percent = currently_playing['progress_ms'] / currently_playing['item']['duration_ms'] * 100
        progress_bar = progress_bar[:int(progress_percent / 8)] + progress_char + progress_bar[int(progress_percent / 8):]

        # Format prograss in format [01:21/06:29]
        progress_time = (
            f"[{currently_playing['progress_ms'] // 60000:02}"
            f":{(currently_playing['progress_ms'] // 1000) % 60:02}"
            f"/{currently_playing['item']['duration_ms'] // 60000:02}"
            f":{(currently_playing['item']['duration_ms'] // 1000) % 60:02}]"
        )

        # Format 8:19PM, do not include leading zero
        current_time_toronto = datetime.now(pytz.timezone('America/Toronto')).strftime('%I:%M%p').lstrip("0")

        dynamic_bio: str = re.sub(
            "money",
            "$$$",
            f"Current Song (Updated {current_time_toronto}):\n\n{current_song} by {current_artist}\n{progress_bar} {progress_time}\n\nMy bio updates every {self.UPDATE_INTERVAL:,} seconds. Yes it's real.",
            flags=re.IGNORECASE
        )

        return dynamic_bio

    async def update_task(self):

        # Update the bio every minute
        while True:
            try:
                self._bio.aboutMe = self._original_about_me + await self.get_dynamic_bio()
                await self.client.web.set_profile_details(body=self._bio)
            except:
                logging.error("Error updating bio! " + traceback.format_exc())

            await asyncio.sleep(60)
