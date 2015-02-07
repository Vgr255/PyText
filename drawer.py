import threading
import shutil

Lock = threading.RLock()

PAD_UP = "\xFFFFFFFFUP"
PAD_DW = "\xFFFFFFFFDW"
PAD_RG = "\xFFFFFF"
PAD_LF = "\xFFFF"

class Handler:
    def __init__(self):
        self.freed = False
        self.combiners = []
        self.previous = []
        self.columns, self.lines = shutil.get_terminal_size()

    def mainloop(self):
        while True:
            columns, lines = shutil.get_terminal_size()
            if columns != self.columns or lines != self.lines:
                self.columns = columns
                self.lines = lines
                with Lock:
                    self.reprint() # user resized the window; let's re-draw the whole thing
            if self.freed:
                with Lock:
                    self.binder()

    def binder(self):
        """Binds together all the strings in a possibly good way."""
        to_combine = []
        bind_up = []
        bind_down = []
        bind_left = []
        bind_right = []
        for item in self.combiners:
            items = item.split("\n")
            if items[0] != PAD_UP:
                bind_up.append(items)
            if items[-1] != PAD_DW:
                bind_down.append(items)
            if False in [x.startswith(PAD_LF) for x in items]:
                bind_left.append(items)
            if False in [x.endswith(PAD_RG) for x in items]:
                bind_right.append(items)
        # todo: bind the same ones together and stuff

    def reprint(self):
        self.combiners = list(self.previous)
        self.binder() # ask it to re-draw everything

    def add(self, item):
        self.combiners.append(item)

    __add__ = add

    def free(self):
        self.freed = True

    def __len__(self):
        return len(self.combiners)

    def __bool__(self):
        return self.freed

def padder(words, maxlen, pad_up=False, pad_down=False, pad_left=False, pad_right=False):
    msg = []
    if pad_up:
        msg.append(PAD_UP)
    for word in words:
        message = word
        if pad_left:
            message = PAD_LF + " | " + message
        if pad_right:
            message = message + " | " + PAD_RG
        msg.append(message)
    if pad_down:
        msg.append(PAD_DW)
    return filler(msg, maxlen)

def filler(items, size, horizontal=True):
    new_items = []
    if horizontal: # horizontal filling
        for item in items:
            if item in (PAD_UP, PAD_DW):
                continue
            alter = True
            item_ = list(item)
            while len(item_) < size:
                if item.startswith(PAD_LF + " | "):
                    if alter:
                        item_.insert(len(PAD_LF)+3, " ")
                    elif item.endswith(" | " + PAD_RG):
                        item_.insert(-len(PAD_RG)+2, " ")
                    else:
                        item_.append(" ")
                elif item.endswith(" | " + PAD_RG):
                    if alter:
                        item_.insert(0, " ")
                    else:
                        item_.insert(-len(PAD_RG)+2, " ")
                else:
                    if alter:
                        item_.insert(0, " ")
                    else:
                        item_.append(" ")
                alter = not alter
            new_items.append("".join(item_))
    else: # vertical filling
        if items[0] == PAD_UP:
            pass # todo

    return new_items

Thread = Handler()

threading.Thread(None, Thread.mainloop, daemon=True).start()
