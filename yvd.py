import traceback
import json
import yt_dlp
import PySimpleGUI as sg
# import re
# import urllib
# import base64
from PIL import Image
import requests
import os
import datetime

WINDOW_TITLE = "YouTube Video Downloader"
THEME = 'Dark Blue 14'
THUMBNAIL_FILENAME = 'thumbnail.jpg'
THUMBNAIL_SIZE = (300, 300)
ERROR_MESSAGE = """An error occurred while attempting to download the video. Please check the following:


Internet Connection: Ensure that you have a stable internet connection. If your connection is unstable or disconnected, please try again once you have a reliable connection.



Invalid Link: Verify that the link you provided is a valid YouTube link and points to a valid YouTube video source. Ensure that the link is complete and accurately specifies the desired video. If the link is incorrect or incomplete, please provide a valid link and try again.


If the issue persists, please contact me at:

Github: 	https://github.com/not-lucky
Discord: 	not.lucky_
"""


def upload_date(date):
    date_obj = datetime.datetime.strptime(date, "%Y%m%d")
    formatted_date = date_obj.strftime("%B %d, %Y")
    return formatted_date


def create_center_column(column: sg.Column) -> list[list]:
    return [[sg.VPush()],
            [
                sg.Push(),
                sg.Column(column, element_justification='c'),
                sg.Push()
            ], [sg.VPush()]]


def validate_youtube_url(url: str) -> tuple:
    print('validate')

    try:
        ydl_opts = {'quiet': True, 'extract_flat': True}
        print(ydl_opts)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print('as')
            info = ydl.extract_info(url, download=False)
            print('extract intfo')

            # ydl.sanitize_info makes the info json-serializable
            info = ydl.sanitize_info(info)
            print('santitize')
        print('returned no error')

        if info['webpage_url_domain'] == 'youtube.com':
            return (False, info)
        else:
            with open('error.json', 'w') as fl:
                json.dump(info, fl, indent=2)
            return (True, ERROR_MESSAGE)

    # except yt_dlp.utils.ExtractorError as ex:
    #     # message = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
    #     message = 'uwuwuasdfo'
    #     print('returned error')
    #     print(message)
    #     return (True, message)

    except yt_dlp.utils.DownloadError as ex:
        # message = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(ex)
        return (True, ERROR_MESSAGE)


def download_thumbnail_image(url: str):

    response = requests.get(url)
    with open(THUMBNAIL_FILENAME, 'wb') as handle:
        handle.write(response.content)

    filename = THUMBNAIL_FILENAME

    image = Image.open(filename)
    image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    new = ".".join(filename.split('.')[:-1]) + ".png"
    image.save(new)
    return new


a = [
    r"\x1b[0;30m", r"\x1b[0;31m", r"\x1b[0;32m", r"\x1b[0;33m", r"\x1b[0;34m",
    r"\x1b[0;35m", r"\x1b[0;36m", r"\x1b[0;37m", r"\u001b", r"\u001b"
]


def escape_ansi(line):
    for i in a:
        line = line.replace(i, '')

    return line


def initial_screen() -> sg.Window:
    image_column = [[
        sg.Image(
            filename=
            r'C:/Users/lucky/downloads/Screenshot 2023-06-04 at 13-16-39 Screenshot.png'
        )
    ]]
    layout = [
        *create_center_column(image_column),
        [
            sg.Text('YouTube video/playlist link: '),
            sg.Input(key='url', expand_x=True, focus=True)
        ], *create_center_column([[
            sg.Button(button_text="Proceed", key="proceed"),
        ]]), [sg.Text('', key='processing')]
    ]
    return sg.Window(WINDOW_TITLE, layout, resizable=True, finalize=True)


