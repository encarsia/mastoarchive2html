## WHAT'S THIS?

This little Python script generates a simple HTML page out of a Mastodon archive (go to *"Edit profile -> Import and Export -> Request archive"*).

Attached videos, audio files and images work as does content in general.

The output is a single HTML page with very little formatting.

## IMPORTANT

This is a simplification of my [Mastodon import plugin](https://github.com/encarsia/import_mastodon) for the Static Site Generator [Nikola](https://getnikola.com). 

You should not publish the results as the page doesn't differentiate between public and private posts and was just written due a community request.

If you intend to publish archived posts I recommend the import plugin mentioned above. The results are much more neat and customizable.

Enjoy.

## USAGE

* request, download and unpack your Mastodon archive
* execute `archive2html.py PATH_TO_ARCHIVE` in a terminal, see available options below
* the output file is saved as `outbox.html` in the archive folder

## OPTIONS
```bash
$ ./archive2html.py -h
usage: archive2html.py [-h] [-s] [-o] [-nb] path

convert Mastodon archive to simple HTML file

positional arguments:
  path             path to Mastodon archive

options:
  -h, --help       show this help message and exit
  -s, --summary    print verbose summary of the archive, other options are ignored
  -o, --original   generate link to original post (not shown by default)
  -nb, --noboosts  don't list links to boosts (shown by default)
```

### -s

* this was a separate script in the original import plugin and analyzes the archive and dumbprints lots of numbers to the console you might be interested in such as
  * overall posts
  * boosted users
  * replied profiles
  * replies to profiles that are no longer available (profiles may be deleted or moved, or are muted/suspended or on muted/suspended instances on your instance)
  * broken conversations (original post of the reply is probably deleted, some users auto-delete old posts so this may probably be a common phenomenon).
  * publishing year
  * hashtags
  * likes
  * media attachments

* the script asks you if you want to check the availability of profiles with the most interactions; this process may take a while as the lookup will be executed just then

* executing the script running this `-s` option will not generate any output file

### -o

* include links to the original posts (if the account is moved or deleted these will be deadlinks, of course)
* shows date and time of post
* is set to *False* by default, use this option to explicitly show this information

### -nb

* contents of boosts are not saved in the archive, only links and authors to the original posts
* is set to *True* by default, use this option to suppress links to boosted posts

## PAGE RESULT
* posts are dumped into a single page starting with the oldest divided by a horizontal line
* images and videos are set to a width of 600px
* the background color of media descriptions is "lightblue"
* the background color of boosts is "lightgreen"
* CWs are ignored, content is displayed just normally
* existing output pages will be overwritten
