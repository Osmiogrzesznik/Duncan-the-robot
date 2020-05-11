'''
class used to store data about known fACES and their detection history
if face is big on camera (x,y,w,h) it means it is close to camera, and if face dissapeared in last few seconds,
duncan may assume the person is still around.

value history could be made as reusable class across system
TODO This object together with some logic could allow for duncan to rotate funnily between faces looking once to one and to other
'''


class ValueHistory:
    def __init__(self, MAX_HIST_LENGTH):
        self.MAX_HIST_LENGTH = MAX_HIST_LENGTH
        self._v = None
        self.prev_v_hist = []

    @property
    def prv(self):
        if not self.prev_v_hist:
            return None
        return self.prev_v_hist[-1]

    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, nu_v):
        # if this is first time setting v
        if not self._v is None:
            self.prev_v_hist.append(self._v)
        # always set new v
        self._v = nu_v
        # remove first element if list is too big
        if len(self.prev_v_hist) > self.MAX_HIST_LENGTH:
            del self.prev_v_hist[0]