def video_screen(json_data: dict):
    image_column = [[
        sg.Image(
            filename=
            r'C:/Users/lucky/downloads/Screenshot 2023-06-04 at 13-16-39 Screenshot.png'
        )
    ]]
    thumbnail = download_thumbnail_image(json_data['thumbnail'])
    # thumbnail_image = ''
    thumbnail_column = [[sg.Image(thumbnail)]]
    print('readchce')

    video_info = f"Uploader: {json_data['uploader']}\n"
    video_info += f"Title: {json_data['fulltitle']}\n"
    video_info += f"Duration: {json_data['duration_string']}\n"
    video_info += f"Views: {json_data['view_count']:,}\n"
    video_info += f"Upload Date: {upload_date(json_data['upload_date'])}\n"

    pass
    info_column = [[sg.Text(video_info)]]

    print('bbbbb')
    field_layout = [[
        sg.Column(thumbnail_column, expand_x=True),
        # sg.VSeperator(),
        sg.Column(info_column,
                  size=THUMBNAIL_SIZE,
                  scrollable=True,
                  expand_x=True),
    ]]

    video_opts = []
    video_opts_ids = []
    index = 1

    audio_size_bytes = 0
    for formats in json_data['formats']:
        if formats['acodec'] != 'none':
            if formats['filesize']:
                audio_size_bytes = formats['filesize']
            else:
                audio_size_bytes = formats['filesize_approx']

        elif formats['acodec'] == 'none' and formats['vcodec'] != 'none':
            if formats['filesize']:
                filesize = yt_dlp.utils.format_bytes(formats['filesize'] +
                                                     audio_size_bytes)
            else:
                filesize = yt_dlp.utils.format_bytes(
                    formats['filesize_approx'] + audio_size_bytes)
            video_opts_ids.append(formats['format_id'])
            video_opts.append(
                f"{index} - Resolution: {formats['resolution']}, FileSize: {filesize}, fps: {formats['fps']}, vcodec: {formats['vcodec']}"
            )
            index += 1
    video_opts[-1] += "                      (RECOMMENDED)"

    video_column = [[
        sg.Combo(video_opts,
                 key='video',
                 auto_size_text=True,
                 default_value=video_opts[-1],
                 readonly=True),
        sg.Text('Video quality'),
    ]]

    # audio_opts = [11, 22, 33, 44, 55]
    # audio_column = [[
    #     sg.Combo(audio_opts, key='audio', size=(50, 99)),
    #     sg.Text('Audio quality'),
    # ]]

    download_info_column = [
        sg.Column(video_column),
        # sg.Column(audio_column)
    ]
    cbox_subtitle_column = [[
        sg.Checkbox("Download Subtitle (english only)",
                    key='sub',
                    default=True)
    ]]
    cbox_thumbnail_column = [[
        sg.Checkbox("Download Thumbnail", key='thumb', default=True)
    ]]
    cbox_comment_column = [[
        sg.Checkbox("Download Comments", key='comm', default=False)
    ]]
    cbox_audio_column = [[
        sg.Checkbox("Download Audio Only", key='audio', default=False)
    ]]
    checkbox_columns = [
        cbox_subtitle_column, cbox_thumbnail_column, cbox_comment_column,
        cbox_audio_column
    ]
    options = [sg.Column(col) for col in checkbox_columns]

    layout = [
        *create_center_column(image_column),
        # [sg.HorizontalSeparator()],
        [
            sg.Column(
                [[sg.Frame('Video Information', field_layout, expand_x=True)]],
                expand_x=True),
        ],
        # [sg.HorizontalSeparator()],
        [
            sg.Column([[
                sg.Frame('Quality Selection',
                         create_center_column([download_info_column]),
                         expand_x=True)
            ]],
                      expand_x=True),
        ],
        [
            sg.Column([[
                sg.Frame('Extra Download Options', [options], expand_x=True)
            ]],
                      expand_x=True)
        ],
        [
            sg.FolderBrowse("Download Folder",
                            key='folder_path',
                            initial_folder=f"{os.getcwd()}/downloads")
        ],
        *create_center_column([[sg.Button('Download Video', key='download')]]),
        [
            sg.Frame('Output', [[
                sg.Multiline("",
                             size=(80, 8),
                             write_only=True,
                             reroute_cprint=True,
                             key='out',
                             expand_x=True,
                             expand_y=True)
            ]])
        ],
    ]
    layout = [[sg.Column(layout, scrollable=True, size=(1030, 950))]]
    window = sg.Window(
        WINDOW_TITLE,
        layout,
        #    size=(900,900),
        resizable=True,
        finalize=True,
        auto_size_text=True,
        scaling=1.5)
    return {
        'window': window,
        'video_opts': video_opts,
        'video_opts_ids': video_opts_ids
    }


