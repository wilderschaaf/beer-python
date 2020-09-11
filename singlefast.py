import logging
import os
from queue import Queue
from threading import Thread
from time import time
import requests

from download import setup_download_dir, get_links, download_link, login, p_to_f
import db

states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"]


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class DownloadWorker(Thread):

    def __init__(self, queue, cur, conn):
        Thread.__init__(self)
        self.queue = queue
        self.cur = cur
        self.conn = conn
    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            link, s, state = self.queue.get()
            try:
                brewdict, beerslist = download_link(link,s)
                # logger.info(beerslist[0])
                try:
                    brewid = db.add_brewery(brewdict, state, self.cur)
                except Exception as e:
                    self.conn.rollback()
                    continue
                    raise e
                else:
                    self.conn.commit()

                logger.info(brewid)
                # if brewid == 0:
                #      continue

                for beer in beerslist:
                    try:
                        db.add_beer(beer, state, brewid, self.cur)
                    except Exception as e:
                        logger.info('beeer: %s',e)
                        self.conn.rollback()
                        raise e
                    else:
                        self.conn.commit()

            except Exception as e:
                logger.info('breeew: %s',e)
                # self.conn.rollback()
            finally:
                # self.conn.commit()
                self.queue.task_done()
        self.cur.close()
        self.conn.close()

def main():
    ts = time()
    s = requests.session()
    #download_dir = setup_download_dir()
    # links = []
    login(s)
    # for state in states:
    #     l = get_links(state, s)
    #     links += l
    #     p_to_f(str(l))
    # print(links)

    # logger.info("Total brew and beer data: %s",download_link(links[0],s))
    # Create a queue to communicate with the worker threads
    queue = Queue()
    # # Create 8 worker threads


    for x in range(8):
        conn = db.establish_connection()
        cur = db.create_cursor(conn)
        worker = DownloadWorker(queue, cur, conn)
    #     # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    # # Put the tasks into the queue as a tuple
    for state in states:
        links = get_links(state,s)
        for link in links:
            # logger.info('Queueing {}'.format(link))
            queue.put((link, s, state))
    # # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    conn.commit()
    db.close_connection(conn,cur)
    logging.info('Took %s', time() - ts)

if __name__ == '__main__':
    main()
