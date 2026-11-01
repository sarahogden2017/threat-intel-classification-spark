import feedparser

FEED = "https://www.bleepingcomputer.com/feed/"

if __name__ == "__main__":
    feed = feedparser.parse(FEED)

    print(feed.bozo)
    print(feed.feed.title)

    for entry in feed.entries:
        print(entry.title)
        print(entry.link)