def playlist_screen(json_data: dict):
    image_column = [[
        sg.Image(
            filename=
            r'C:/Users/lucky/downloads/Screenshot 2023-06-04 at 13-16-39 Screenshot.png'
        )
    ]]

    videos = []
    for i, entry in enumerate(json_data['entries']):
        videos.append(f"{i+1}: {entry['title']}")

    # videos = []
    # qualities = []
    # qualities_formatted_string = []
    # quality = {}

    # for entries in json_data['entries']:
    #     videos.append(f"{entries['playlist_index']} - {entries['title']}")
    #     for formats in entries['formats']:
    #         if formats['acodec'] == 'none' and formats['vcodec'] != 'none':
    #             if formats['height'] not in qualities:
    #                 formatted_string = str(formats['height']) + 'p'
    #                 quality[formats['height']] = formatted_string
    #                 qualities.append(formats['height'])

    # quality_list = sorted(quality.items(), key=lambda x: x[0])
    # # sorted(quality.values(), key=lambda x: int(x.split('p')[0]))

    # qualities = []
    # for tup in quality_list:
    #     qualities.append(tup[0])
    # qualities_formatted_string.append(tup[1])

    qualities_formatted_string = [
        '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p'
    ]

    qualities_formatted_string[-1] += '              (RECOMMENDED)'

    info_column = [[sg.Text(video)] for video in videos]

    print('bbbbb')
    field_layout = [[
        sg.Column(
            info_column,
            #   size=THUMBNAIL_SIZE,
            size=(900, 200),
            scrollable=True,
            expand_x=True),
    ]]

    playlist_column = sg.Column(
        [[
            sg.Frame('Playlist Title: ' + json_data['title'],
                     field_layout,
                     expand_x=True)
        ]],
        expand_x=True,
    )

    video_column = [[
        sg.Combo(
            qualities_formatted_string,
            key='video',
            #  disabled=True,
            auto_size_text=True,
            default_value=qualities_formatted_string[-1],
            readonly=True),
        sg.Text('Max Video quality'),
    ]]

    download_info_column = [
        sg.Column(video_column),
        # sg.Column(audio_column)
    ]
    cbox_subtitle_column = [[
        sg.Checkbox("Download Subtitle (english only)",
                    key='sub',
                    default=True)
    ]]
    cbox_audio_column = [[
        sg.Checkbox("Download Audio Only", key='audio', default=False)
    ]]

    cbox_folder = [[
        sg.Checkbox("Put videos in folder", key='folder', default=True)
    ]]
    cbox_number = [[
        sg.Checkbox("Autonumbering of videos", key='number', default=True)
    ]]

    cbox_thumbnail_column = [[
        sg.Checkbox("Download Thumbnail", key='thumb', default=True)
    ]]
    cbox_comment_column = [[
        sg.Checkbox("Download Comments", key='comm', default=False)
    ]]
    checkbox_columns = [
        cbox_audio_column, cbox_number, cbox_folder, cbox_subtitle_column,
        cbox_thumbnail_column, cbox_comment_column
    ]
    options = [sg.Column(col) for col in checkbox_columns]

    cbox_playlist_start = [[sg.Input(key='play_start', default_text='1')]]
    cbox_playlist_end = [[
        sg.Input(key='play_end', default_text=json_data['playlist_count'])
    ]]

    play_col = [cbox_playlist_start, cbox_playlist_end]

    play = [sg.Column(col) for col in play_col]

    layout = [
        *create_center_column(image_column),
        # [sg.HorizontalSeparator()],
        [playlist_column],
        # [sg.HorizontalSeparator()],
        [
            sg.Column([[
                sg.Frame('Quality Selection',
                         create_center_column([download_info_column]),
                         expand_x=True)
            ]],
                      expand_x=True),
        ],
        [
            sg.Column(
                [[sg.Frame('Playlist Range Options', [play], expand_x=True)]],
                expand_x=True)
        ],
        [
            sg.Column([[
                sg.Frame('Extra Download Options', [options], expand_x=True)
            ]],
                      expand_x=True)
        ],
        [
            sg.FolderBrowse("Download Folder",
                            key="folder_path",
                            initial_folder=f"{os.getcwd()}/downloads")
        ],
        *create_center_column(
            [[sg.Button('Download Video', key='download_playlist')]]),
        [
            sg.Frame('Output', [[
                sg.Multiline("",
                             do_not_clear=True,
                             key='out',
                             size=(80, 8),
                             write_only=True,
                             reroute_cprint=True,
                             expand_x=True,
                             expand_y=True)
            ]])
        ],
    ]
    layout = [
        *create_center_column(
            [[sg.Column(
                layout,
                size=(1200, 950),
                scrollable=True,
            )]])
    ]
    window = sg.Window(
        WINDOW_TITLE,
        layout,
        #    size=(800,900),
        resizable=True,
        auto_size_text=True,
        scaling=1.5)
    return {'window': window}


