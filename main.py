# mypy: disable-error-code="import-untyped"

import json
import os
from datetime import datetime, timedelta

import functions_framework
import pytz
from flask import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@functions_framework.http
def main(request: Request) -> str:
    data = json.loads(request.data)

    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )

    try:
        service = build(
            "calendar", "v3", credentials=credentials, cache_discovery=False
        )

        tz_info = pytz.timezone(os.environ["TZ"])
        today = datetime.today().astimezone(tz_info)

        timeMin = datetime.combine(today, datetime.min.time())
        timeMax = datetime.combine(today, datetime.max.time())

        if data and "timedelta" in data:
            match data["timedelta"]:
                case {"days": float}:
                    timeMax += timedelta(days=data["timedelta"]["days"])
                case {"weeks": float}:
                    timeMax += timedelta(weeks=data["timedelta"]["weeks"])

        events_list = (
            service.events()
            .list(
                calendarId=os.environ["PRIMARY_CALENDAR_EMAIL"],
                timeMin=timeMin.isoformat(),
                timeMax=timeMax.isoformat(),
                singleEvents=True,
                orderBy="startTime",
                # additional available fields:
                # maxResults=2500,
                # ^ The page size can never be larger than 2500 events. Optional.
                # q="string search terms",
                # ^ Free text search terms to find events that match these terms in the following fields:
                #   summary, description, location, attendee's displayName, attendee's email. Optional.
            )
            .execute()
        )

        events = events_list.get("items", [])

        if not events:
            return "No upcoming events found."

        for event in events:
            start = datetime.fromisoformat(event["start"]["dateTime"])
            end = datetime.fromisoformat(event["end"]["dateTime"])
            title = event["summary"]

            # do something with events...
            print("%s - %s: %s" % (start, end, title))

        return "Done."

    except HttpError as e:
        return "An error occurred: %s" % e
