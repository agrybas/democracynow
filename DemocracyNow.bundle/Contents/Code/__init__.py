PREFIX = '/video/democracynow'
NAME = 'DemocracyNow!'

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

BASE_URL = 'http://m.democracynow.org'


####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = 'List'

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR


@handler(PREFIX, NAME, ICON, ART)
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(
        key=Callback(EpisodeDates),
        title='Daily Episodes',
        summary='',
        thumb=R('icon-channel.png')))

    return oc


@route('%s/dates' % PREFIX)
def EpisodeDates():
    oc = ObjectContainer(title1='Daily Episodes')
    page = HTML.ElementFromURL(BASE_URL)
    headings = page.xpath("//div[contains(concat(' ', @class, ' '), ' context_header ')]/h2/text()")    
    dates = [Datetime.ParseDate(item) for item in headings]
    Log(dates)

    for date in dates:
        daily_url = '{base}/shows_include/{year}/{month}/{day}'.format(base=BASE_URL, 
            year=date.strftime('%Y'), month=date.strftime('%m'), day=date.strftime('%d'))
        oc.add(DirectoryObject(
            key=Callback(EpisodeList, url=daily_url),
            title=date.strftime('%Y-%m-%d'),
            thumb=R('icon-channel.png')))

    if len(oc) < 1:
        Log('No episodes found')
        return ObjectContainer(header='Empty', message='No episodes available at the moment.')

    return oc


@route('%s/episodes' % PREFIX)
def EpisodeList(url):

    try:
        contents = HTTP.Request(url)
        page = HTML.ElementFromString(contents)
    except:
        return ObjectContainer(header='Empty', message='No episodes available at the moment.')

    oc = ObjectContainer(title1=page.xpath("//div[@class='context_header']/h2/text()")[0])
    items = page.xpath("//li[contains(@class, 'news_item') and contains(@class, 'item_with_video')]/div[@class='full_third']")
    
    tags_to_remove = page.xpath("//div[@class='full_third']/div[@class='more_summary']/p/span")
    for tag in tags_to_remove:
        tag.drop_tag()

    summaries = page.xpath("//div[@class='full_third']/div[@class='more_summary']/p/text()")

    for idx, item in enumerate(items):
        try:
            title = item.xpath("./div[@class='two_thirds']/h3/a/text()")[0]
            if len(title) > 50:
                words = title[:50].split()
                title = ' '.join(words[:-1]) + '...'
            video_url = item.xpath("./div[@class='one_third']/div[@class='video_holder']/a/@href")[0]
        except IndexError:
            continue

        try:
            summary = summaries[idx]
        except:
            summary = None

        try:    
            thumb = item.xpath("./div[@class='one_third']/div[@class='video_holder']/a/img/@src")[0]
        except:
            thumb = None

        oc.add(VideoClipObject(
            url=video_url,
            title=title,
            summary=summary,
            thumb=Resource.ContentsOfURLWithFallback(thumb, R('icon-movie.png'))))

    if len(oc) < 1:
        Log('No episodes found')
        return ObjectContainer(header='Empty', message='No episodes available at the moment.')

    return oc