def folderr(folder_path: str,
            playlist: bool = False,
            put_in_folder: bool = False,
            numbering: bool = False) -> str:

    tmpl = '%(title)s-[%(id)s].%(ext)s'

    if playlist:
        a = ''
        if put_in_folder:
            a = '%(playlist_title)s/'
        if numbering:
            a += '%(playlist_index)s - '
        tmpl = a + tmpl

    if folder_path:
        return folder_path + '/' + tmpl
    else:
        f = os.getcwd()
        if not os.path.exists(f + '/downloads'):
            os.mkdir(f + '/downloads')
        return f + '/downloads/' + tmpl


def download_video(data: dict, values: dict, json_data: dict, url: str):
    window = data['window']

    i = 0

    def progress_hook(progress):
        nonlocal i
        if i == 0:
            output_ = f"Now Downloading: {progress.get('filename', '')}\n\n"
            sg.cprint(output_, colors='black')
            i = 1

        if progress['status'] == 'downloading':
            percent = progress['_percent_str']
            speed = progress['_speed_str']
            eta = progress['_eta_str']
            output_ = f"Downloading: {percent} at {speed}, ETA: {eta}"
            print(output_)
            sg.cprint(output_, colors='black')
            window.refresh()
            # i += 1

        elif progress['status'] == 'finished':
            output_ = f"\n\nDownload Complete: {progress.get('filename', '')}\n\n"
            sg.cprint(output_, colors='black')
            print("Download completed!")
            i = 0

    format_id = data['video_opts_ids'][data['video_opts'].index(
        values['video'])]

    form = f"{format_id}+bestaudio/b"

    if values.get('audio', False):
        form = "bestaudio"
    else:
        form = f"{format_id}+bestaudio/b"

    outtmpl = folderr(values['folder_path'])

    ydl_opts = {
        'format': form,
        'progress_hooks': [progress_hook],
        'no_color': True,
        'outtmpl': outtmpl
    }

    if values['sub'] is True:

        ydl_opts |= {
            'writesubtitles': True,
            'subtitlesformat': 'srt',
            'subtitleslangs': ['en'],
        }

    if values['thumb'] is True:
        ydl_opts |= {'writethumbnail': True}

    if values['comm'] is True:
        ydl_opts |= {'getcomments': True, 'writeinfojson': True}

    print(ydl_opts)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print('downloading')
        ydl.download([url])
        print('download actually complete')

        # ydl.sanitize_info makes the info json-serializable
        # info = ydl.sanitize_info(info)


def download_playlist(data: dict, values: dict, json_data: dict, url: str):

    window = data['window']
    i = 0

    # j = 0

    def progress_hook(progress):
        nonlocal i
        # nonlocal j
        if i == 0:
            output_ = f"Now Downloading: {progress.get('filename', '')}\n\n"
            sg.cprint(output_, colors='black')
            i = 1

        # if j < 3:
        #     with open('hellow.json', 'a+', encoding='utf-8') as fl:
        #         # a = json.load(fl)
        #         # a.append(progress)
        #         json.dump(progress, fl, indent=2)

        if progress['status'] == 'downloading':
            # percent = progress['_percent_str']
            # speed = progress['_speed_str']
            # eta = progress['_eta_str']
            # output_ = f"Downloading: {percent} at {speed}, ETA: {eta}"
            # print(output_)
            output_ = progress['_default_template']
            sg.cprint(output_, colors='black')
            window.refresh()
            # j += 1
            # i += 1

        elif progress['status'] == 'finished':
            output_ = f"\n\nDownload Complete: {progress.get('filename', '')}\n\n"
            sg.cprint(output_, colors='black')
            print("Download completed!")
            i = 0

    height = values['video'].split('p')[0]

    form = f"bv*[height<={height}]+ba/b"

    if values.get('audio', False):
        form = "bestaudio"
    else:
        form = f"bv*[height<={height}]+ba/b"

    # form = f"bv*[height<={height}]+ba/b"

    outtmpl = folderr(values['folder_path'], True, values['folder'],
                      values['number'])

    ydl_opts = {
        'format': form,
        'progress_hooks': [progress_hook],
        'no_color': True,
        'outtmpl': outtmpl,
        'playliststart': int(values['play_start']),
        'playlistend': int(values['play_end'])
    }

    if values['sub'] is True:

        ydl_opts |= {
            'writesubtitles': True,
            'subtitlesformat': 'srt',
            'subtitleslangs': ['en'],
        }

    if values['thumb'] is True:
        ydl_opts |= {'writethumbnail': True}

    if values['comm'] is True:
        ydl_opts |= {'getcomments': True, 'writeinfojson': True}

    print(ydl_opts)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print('downloading')
        ydl.download([url])
        print('download actually complete')

        # ydl.sanitize_info makes the info json-serializable
        # info = ydl.sanitize_info(info)


