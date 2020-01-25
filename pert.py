
from math import floor, ceil
def round(n):
    if n - floor(n) >= 0.5:
        return ceil(n)
    return floor(n)

class MissingActivity(Exception):
    pass

class Pert:
    class Activity:
        code = ''

        a = None # optimistic
        b = None # pessimistic
        m = None # most probable time
        predecessors_codes = [] # ['name', 'name'] of predecessor
        predecessors_objs = [] # [type(Activity)] of predecessor

        et = None
        es = None
        ef = None

        ls = None
        lf = None

        slack = None

        def __init__(self, a, m, b, code='', predecessors_codes=[]):
            self.predecessors_codes = predecessors_codes
            self.predecessors_objs = []
            self.a = a
            self.b = b
            self.m = m
            self.code = code
            self._et()

        def solve_e(self):
            self._es()
            self._ef()
        
        def solve_l(self, lf):
            if self.lf is None:
                self.lf = lf
            elif lf < self.lf:
                self.lf = lf
            self.ls = self.lf - self.et
            for pred in self.predecessors_objs:
                pred.solve_l(self.ls)
        
        def solve_s(self):
            self.slack = self.lf - self.ef

        def _et(self):
            self.et =  round( (self.a + (4 * self.m) + self.b) / 6 )

        def _es(self):
            if len(self.predecessors_objs) == 0:
                self.es = 0
            else:
                # print(self.code, [p.ef for p in self.predecessors_objs])
                for p in self.predecessors_objs:
                    if p.ef is None:
                        p.solve_e()
                self.es = max([p.ef for p in self.predecessors_objs])            
            return self.es
            
        def _ef(self):
            self.ef = self.et + self.es
        
        def addPredecessor(self, other):
            self.predecessors_objs.append(other)

        def __str__(self):
            return f'{self.code}\t{self.et}\t{self.es}\t{self.ef}\t{self.ls}\t{self.lf}\t{self.slack}'

    def __init__(self):
        self.activities = []
        self.ends = []
        self.ends_objs = []
        self.cp = None

    def solve(self):
        self.gen_endsobjs()
        self.activities.sort(key=lambda x: x.code)
        self.checkactivities()
        
        for activity in self.activities: # add predecessor objects to the activities
            for code in activity.predecessors_codes:
                predecessor = self.find_activity(code)
                if predecessor:
                    activity.addPredecessor(predecessor)        
        # ES AND EF
        for endobj in self.ends_objs:
            endobj.solve_e()
        # MAXIMUM DURATION
        max_ef = max([ e.ef for e in self.ends_objs ])
        # LS AND LF
        for endobj in self.ends_objs:
            endobj.solve_l(max_ef)
        # SLACK
        for activity in self.activities:
            activity.solve_s()
        # CRITICAL PATH
        cpms = []
        found = True
        zslack = [x for x in self.ends_objs if x.slack == 0]
        if len(zslack) != 0:
            zslack = zslack[0]
            cpms.append(zslack.code)
            while zslack.predecessors_objs != None:
                zslack = [x for x in zslack.predecessors_objs if x.slack == 0]
                if len(zslack) != 0:
                    zslack = zslack[0]
                    cpms.append(zslack.code)
                else:
                    break
            for a in cpms:
                act = self.find_activity(a)
                if act.slack != 0:
                    found = False
                    break
            if found:
                cpms = cpms[::-1]
                temp = '-'.join(cpms)
                self.cp = temp

    def gen_endsobjs(self):
        for end in self.ends:
            self.ends_objs.append(self.find_activity(end))

    def find_activity(self, code):
        for activity in self.activities:
            if activity.code == code:
                return activity
        return False

    def add(self, a, m, b, code, predecessors=[]):
        predecessors = ([] if not predecessors else predecessors)
        new = self.Activity(a,m,b,code,predecessors)
        self.activities.append(new)
        self._update(end = new)

    def _update(self, end):
        self.ends.append(end.code)
        
        for end in self.ends: # for end in ends check if it is part of ends.predecessors
            for activity in self.activities:
                if end in activity.predecessors_codes:
                    try:
                        self.ends.remove(end)
                    except:
                        pass
    
    def show(self):
        self.activities.sort(key=lambda x: x.code)
        response = 'Code\tET\tES\tEF\tLS\tLF\tSlack\n'
        for a in self.activities:
            response += f'{a.code}\t\t{a.et}\t{a.es}\t{a.ef}\t{a.ls}\t{a.lf}\t{a.slack}\n'
        if self.cp:
            response += f'\nThe Critical Path for this set of activities is \n{self.cp}.'
        else:
            response += f'There are no critical path for this set of activities.'
        return response

    def checkactivities(self):
        codes = [act.code for act in self.activities]
        for act in self.activities:
            if act.code == None:
                pass
            else:
                for p_act in act.predecessors_codes:
                    if p_act not in codes:
                        raise MissingActivity(p_act)

if __name__ == '__main__':
    obj = Pert()
    obj.add(3,6,15,'A')
    obj.add(2,5,14,'B')
    obj.add(6,12,30,'C',['A'])
    obj.add(2,5,8,'D',['A'])
    obj.add(5,11,17,'E',['C'])
    obj.add(3,6,15,'F',['D'])
    obj.add(3,9,27,'G',['B'])
    obj.add(1,4,7,'H',['F','E'])
    obj.add(4,19,28,'I',['G'])

    print(f'{obj.ends=}')
    obj.solve()
    print('-----------------')

    print(obj.show())
