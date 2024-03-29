#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import requests
import sys
from collections import Counter
from pathlib import Path

# just a horizontal line
HLINE = """
********************************************************
"""

HTML_HEAD = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Mastodon archive</title>
    <style>
       div {
          padding: 20px;
      }
      .img_desc {
          background-color: lightblue;
      }
      .boost {
          background-color: lightgreen;
      }
    </style>
  </head>

<body>
<hr/>
"""

HTML_FOOT = """
</body>
</html>
"""


def analyze_archive(tl):
    
    print("""
    ┌──────────────────────────────┐
    │   Mastodon archive summary   │
    └──────────────────────────────┘
    """)
    
    # ### TOOTS ###
    
    posttype, to, inreplyto, boostedusers, year, tags = [], [], [], [], [], []
    import_list = []
    orph_counter, tagged_posts = 0, 0
    vanished_users, broken_conversations = [], []
    media_type, media_desc = [], []
    
    for value in tl:
        try:
            # Create = toot or Announce = boost
            posttype.append(value["type"])
            # user name list of boosts
            if value["type"] == "Announce":
                boostedusers.append(value["cc"][0])
            # public posts, followers only posts, direct messages
            if value["object"]["to"][0].endswith("#Public"):
                to.append("public")
            elif value["object"]["to"][0].endswith("/followers"):
                to.append("followers only")
            else:
                to.append("direct message")
            # original toots and replies
            if value["object"]["inReplyTo"] is None:
                inreplyto.append(None)
            else:
                # only add user name
                inreplyto.append(
                    value["object"]["inReplyTo"].split("/statuses")[0])
            # publishing year, first 4 characters of publishing date
            year.append(value["published"][:4])
            # hashtags
            for tag in value["object"]["tag"]:
                if tag["type"] == "Hashtag":
                    tags.append(tag["name"])
                    tagged_posts += 1
    
            if value["type"] == "Create" and value["object"]["inReplyTo"] is None:
                # count orphaned replies
                _firstline = value["object"]["content"].split("</p>")[0][3:]
                # post starts with addressing user by leading @ 
                # not hyperlinked
                if _firstline.startswith("@"):
                    orph_counter += 1
                    vanished_users.append(_firstline.split()[0])
                # hyperlinked
                elif _firstline.startswith("<span class=\"h-card\"><a href=") \
                        and "class=\"u-url mention\">@<span>" in _firstline:
                    orph_counter += 1
                    broken_conversations.append(_firstline.split("\"")[3])
    
            for attachment in value["object"]["attachment"]:
                media_type.append(attachment["mediaType"])
                media_desc.append(attachment["name"])
    
        except (TypeError, IndexError):
            pass
    
    # number of toots
    print("total number of toots:", len(tl))
    
    # number of boosts
    print("among them boosts:", Counter(posttype)["Announce"])
    
    print(HLINE)
    
    # most boosted users
    print("most boosted users (10)")
    print("~~~~~~~~~~~~~~~~~~~~~~~")
    
    for u, i in Counter(boostedusers).most_common(10):
        print("{:>4}: {}".format(i, u))
    
    print("\nboosted users (total):", len(Counter(boostedusers)))
    
    print(HLINE)
    
    # public posts, follower only posts, direct messages
    print("public posts:", Counter(to)["public"])
    print("followers only posts:", Counter(to)["followers only"])
    print("direct messages:", Counter(to)["direct message"])
    
    print(HLINE)
    
    # original toots and replies
    print("original toots:", Counter(inreplyto)[None])
    print("among them orphaned replies:", orph_counter)
    print("replies:", len(inreplyto) - Counter(inreplyto)[None])
    print("posts with hashtags:", tagged_posts)
    
    print(HLINE)
    
    # remove None values from list
    
    inreplyto = [x for x in inreplyto if x is not None]
    print("most replied profiles (20)")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    for u, i in Counter(inreplyto).most_common(20):
        print("{:>4}: {}".format(i, u))
    
    print("\nreplied users (total):", len(Counter(inreplyto)))
    
    
    print("\nmost replied profiles that are no longer available (20)")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    for u, i in Counter(vanished_users).most_common(20):
        print("{:>4}: {}".format(i, u))
    
    print("\nreplied users (total):", len(Counter(vanished_users)))
    
    print("\nprofiles with broken conversations (20)")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    for u, i in Counter(broken_conversations).most_common(20):
        print("{:>4}: {}".format(i, u))
        
    print("\nreplied users (total):", len(Counter(broken_conversations)))
    
    print(HLINE)
    
    # numbers by year
    print("publishing year")
    print("~~~~~~~~~~~~~~~~")
    
    for key, value in sorted(Counter(year).items()):
        print("{}: {:>5}".format(key, value))
    
    print(HLINE)
    
    # hashtags
    print("popular hashtags (25)")
    print("~~~~~~~~~~~~~~~~~~~~~")
    
    # if #25 is used at the same frequency as others, print all others,
    # e.g. #25 is used four times then print all hashtags used four times 
    
    # get number of shares of 25th most common hashtag
    _, _max = Counter(sorted(tags)).most_common(25)[-1]
    
    for tag, i in Counter(sorted(tags)).most_common():
        if i < _max:
            break
        else:
            print("{:>4}: {}".format(i, tag))
    
    print("\nhashtags (total):", len(Counter(tags)))
    
    print(HLINE)
    
    # ### LIKES ###
    
    with open(os.path.join(archive_path,
                           "likes.json",
                           )) as f:
        data = json.load(f)
    
    likes = data["orderedItems"]
    
    fedi = []
    masto_users = []
    
    for i in likes:
        if i.startswith("tag") or i.startswith("urn"):
            fedi.append("unknown (vanished posts)")
        elif "/users/" in i:
            fedi.append("Mastodon")
            masto_users.append(i.split("/statuses")[0])
        elif "/p/" in i:
            fedi.append("Pixelfed")
        elif "/objects/" in i:
            fedi.append("Pleroma")
        elif "/item/" in i:
            fedi.append("Hubzilla")
        elif "/videos/" in i:
            fedi.append("PeerTube")
        elif "/notes/" in i:
            fedi.append("Misskey")
        else:
            fedi.append("unknown ({})".format(i))
    
    print("likes")
    print("~~~~~")
    
    # number of likes
    print("total:", len(likes))
    
    # count by platform
    print("liked posts by platform:")
    
    for platform, i in Counter(fedi).most_common():
        print("{:>6}: {}".format(i, platform))
    
    print(HLINE)
    
    # most liked Mastodon profiles
    print("most liked Mastodon profiles (50)")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    for profile, i in Counter(masto_users).most_common(50):
        print("{:>4}: {}".format(i, profile))
    
    print("\nliked profiles (total):", len(Counter(masto_users)))
    
    print(HLINE)
    
    # ### MEDIA ATTACHMENTS ###
    
    print("media attachments")
    print("~~~~~~~~~~~~~~~~~")
    
    print("files (total):", len(media_type))
    print("without description:", Counter(media_desc)[None])
    print("media files by type:")
    
    for t, i in Counter(media_type).most_common():
        print("{:>5}: {}".format(i, t))
    
    print(HLINE)
    
    # ######## check which users are still available ######## 
    
    while True:
        q = input(
            "Do you want to check if your most frequently boosted profiles (50) "
            "are currently up? This may take a while... (y/N)> ")
        if q == "y":
            status = []
            for url, _ in Counter(boostedusers).most_common(50):
                try:
                    status.append(requests.head(url).status_code)
                except requests.exceptions.SSLError:
                    status.append("SSL error")
                except requests.exceptions.ConnectionError:
                    status.append("connection error")
                print(url, status[-1])
            print("number of different profiles boosted:", len(status),
                  "of which are:")
            print(Counter(status)[200] + Counter(status)[302], "available")
            print(
                Counter(status)["SSL error"] + Counter(status)["connection error"],
                "currently not available")
            print(Counter(status)[404], "no more existing")
            break
        else:
            print("That's a 'no'.")
            break
    
    print(HLINE)
    
    while True:
        q = input(
            "Do you want to check if your most replied Mastodon profiles (50) "
            "are currently up? This may take a while... (y/N)> ")
        if q == "y":
            status = []
            for url, _ in Counter(inreplyto).most_common(50):
                try:
                    status.append(requests.head(url).status_code)
                except requests.exceptions.SSLError:
                    status.append("SSL error")
                except requests.exceptions.ConnectionError:
                    status.append("connection error")
                print(url, status[-1])
            print("number of different profiles checked:", len(status),
                  "of which are:")
            print(Counter(status)[200] + Counter(status)[302], "available")
            print(
                Counter(status)["SSL error"] + Counter(status)["connection error"],
                "currently not available")
            print(Counter(status)[404], "no more existing")
            break
        else:
            print("OK then we are done here. Bye.")
            break


def generate_HTML(tl, src, boost):

    output = HTML_HEAD
    for value in tl:

        try:
            if value["type"] == "Announce":
                # add link to boosted post (optional)
                if boost:
                    _author = value["cc"][0].split("/")[-1]
                    output += f"""<div class="boost"><a href="{value["object"]}">Boosted post</a> by <a href="{value["cc"][0]}">{value["cc"][0].split("/")[-1]}</a></div>\n"""
                    output += "<hr/>\n"
            else:
                output += f"""<div>"""
                # add link to original post (optional)
                if src:
                    # remove the letters for better readability
                    # e.g 2022-11-13T21:19:52Z -> 2022-11-1321:19:52
                    _date = value["object"]["published"].replace("T", " ")[:-1]
                    output += f"""<a href="{value["object"]["id"]}">Original</a> {_date}\n"""
                # add post content to output
                output += f"""{value["object"]["content"]}</div>\n"""

                # add media + description
                for attachment in value["object"]["attachment"]:
                    if attachment["mediaType"].startswith("image"):
                        output += f"""<div><img src="{attachment["url"][1:]}" width="600" alt="{attachment["name"]}"></div>\n"""
                    elif attachment["mediaType"].startswith("video"):
                        output += f"""<div><video width="600" controls>
                            <source src="{attachment["url"][1:]}" type="{attachment["mediaType"]}"></video></div>\n"""
                    elif attachment["mediaType"].startswith("audio"):
                        output += f"""<div><audio controls>
                            <source src="{attachment["url"][1:]}" type="{attachment["mediaType"]}"></audio></div>\n"""
                    else:
                        output += f"""<div><i>(error: media attachment is neither image nor video)</i></div>\n"""
                    output += f"""<div class="img_desc">{attachment["name"]}</div>\n"""

                # horizontal line
                output += "<hr/>\n"

        except (TypeError, IndexError):
            #pass
            raise
    
    # end of HTML file
    output += HTML_FOOT
    
    # write file into archive folder
    with open(os.path.join(archive_path,"outbox.html"), "w") as f:
        f.write(output)

# ### SCRIPT STARTS HERE ###

# CLI options
parser = argparse.ArgumentParser(
                    prog="archive2html.py",
                    description="convert Mastodon archive to simple HTML file",
                    )
parser.add_argument("path",
                    help="path to Mastodon archive")
parser.add_argument("-s", "--summary", action="store_true",
                    help="print verbose summary of the archive, other options are ignored")
parser.add_argument("-o", "--original", action="store_true",
                    help="generate link to original post (not shown by default)")
parser.add_argument("-nb", "--noboosts", action="store_false",
                    help="don't list links to boosts (shown by default)")
args = parser.parse_args()

archive_path = Path(args.path)

if not archive_path.exists():
    print("The target directory doesn't exist.")
    raise SystemExit(1)

with open(os.path.join(archive_path,
                       "outbox.json",
                       )) as f:
    data = json.load(f)

if args.summary:
    analyze_archive(data["orderedItems"])
else:
    # args: data, link to original post, show boosts
    generate_HTML(data["orderedItems"],
                  args.original,
                  args.noboosts,
                  )

sys.exit()