def popup_continue_or_not():

    layout = [[sg.Text("DOWNLOAD COMPLETE!!!\n\n")],
              [sg.HorizontalSeparator()], [sg.Text("\n\n")],
              *create_center_column([[
                  sg.Button("Same Video/Playlist Screen", key="popup_cont"),
                  sg.Button("New Video/Playlist Screen", key="popup_no_cont")
              ]])]
    return sg.Window("Download Complete", layout, modal=True)


def main():
    # i = 1
    data = {}
    url = ''
    json_data = {}
    # with open('data.json', encoding='utf-8') as fl:
    #     json_data = json.load(fl)

    # curr_window = 'init'
    window = initial_screen()
    window.BringToFront()
    # sg.cprint_set_output_destination(window, multiline_key)

    # window.close()

    # data = playlist_screen(json_data)
    # window = data['window']
    # print(window.read())
    # print(data)

    # exit()
    # i = 1
    while True:
        # print(i)
        event, values = window.Read()
        print(event, values)

        if event == 'proceed':

            # to inform user that video is processing, as window may look like it stopped responding
            window.Element('processing').update(
                'The video/playlist is processing.\n\n\nPLEASE DO NOT CLOSE THE WINDOW!!!\n\n\nIf there\'s an error, a popup will automatically appear.',
                # text_color='DarkOrchid2'
            )
            window.refresh()

            url = values['url'].strip()
            # window.perform_long_operation(
            #     lambda: my_long_func(int(values['-IN-']), a=10), '-END KEY-')

            url = url.split('&index')[0]
            temp = url.split('=')
            url = temp[0] if len(temp) == 1 else temp[1]
            url = url.split('&')[0]

            if len(url) > 11:
                url = "https://www.youtube.com/playlist?list=" + url
            print(url)

            error, json_data = validate_youtube_url(url)
            print(json_data)

            if error:

                # to remove the processing message
                window.Element('processing').update('')
                print(values)
                window.refresh()

                error_message = f'ERROR!!!\n\nURL: {url}' + '\n\n\n\n' + json_data

                sg.Popup(escape_ansi(error_message), keep_on_top=True)

            # if no error getting data
            else:

                if json_data['_type'] == 'playlist':
                    # curr_window = 'playlist'
                    data = playlist_screen(json_data)
                    print(data)

                    window.close()
                    window = data['window']

                    # pass
                else:
                    # curr_window = 'video'
                    data = video_screen(json_data)
                    window.close()
                    window = data['window']
                    # pass

                # window.close()

                # print("good url")

        elif event == "download":
            print(data, values, url, sep='\n\n')
            # download_video(data, values, json_data, url)
            sg.cprint("DOWNLOAD STARTING!!!")
            window.refresh()

            download_video(data, values, json_data, url)
            # sg.Popup("DOWNLOAD COMPLETED!!!", keep_on_top=True)

            window_pop = popup_continue_or_not()
            event_pop, _ = window_pop.read()

            if event_pop == "popup_cont" or event_pop == sg.WIN_CLOSED:
                window_pop.close()
                # continue
            elif event_pop == 'popup_no_cont':
                window_pop.close()
                window.close()

                window = initial_screen()

        elif event == 'download_playlist':
            print(data, values, url, sep='\n\n')
            print('called downlaod')
            download_playlist(data, values, json_data, url)
            sg.cprint("DOWNLOAD STARTING!!!")
            window.refresh()

            # sg.Popup("DOWNLOAD COMPLETED!!!", keep_on_top=True)

            window_pop = popup_continue_or_not()
            event_pop, _ = window_pop.read()

            if event_pop == "popup_cont" or event_pop == sg.WIN_CLOSED:
                window_pop.close()
                # continue
            elif event_pop == 'popup_no_cont':
                window_pop.close()
                window.close()

                window = initial_screen()

        else:
            break


if __name__ == '__main__':
    main()