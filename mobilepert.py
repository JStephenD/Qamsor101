import json, csv, os
from pert import (Pert, 
    MissingActivity
    )

class ParseError(Exception):
    pass

class MobilePert:
    def updatejson(self, func=None):
        try:
            with open(self.jsonpath, 'r') as rf:
                self.data = json.load(rf)
        except:
            with open(self.jsonpath, 'w') as wf:
                data = {}
                json.dump(data, wf)
        finally:
            with open(self.jsonpath, 'r') as rf:
                self.data = json.load(rf)
        def f(*args, **kwargs):
            return func(*args, **kwargs)
        return (f if func else None)
    
    def dumpjson(self):
        with open(self.jsonpath, 'w') as wf:
            json.dump(self.data, wf)

    def __init__(self, jsonpath=None):
        self.jsonpath = jsonpath
        self.updatejson()

        self.dumpjson = self.updatejson(self.dumpjson)
        self.reset = self.updatejson(self.reset)
        self.add = self.updatejson(self.add)
        self.solve = self.updatejson(self.solve)
        self.changeState = self.updatejson(self.changeState)
        self.state = self.updatejson(self.state)

        self.updatejson()

    def reset(self, id):
        id = str(id)
        def init():
            nonlocal self, id
            self.data[id]['state'] = 'pert-start'
            self.data[id]['activities'] = []
            
        if not self.data.get(id):
            self.data[id] = {}
        init()
    
        self.dumpjson()

    def add(self, id, code=None, a=None, m=None, b=None, prs=None, message=None):
        response = ''
        if message:
            parsed = message.split(' ')
            if len(parsed) < 4:
                return 'Error in parsing activity, insufficient data.'
            elif len(parsed) > 5:
                return 'Error in parsing activity, data entered incorrectly.'
            for i, e in enumerate(parsed):
                if i == 0:
                    code = e
                elif i in [1,2,3]:
                    try:
                        int(e)
                        a = e if i == 1 else a
                        m = e if i == 2 else m
                        b = e if i == 3 else b
                    except:
                        return 'Error in parsing activity, value error'
                elif i == 4:
                    prs = e.split('-')
        id = str(id)
        self.data[id]['activities'].append({
            "code": code,
            "a": a,
            "m": m,
            "b": b,
            "prs": (prs if prs else None)
        })
        self.dumpjson()
        return f'Activity {code} with values < {a}, {m}, {b} > added.'
    
    def changeState(self, id, state):
        id = str(id)
        self.data[id]['state'] = state
        self.dumpjson()
    
    def state(self, id):
        id = str(id)
        if id not in self.data:
            self.reset(id)
        return self.data[id]['state']
    
    def showactivities_s(self, id):
        id = str(id)
        rv = 'Code\ta\tm\tb\tPrds\n'
        for act in self.data[id]['activities']:
            prs = act['prs'] if act['prs'] else ''
            rv += f'{act["code"]}\t\t{act["a"]}\t{act["m"]}\t{act["b"]}\t{prs}\n'
        return rv

    def solve(self, id):
        id = str(id)
        pert = Pert()
        for act in self.data[id]['activities']:
            pert.add(int(act['a']), int(act['m']), int(act['b']), act['code'], act['prs'])
        try:
            pert.solve()
            with open(f'./pert{id}.csv', 'w') as wf:
                wr = csv.writer(wf)
                wr.writerow(['Code', 'a', 'm', 'b', 'et', 'es', 'ef', 'ls', 'lf', 'slack'])
                for a in pert.activities:
                    wr.writerow([a.code, a.a, a.m, a.b, a.et, a.es, a.ef, a.ls, a.lf, a.slack])

        except MissingActivity as e:
            raise MissingActivity(f'Missing Activity with code {e}')
        return pert.show()

    def perthelp(self):
        text = '''In project management, Project Evaluation Review Technique or PERT is used to identify the 
time it takes to finish a particular task or activity. It is a system that helps in proper scheduling and 
coordination of all tasks throughout the project. It also helps in keeping track of the progress, or lack 
thereof, of the project.

Knowing the time it would take to execute a project is crucial as it helps project managers decide on other 
factors such as the budget and task delegation. No matter how big or small a project is, estimates can be 
too optimistic or pessimistic, but using a PERT chart will help determine more realistic estimates.

Definitions and Terminologies:
Optimistic time – The least amount of time to complete a task
Pessimistic time – The maximum amount of time to complete a task
Most likely time – Assuming there are no problems, it is the best estimate of how long it would take to complete a task.
Expected time – Assuming there are problems, it is the best estimate of how long it would take to complete a task.
ES - Earliest time to start.
EF - Earliest time to finish.
LS - Latest time to start.
LF - Latest time to finish.

Slack – Refers to the amount of time a task can be delayed without resulting in an overall delay to other tasks or the project.
Critical Path – Indicates the longest possible continuous path from the start to the end of a task or event
Critical Path Activity – Refers to an activity without slack'''
        return text

if __name__ == '__main__':
    mp = MobilePert('./pert.json')
    mp.reset(1111)
    mp.add(1111, message="A 3 6 15")
    mp.add(1111, message="B 2 5 14")
    mp.add(1111, message="C 6 12 30 A")
    mp.add(1111, message="D 2 5 8 A")
    mp.add(1111, message="E 5 11 17 C")
    mp.add(1111, message="F 3 6 15 D")
    mp.add(1111, message="G 3 9 27 B")
    mp.add(1111, message="H 1 4 7 F-E")
    mp.add(1111, message="I 4 19 28 G")
    print(mp.perthelp())
    print(mp.solve(1111))
