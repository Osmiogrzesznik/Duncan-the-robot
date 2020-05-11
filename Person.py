'''
class used to store data about known fACES and their detection history
if face is big on camera (x,y,w,h) it means it is close to camera, and if face dissapeared in last few seconds,
duncan may assume the person is still around.

Position/value history could be made as reusable class across system
TODO This object together with some logic could allow for duncan to rotate funnily between faces looking once to one and to other
'''
from ValueHistory import ValueHistory


class Person:
    def __init__(self, name):
        self.MAX_HIST_LENGTH = 10
        self.name = name
        self.time_last_seen_history = ValueHistory(10)
        self.prev_pos_hist = ValueHistory(10)

    ''' returns first element of position history '''
    @property
    def prev_pos(self):
        return self.prev_pos_hist.prv

    @property
    def pos(self):
        return self.prev_pos_hist.v

    @pos.setter
    def pos(self, nu_pos):
        # if this is first time setting pos
        self.prev_pos_hist.v = nu_pos  # bit weird if java but so cool , just set and forget
