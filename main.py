import JK
import fanza
from multiprocessing import Pool



if __name__ == '__main__':
    # config
    root_raw = R'E:\Project\jav\meta-scraper\raw'.replace('\\', '/')
    root_finished = R'E:\Project\jav\meta-scraper\finished'.replace('\\', '/')

    # pre
    videos = JK.file.findall(root_raw, ['mp4', 'mkv', 'wmv'])

    print(F'Find {len(videos)} files.\n\n')

    # main
    p = Pool(24)

    for video in videos:
        # fanza.scraper(video, root_finished)
        p.apply_async(fanza.scraper, args=(video, root_finished, ))
    
    p.close()
    p.join()
