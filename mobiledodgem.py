import json, os, random, copy
from operator import itemgetter

class InvalidMove(Exception):
    pass
class MaximumMoveFindTries(Exception):
    pass
class AiLost(Exception):
    pass

class MobileDodgem:

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

    def __init__(self, jsonpath):
        self.jsonpath = jsonpath
        self.updatejson()
        self.lookup1 = {
            0: {
                0: 10,
                1: 25,
                2: 40
            },
            1: {
                0: 5,
                1: 20,
                2: 35
            },
            2: {
                0: 0,
                1: 15,
                2: 30
            }
        }
        self.lookup2 = {
            0: {
                0: -30,
                1: -35,
                2: -40
            },
            1: {
                0: -15,
                1: -20,
                2: -25
            },
            2: {
                0: 0,
                1: -5,
                2: -10
            }
        }

        self.maxi = ['B1', 'B2']
        self.mini = ['R1', 'R2']

        self.dumpjson = self.updatejson(self.dumpjson)
        self.start = self.updatejson(self.start)
        self.ai = self.updatejson(self.ai)
        self.change_ai = self.updatejson(self.change_ai)
        self.state = self.updatejson(self.state)
        self.change_state = self.updatejson(self.change_state)
        self.find_token = self.updatejson(self.find_token)
        self.get_available_moves_of_token = self.updatejson(self.get_available_moves_of_token)
        self.get_movable_tokens = self.updatejson(self.get_movable_tokens)
        self.move_token = self.updatejson(self.move_token)
        self.board_value = self.updatejson(self.board_value)
        self.ai_move = self.updatejson(self.ai_move)
        self.check_winner= self.updatejson(self.check_winner)
        self.show_board = self.updatejson(self.show_board)        

    def start(self, id):
        id = str(id)
        def init():
            nonlocal self, id
            self.data[id]['ai'] = ''
            self.data[id]['state'] = 'dodgem-start'
            self.data[id]['dodgem'] = [
                [self.maxi[0], ' ', ' '],
                [self.maxi[1], ' ', ' '],
                [' ', self.mini[0], self.mini[1]]
            ]

            # self.data[id]['dodgem'] = [
            #     [' ', 'R2', ' '],
            #     [' ', 'B2', 'B1'],
            #     [' ', ' ', 'R1']
            # ]
            
        if not self.data.get(id):
            self.data[id] = {}    
        init()
    
        self.dumpjson()

    def ai(self, id):
        id = str(id)
        return self.data[id]['ai']

    def change_ai(self, id, ai):
        id = str(id)
        self.data[id]['ai'] = ai

        self.dumpjson()

    def state(self, id):
        id = str(id)
        return self.data[id]['state']

    def change_state(self, id, state):
        id = str(id)
        self.data[id]['state'] = state
        self.dumpjson()

    def find_token(self, id, token, board=None):
        id = str(id)
        if 'dodgem' not in self.data[id]:
            self.start(id)
        board = board if board else self.data[id]['dodgem']
        
        for i, row in enumerate(board):
            for j, col in enumerate(row):
                if token == col:
                    return [i, j]

        return None

    def get_available_moves_of_token(self, id, token, board=None):
        id = str(id)
        board = board if board else self.data[id]['dodgem']

        rv = []
        pos = self.find_token(id, token, board)
        if token in self.maxi: # r d u 
            # r
            if pos[1] < 2 and board[pos[0]][pos[1]+1] == ' ':
                rv.append('r')
            # d
            if pos[0] < 2 and board[pos[0]+1][pos[1]] == ' ':
                rv.append('d')
            # u
            if pos[0] > 0 and board[pos[0]-1][pos[1]] == ' ':
                rv.append('u')
        elif token in self.mini: # l u r
            # l
            if pos[1] > 0 and board[pos[0]][pos[1]-1] == ' ':
                rv.append('l')
            # u 
            if pos[0] > 0 and board[pos[0]-1][pos[1]] == ' ':
                rv.append('u')
            # r
            if pos[1] < 2 and board[pos[0]][pos[1]+1] == ' ':
                rv.append('r')
        return (rv if len(rv) > 0 else None)

    def get_movable_tokens(self, id, isMaximizing=True, board=None):
        id = str(id)
        board = board if board else self.data[id]['dodgem']

        tokens = self.maxi if isMaximizing else self.mini

        rv = []
        for token in tokens:
            if self.get_available_moves_of_token(id, token, board):
                rv.append(token)
        return rv

    def move_token(self, id, token, dir, board=None):
        id = str(id)
        board = board if board else self.data[id]['dodgem']

        pos = self.find_token(id, token, board)
        if moves := self.get_available_moves_of_token(id, token, board):
            if dir in moves:
                board[pos[0]][pos[1]] = ' '
                if dir == 'l':
                    board[pos[0]][pos[1]-1] = token
                elif dir == 'u':
                    board[pos[0]-1][pos[1]] = token
                elif dir == 'r':
                    board[pos[0]][pos[1]+1] = token
                elif dir == 'd': 
                    board[pos[0]+1][pos[1]] = token
                self.dumpjson()
                return board
        else:
            raise InvalidMove(f'Token: {token}, Move: {dir}')

    def board_value(self, id, board=None):
        id = str(id)
        board = board if board else self.data[id]['dodgem']

        def get_block_value(token):
            nonlocal self, id, board
            pos = self.find_token(id, token, board)

            rv = 0
            if token in self.maxi:
                if pos[0] in [1,2]:
                    for i in range(pos[0], 3):
                        if board[pos[0]][i] in self.mini:
                            rv += (-40 if i - pos[1] == 1 else -30)
                if pos[1] in [2]:
                    for i in range(pos[0], 3):
                        if board[i][pos[1]] in self.mini:
                            rv += (-40 if i - pos[0] == 1 else -30)
            if token in self.mini:
                if pos[0] in [0]:
                    for i in range(0, pos[1]):
                        if board[pos[0]][i] in self.maxi:
                            rv += (40 if i - pos[0] == 1 else 30)
                if pos[1] in [0, 1]:
                    for i in range(0, pos[0]):
                        if board[i][pos[1]] in self.maxi:
                            rv += (40 if pos[0] - i == 1 else 30)
            return rv

        def tile_value(token):
            nonlocal self, id, board
            pos = self.find_token(id, token, board)
            if token in self.maxi:
                return self.lookup1[pos[0]][pos[1]]
            elif token in self.mini:
                return self.lookup2[pos[0]][pos[1]]

        def win_tiles(token):
            nonlocal self, id
            pos = self.find_token(id, token)
            rv = 0
            if token in self.maxi:
                if pos == [1, 2]:
                    rv += 50
                if pos == [2,2]:
                    rv += 50
            elif token in self.mini:
                if pos == [0, 0]:
                    rv += -50
                if pos == [0, 1]:
                    rv += -50
            return rv

        tokens = self.maxi + self.mini
        tile_score = sum(list(map(tile_value, tokens)))
        block_score = sum(list(map(get_block_value, tokens)))
        win_score = sum(list(map(win_tiles, tokens)))
        total = tile_score + block_score + win_score
        return total

    def check_winner(self, id, board=None):
        id = str(id)
        board = board if board else self.data[id]['dodgem']

        # check mini
        if board[0][0] in self.mini and board[0][1] in self.mini:
            return self.mini

        # check maxi 
        if board[1][2] in self.maxi and board[2][2] in self.maxi:
            return self.maxi
        
        return None

    def ai_move(self, id, mode, board=None):
        id = str(id)
        board = board if board else self.data[id]['dodgem']
        maxdepth = 8

        def on_win_tile(token, isMaximizing, board):
            nonlocal self, id
            pos = self.find_token(id, token, board)
            if isMaximizing:
                return pos in [ [1, 2] , [2,2] ]
            else: 
                return pos in [ [0, 0] , [0, 1] ]

        def best_move_of_token(token, isMaximizing, board):
            nonlocal self, id
            
            token_move_score = []
        
            if moves := self.get_available_moves_of_token(id, token, board):
                for move in moves:
                    newboard = copy.deepcopy(board)                    
                    self.move_token(id, token, move, newboard)
                    score = self.board_value(id, newboard)
                    token_move_score.append([token, move, score])
                return sorted(token_move_score, key=itemgetter(2), reverse=isMaximizing)[0]

        def easy():
            nonlocal self, id
            moves = None
            tries = 10
            
            while moves == None:
                token = random.choice(self.mini)
                moves = self.get_available_moves_of_token(id, token, board)
                tries -= 1
                if tries == 0:
                    raise MaximumMoveFindTries
            chosen_move = random.choice(moves)            
            self.move_token(id, token, chosen_move)

        def medium():
            nonlocal self, id, board
            
            token_move_score = []
            other_choice = []
            for token in self.mini:
                if best_move := best_move_of_token(token, False, board):
                    if on_win_tile(token, False, board):
                        other_choice.append(best_move)
                    else:
                        token_move_score.append(best_move)
            if len(token_move_score) == 0:
                if len(other_choice) == 0:
                    raise AiLost('No moves left')
                print('other choice')
                token_move_score = other_choice
            token_move_score.sort(key=itemgetter(2))
            best_token_move = token_move_score[0] #  ['X', 'u', '-50']
            self.move_token(id, best_token_move[0], best_token_move[1])

        def hard():
            nonlocal self, id, board, maxdepth
            def minimax(token, move, isMaximizing, board, depth=maxdepth):
                board = copy.deepcopy(board)

                self.move_token(id, token, move, board)
                score = self.board_value(id, board)
                if self.check_winner(id, board) == self.mini:
                    return score + (-50 * (maxdepth - (maxdepth - depth)))

                if depth == 0:
                    return score
                else:
                    token_move_score = []
                    other_choice = []
                    if tokens := self.get_movable_tokens(id, not isMaximizing, board):
                        for token in tokens:
                            newboard = copy.deepcopy(board)
                            best_move = best_move_of_token(token, not isMaximizing, newboard)
                            self.move_token(id, best_move[0], best_move[1], newboard)
                            if on_win_tile(token, not isMaximizing, newboard):
                                other_choice.append(best_move)
                            else:
                                token_move_score.append(best_move)

                    if len(token_move_score) == 0:
                        if len(other_choice) == 0:
                            return score
                            # raise AiLost('No moves left')
                        token_move_score = other_choice 
                    token_move_score.sort(key=itemgetter(2), reverse=not isMaximizing)
                    token_move = token_move_score[0]
                    token, move = token_move[0], token_move[1]
                    return (score + minimax(token, move, not isMaximizing, board, depth-1) + (-50 if isMaximizing else 50))
                
            token_move_score = []
            movable_tokens = self.get_movable_tokens(id, False, board)
            for token in movable_tokens:
                moves = self.get_available_moves_of_token(id, token, board)
                for move in moves:
                    token_move_score.append([token, move])
            
            if len(token_move_score) == 1: # move if only one token and one move for token
                token_move = token_move_score[0]
                self.move_token(id, token_move[0], token_move[1], board)
            else:
                for token_move in token_move_score:
                    token, move = token_move[0], token_move[1]
                    token_move.append(minimax(token, move, False, board))
                token_move_score.sort(key=itemgetter(2))
                best_move = token_move_score[0]
                self.move_token(id, best_move[0], best_move[1], board)

        modes = {'easy': easy, 'medium': medium, 'hard': hard}
        modes[mode]()
        self.dumpjson()

    def show_board(self, id):
        id = str(id)
        rv = 'Board:\n'

        for i, row in enumerate(self.data[id]['dodgem']):
            rv += f'{row[0]:^6}|{row[1]:^6}|{row[2]:^6}\n'
            if not i == 2:
                rv += '-' * 16 + '\n'
        return rv

    def dodgemhelp(self):
        def table(i):
            lookup = self.lookup1 if i == 1 else self.lookup2
            rv = ''  
            for k in range(0, 3):
                rv += ' | '.join(list(map(lambda x: f'{x:3}', lookup[k].values())))
                rv += '\n'
                rv += '-' * 15
                rv += '\n' if k < 2 else ''

            return rv

        text = f'''Dodgem is a simple abstract strategy game invented by Colin Vout and described in 
the book Winning Ways for Your Mathematical Plays. The 3×3 game can be completely analyzed (strongly solved) 
and is a win for the first player—a table showing who wins from every possible position is given 
in Winning Ways, and given this information it is easy to read off a winning strategy.

Score Board - Maximizing Player
{table(1)}

Score Board - Minimizing Player
{table(2)}'''

        return text
if __name__ == '__main__':
    md = MobileDodgem('./pert.json')
    md.start(2222)
    print(md.show_board(2222))
    print(md.dodgemhelp())
    # md.board_value(2222)
    # md.move_token(2222, 'B', 'r')
    # md.ai_move(2222, 'hard')
    # md.board_value(2222)