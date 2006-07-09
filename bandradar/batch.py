import turbogears
import logging
from sqlobject.util.threadinglocal import local as threading_local
from model import hub, BatchRecord

log = logging.getLogger("bandradar.batch")

def task():
    hub.threadingLocal = threading_local()
    hub.begin()
    last = BatchRecord.select(orderBy=BatchRecord.q.last_handled).reversed()[:1][0]
    hub.commit()
    log.info("Bandradar task executing")
