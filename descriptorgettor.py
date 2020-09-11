import logging
import os
from queue import Queue
from threading import Thread
from time import time
import requests
import re

from download import setup_download_dir, get_links, download_link, login, p_to_f, get_reviews, descs
import db

ld = len(descs)

states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"]


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class DownloadWorker(Thread):

    def __init__(self, queue, cur, conn, bc):
        Thread.__init__(self)
        self.queue = queue
        self.cur = cur
        self.conn = conn
        self.count = [0]*len(descs)
        self.bc = bc
    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            link, s = self.queue.get()

            try:
                revs = get_reviews(link,s)
                for rev in revs:
                    self.count = count_agg(self.count, rev)
                try:
                    add_descs(link, self.cur, self.count)
                except Exception as e2:
                    logger.info('error: %s',e2)
                    self.conn.rollback()
                else:
                    self.conn.commit()
            except Exception as e:
                logger.info('error: %s',e)
            finally:
                self.count = [0]*len(descs)
                self.bc+=1
                if self.bc%100==0:
                    logger.info(self.bc)
                # self.f.write(str(self.count))
                self.queue.task_done()
        self.cur.close()
        self.conn.close()

def add_descs(link, cur, counts):
    try:
        cur.execute('UPDATE Beers SET descs=%s WHERE Link = %s',(counts, link))
    except Exception as e:
        raise e
    finally:
        return

def count_agg(counts, rev):
    words = re.split(', | |\. |-|! |,|\.|!|; |;',rev)
    for word in words:
        for i in range(ld):
            if word in descs[i].split('/'):
                counts[i]+=1
    return counts

def get_all_bids():
    conn = db.establish_connection()
    cur = db.create_cursor(conn)
    out = []
    try:
        cur.execute('SELECT BreweryID FROM Breweries')
        for bid in cur:
            out.append(bid[0])
    except Exception as e:
        logger.info(e)
    finally:
        db.close_connection(conn,cur)
        return out

def get_blinks_from_bid(bid):
    conn = db.establish_connection()
    cur = db.create_cursor(conn)
    out = []
    try:
        cur.execute('SELECT Link FROM Beers WHERE BreweryID=%s',(bid,))
        for link in cur:
            out.append(link[0])
    except Exception as e:
        logger.info(e)
    finally:
        db.close_connection(conn,cur)
        return out

def main():
    ts = time()
    s = requests.session()
    f = open("test.html","a")
    #download_dir = setup_download_dir()
    # links = []
    login(s)
    bids = get_all_bids()
    # for state in states:
    #     l = get_links(state, s)
    #     links += l
    #     p_to_f(str(l))
    # print(links)

    # logger.info("Total brew and beer data: %s",download_link(links[0],s))
    # Create a queue to communicate with the worker threads
    queue = Queue()
    # # Create 8 worker threads
    bc=0

    for x in range(8):
        conn = db.establish_connection()
        cur = db.create_cursor(conn)
        worker = DownloadWorker(queue, cur, conn, bc)
    #     # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    # # Put the tasks into the queue as a tuple
    for bid in bids:
        links = get_blinks_from_bid(bid)
        for link in links:
            # logger.info('Queueing {}'.format(link))
            queue.put((link, s))
    # # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    # conn.commit()
    # db.close_connection(conn,cur)
    f.close()
    print(bids)
    print(ld)
    logging.info('Took %s', time() - ts)

if __name__ == '__main__':
    main()
