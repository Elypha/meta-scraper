from multiprocessing import Pool

import JK

import dmm
import mgstage
import tokyohot


if __name__ == '__main__':

    # conf
    root_raw = R'K:\0'
    root_finished = R'K:\1'
    single_processe = 0
    processes = 12

    # main
    root_raw = root_raw.replace('\\', '/')
    root_finished = root_finished.replace('\\', '/')
    videos = JK.file.findall(root_raw, ['mp4', 'mkv', 'wmv', 'avi'])

    print(F'Find {len(videos)} files\n\n')

    if single_processe == 0:
        p = Pool(processes)
        for video in videos:
            p.apply_async(dmm.scraper, args=(video, root_finished, ))
        p.close()
        p.join()
    else:
        for video in videos:
            print(video)
            dmm.scraper(video, root_finished)
