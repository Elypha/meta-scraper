from multiprocessing import Pool

import JK

import dmm
import mgstage
import tokyohot



if __name__ == '__main__':
    
    root_raw      = R'H:\0'
    root_finished = R'H:\1'

    root_raw = root_raw.replace('\\', '/')
    root_finished = root_finished.replace('\\', '/')
    videos = JK.file.findall(root_raw, ['mp4', 'mkv', 'wmv', 'avi'])

    print(F'Find {len(videos)} files\n\n')

    ## main
    # p = Pool(12)

    # for video in videos:
    #     p.apply_async(mgstage.scraper, args=(video, root_finished, ))

    # p.close()
    # p.join()


    ## main (debug)
    for video in videos:
        print(video)
        dmm.scraper(video, root_finished)
