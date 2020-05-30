import json
import time

import requests
from apollo.Scraper.config import (
    USER_AGENT,
    YOUTUBE_COMMENTS_AJAX_URL_NEW,
    YOUTUBE_COMMENTS_AJAX_URL_OLD,
    YOUTUBE_VIDEO_URL,
)
from apollo.Scraper.extract import extract_comments, extract_reply_cids
from apollo.Scraper.helper import ajax_request, find_value, search_dict


def download_comments(youtube_id, sleep=0.1):
    if (
        "liveStreamability"
        in requests.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id)).text
    ):
        print("Live stream detected! Not all comments may be downloaded.")
        return download_comments_new_api(youtube_id, sleep)
    return download_comments_old_api(youtube_id, sleep)


def download_comments_new_api(youtube_id, sleep=1):
    # Use the new youtube API to download some comments
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
    print("Printing response", response)
    html = response.text
    session_token = find_value(html, "XSRF_TOKEN", 3)

    data = json.loads(
        find_value(html, 'window["ytInitialData"] = ', 0, "\n").rstrip(";")
    )
    ncd = next(search_dict(data, "nextContinuationData"))
    continuations = [(ncd["continuation"], ncd["clickTrackingParams"])]

    while continuations:
        continuation, itct = continuations.pop()
        response = ajax_request(
            session,
            YOUTUBE_COMMENTS_AJAX_URL_NEW,
            params={
                "action_get_comments": 1,
                "pbj": 1,
                "ctoken": continuation,
                "continuation": continuation,
                "itct": itct,
            },
            data={"session_token": session_token},
            headers={
                "X-YouTube-Client-Name": "1",
                "X-YouTube-Client-Version": "2.20200207.03.01",
            },
        )
        if not response:
            break
        if list(search_dict(response, "externalErrorMessage")):
            raise RuntimeError(
                "Error returned from server: "
                + next(search_dict(response, "externalErrorMessage"))
            )

        # Ordering matters. The newest continuations should go first.
        continuations = [
            (ncd["continuation"], ncd["clickTrackingParams"])
            for ncd in search_dict(response, "nextContinuationData")
        ] + continuations

        for comment in search_dict(response, "commentRenderer"):
            yield {
                "id": comment["commentId"],
                "content": "".join([c["text"] for c in comment["contentText"]["runs"]]),
                "time": comment["publishedTimeText"]["runs"][0]["text"],
                "author": comment.get("authorText", {}).get("simpleText", ""),
                "votes": comment.get("voteCount", {}).get("simpleText", "0"),
                "photo": comment["authorThumbnail"]["thumbnails"][-1]["url"],
            }

        time.sleep(sleep)


def download_comments_old_api(youtube_id, sleep=1):
    # Use the old youtube API to download all comments (does not work for live streams)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    # Get Youtube page with initial comments
    response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
    html = response.text

    reply_cids = extract_reply_cids(html)

    ret_cids = []
    for comment in extract_comments(html):
        ret_cids.append(comment["id"])
        yield comment

    page_token = find_value(html, "data-token")
    session_token = find_value(html, "XSRF_TOKEN", 3)

    first_iteration = True

    # Get remaining comments (the same as pressing the 'Show more' button)
    while page_token:
        data = {"video_id": youtube_id, "session_token": session_token}

        params = {
            "action_load_comments": 1,
            "order_by_time": True,
            "filter": youtube_id,
        }

        if first_iteration:
            params["order_menu"] = True
        else:
            data["page_token"] = page_token

        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_OLD, params, data)
        if not response:
            break

        page_token, html = response.get("page_token", None), response["html_content"]

        reply_cids += extract_reply_cids(html)
        for comment in extract_comments(html):
            if comment["id"] not in ret_cids:
                ret_cids.append(comment["id"])
                yield comment

        first_iteration = False
        time.sleep(sleep)

    # Get replies (the same as pressing the 'View all X replies' link)
    for cid in reply_cids:
        data = {
            "comment_id": cid,
            "video_id": youtube_id,
            "can_reply": 1,
            "session_token": session_token,
        }

        params = {
            "action_load_replies": 1,
            "order_by_time": True,
            "filter": youtube_id,
            "tab": "inbox",
        }

        response = ajax_request(session, YOUTUBE_COMMENTS_AJAX_URL_OLD, params, data)
        if not response:
            break

        html = response["html_content"]

        for comment in extract_comments(html):
            if comment["id"] not in ret_cids:
                ret_cids.append(comment["id"])
                yield comment
        time.sleep(sleep)
