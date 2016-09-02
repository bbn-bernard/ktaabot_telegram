
# coding: utf-8

import datetime as dt
import random
import time

import game_model as gm

MIN_WORD_LEN = 3
MAX_QUERY_LEN = 50

GAME_OBJ = {}
# game_obj = {
    # chat['id']: {
    # 'game': game_model,
    # 'chat_type': group/private,
    # 'answer': {'first_name': [],
    #           }
# }
# }

POINTS = {3: 1,
          4: 1,
          5: 2,
          6: 3,
          7: 5,
          8: 11}

DEBUG = True
GAME_DURATION = 300
GAME_REMAINDER = 30
GAME_WAIT_BEGIN = 30
GAME_GROUP_QUOTA = 2
GAME_REMAINDER_BEGIN = 10
GAME_REMAINDER_GRID = 10

if DEBUG:
    GAME_DURATION = 30
    GAME_REMAINDER = 10
    GAME_WAIT_BEGIN = 10
    GAME_REMAINDER_BEGIN = 5
    GAME_REMAINDER_GRID = 3
GAME_INTERVAL = 1

GAME_STATE_DRAFT = 1
GAME_STATE_RUNNING = 1<<1
GAME_STATE_FINISH = 1<<2
GAME_STATE_REMIND_OK = 1<<3
GAME_STATE_REMIND_BEGIN_OK = 1<<4

COMMANDS = ['/aturan', '/buat', '/game', '/skor']

# NOTES: for refactor
import net_request as req
json_request = req.json_request

def print_grid(chat_id, message_id=False):
    game_ins = GAME_OBJ[chat_id]
    grid = game_ins['game']['grid'].split(' ')
    
    respond_text = 'Grid KTAA:\n\n'
    respond_text += '''```text\n'''
    for g in grid:
        g_ = '{:>12}'.format(''.join(['%s ' %x for x in g.upper()]))
        respond_text += '''%s\n''' % (g_)
    respond_text += '''```\n\n'''
    
    result = json_request('sendMessage', 
                          {'chat_id': chat_id,
                           'text': respond_text,
                           'reply_to_message_id': message_id,
                           'parse_mode': 'Markdown',})
    
    return result

def print_no_game(chat_id, message_id=False):
    respond_text = 'Tidak ada game di sini.\nBuat game baru dengan /buat.'
    result = json_request('sendMessage', 
                          {'chat_id': chat_id,
                           'text': respond_text,
                           'reply_to_message_id': message_id,})
                                 
    return result

def get_score_text(game_ins):
    answer_obj = game_ins['answer']
    
    scores = {}
    for k,vs in answer_obj.items():
        score = sum([get_point(w) for w in vs])
        first_name = k.split('$')[0]
        scores.update({first_name: score})
    
    if scores:
        import operator
        # sort scores by value
        sorted_scores = sorted(scores.items(), 
                               key=operator.itemgetter(1), reverse=True)
        
        respond_text = ''
        for i, score in enumerate(sorted_scores):
            if i == 0:
                respond_text += '{:>2}. {} ({}) \xf0\x9f\xa4\x93\n'.format(i+1, score[0], score[1])
            else:
                respond_text += '{:>2}. {} ({})\n'.format(i+1, score[0], score[1])
    else:
        respond_text = 'Tidak ada yang dapat skor. Coba lagi!'
        
    return respond_text

def get_finish_text(game_ins):
    solutions = game_ins['game']['solutions'].split(',')
    total_points = sum([get_point(w) for w in solutions])
    score_text = get_score_text(game_ins)
    respond_text = 'Game selesai!\n\n%s\n' % (score_text)
    respond_text += 'Fakta: \n'
    respond_text += ' - banyak kata dalam grid = %s\n' % (len(solutions))
    respond_text += ' - total poin = %s' % (total_points)
    
    return respond_text
    
def print_need_player(game_ins, update_obj):
    n_more_players = GAME_GROUP_QUOTA - len(game_ins['players'])
    # NOTES: need more players
    respond_text = '''\
Kurang %s pemain. Ping teman-temanmu!
Gunakan /game untuk bergabung.''' % (n_more_players)
    json_request('sendMessage', {'chat_id': update_obj['message']['chat']['id'],
                                 'text': respond_text,
                                 'reply_to_message_id': update_obj['message']['message_id'],})
                                 
    return True
    
def check_quorum(game_ins, update_obj):
    result = False
    players = game_ins['players']
    players.add(update_obj['message']['from']['id'])
    n_players = len(players)
    if n_players < GAME_GROUP_QUOTA:
        print_need_player(game_ins, update_obj)
    else:
        # NOTES: toggle draft
        game_ins['state'] ^= GAME_STATE_DRAFT
        game_ins['state'] |= GAME_STATE_RUNNING
        print_grid(update_obj['message']['chat']['id'], 
                   update_obj['message']['message_id'])
                   
        result = True
    
    return result

def parse_input(update_obj):
    msg_text = update_obj['message']['text']
    args_ = msg_text.split(' ')
    args = [arg.lower() for arg in args_]
    
    return args

def get_point(word):
    # NOTES: longer than 8 character
    if len(word) < MIN_WORD_LEN:
        result = 0
    else:    
        result = POINTS.get(len(word), max(POINTS.values()))
    
    return result
    
last_update_id = 0

while True:
    updates = json_request('getUpdates', {'offset': last_update_id})
    
    if not updates:
        time.sleep(3)
        continue

    respond_text = ''
    for result in updates['result']:
        
        if result.get('message', False): #and result['message'].get('entities', False):
            game_ins = GAME_OBJ.get(result['message']['chat']['id'], False)
            
            command, answer = False, False
            msg_text = result['message'].get('text', False)
            if msg_text:
                args = parse_input(result)
                if args[0].startswith('/'):
                    raw_command = args[0]
                    # format: command@botname
                    command = raw_command.split('@')[0]
                else:
                    answer = args[0]
            else:
                args = []
                
            # print result
            timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print '%s, %s' % (args, timestamp)
            
            if msg_text and not command and game_ins and \
                game_ins['state'] & GAME_STATE_RUNNING:
                # NOTES: process jawaban
                if answer and len(answer) >= MIN_WORD_LEN and len(answer) < MAX_QUERY_LEN:
                    w = answer
                    if game_ins:
                        if game_ins['state'] & GAME_STATE_RUNNING:
                            solutions = game_ins['game']['solutions'].split(',')
                            answer_obj = game_ins['answer']
                            current_sol = []
                            for k,ans in answer_obj.items():
                                current_sol += ans
                            if w in current_sol:
                                respond_text = '"%s" sudah ketebak. Cari yang lain!' % (w)
                                json_request('sendMessage', 
                                             {'chat_id': result['message']['chat']['id'],
                                              'text': respond_text,
                                              'reply_to_message_id': result['message']['message_id'],})
                            elif w in solutions:
                                poin = get_point(w)
                                answer_obj = game_ins['answer']
                                ans_key = '%s$%s' % (result['message']['from']['first_name'], \
                                    result['message']['from']['id'])
                                current_ans = answer_obj.get(ans_key, [])
                                answer_obj.update({
                                    ans_key: current_ans + [w]
                                })    
                                # print game_ins
                                respond_text = 'Kata ditemukan. Poinmu +%s' % (poin)

                                json_request('sendMessage', 
                                             {'chat_id': result['message']['chat']['id'],
                                              'text': respond_text,
                                              'reply_to_message_id': result['message']['message_id'],})
                                # NOTES: send grid remainder, only when it idle
                                # don't spam!
                                elapsed_last_update = time.time() - game_ins['last_update']
                                if elapsed_last_update > GAME_REMAINDER:
                                    print_grid(result['message']['chat']['id'])              
                                              
                        else:
                            respond_text = 'Game belum dimulai. Gunakan /game untuk menambah kuota'
                            json_request('sendMessage', {'chat_id': result['message']['chat']['id'],
                                                         'text': respond_text,
                                                         'reply_to_message_id': result['message']['message_id'],})   
                            
                    else:
                        print_no_game(result['message']['chat']['id'], 
                                      result['message']['message_id'])
                pass
            
            elif command:
                if command == '/aturan':
                    respond_text = '''ktaabot adalah game mencari kata dari karakter-karakter acak berukuran grid 4x4. 
Cari kata dari grid. Setiap kata sama dengan rangkaian karakter dalam grid. Kamu dapat merangkaikan karakter yang bertetangga secara horizontal, vertika, atau diagonal. Panjang kata minimal 3 karakter. Perintah yang tersedia:
/aturan - liat aturan ini
/buat - membuat game dengan grid baru
/game - memulai game atau melihat grid game yang ada
/skor - liat skor'''
                    json_request('sendMessage', {'chat_id': result['message']['chat']['id'],
                                                 'text': respond_text})
                # TODOS: refactor
                elif command == '/buat':
                    if result['message']['chat']['type'] == 'private':
                        game_state = GAME_STATE_RUNNING
                    else:
                        game_state = GAME_STATE_DRAFT
                    if not game_ins:
                        grid = gm.get_game(result['message']['chat']['id'])
                        assert not grid.get('error', False), 'No grid available'
                        
                        GAME_OBJ.update({
                            result['message']['chat']['id']: {
                                'game': grid,
                                'chat_type': result['message']['chat']['type'],
                                'answer': {},
                                'create_date': time.time(),
                                'players': set([result['message']['from']['id'],]),
                                'state': game_state,
                                'last_update': time.time(), # to track idle time
                            }
                        })
                        if game_state & GAME_STATE_DRAFT:
                            game_ins = GAME_OBJ[result['message']['chat']['id']]
                            check_quorum(game_ins, result)
                        if game_state & GAME_STATE_RUNNING:
                            print_grid(result['message']['chat']['id'], 
                                       result['message']['message_id'])    
                    else:
                        if game_ins['state'] & GAME_STATE_RUNNING:
                            print_grid(result['message']['chat']['id'], 
                                       result['message']['message_id'])
                        else:
                            check_quorum(game_ins, result)

                elif command == '/game':
                    if not game_ins:
                        print_no_game(result['message']['chat']['id'], 
                                      result['message']['message_id'])
                    else:
                        if game_ins['state'] & GAME_STATE_DRAFT:
                            check_quorum(game_ins, result)
                        
                        elif game_ins['state'] & GAME_STATE_RUNNING:
                            print_grid(result['message']['chat']['id'], 
                                       result['message']['message_id'])
                        
                        else:
                            pass
                    
                elif command == '/skor':
                    if not game_ins:
                        top_scores = gm.get_score(result['message']['chat']['id'])
                        respond_text = ''
                        if top_scores:
                            respond_text = 'Skor Tertinggi:\n'
                            for i,p in enumerate(top_scores):
                                if i == 0:
                                    respond_text += '{:>2}. {} ({}) \xf0\x9f\x91\x91\n'.format(i+1, p['user_name'], p['score'])
                                else:
                                    respond_text += '{:>2}. {} ({})\n'.format(i+1, p['user_name'], p['score'])
                            json_request('sendMessage', {'chat_id': result['message']['chat']['id'],
                                                         'text': respond_text,})
                        else:
                            print_no_game(result['message']['chat']['id'],
                                          result['message']['message_id'])
                    else:   
                        if game_ins['state'] & GAME_STATE_RUNNING:
                            respond_text = get_score_text(game_ins)
                            json_request('sendMessage', {'chat_id': result['message']['chat']['id'],
                                                         'text': respond_text,
                                                         'reply_to_message_id': result['message']['message_id'],})
                        else:
                            respond_text = 'Gunakan /game untuk menambah kuota'
                            json_request('sendMessage', {'chat_id': result['message']['chat']['id'],
                                                         'text': respond_text,
                                                         'reply_to_message_id': result['message']['message_id'],})
                else:
                    pass
                    
            # NOTES: recheck to update last_update
            if game_ins and (answer or command in COMMANDS):
                # NOTES: update last_update (last command event occurs)
                game_ins['last_update'] = time.time()
    
                
        last_update_id = int(result['update_id']) + 1
    
    # NOTES: periodic process
    # broadcast
    game_to_saves = []
    for k,game_ins in GAME_OBJ.items():
        created = game_ins['create_date']
        elapsed = time.time() - created
        
        if game_ins['state'] & GAME_STATE_DRAFT:
            if elapsed > GAME_WAIT_BEGIN:
                respond_text = 'Game dibatalkan. ktaa butuh min %s pemain.\n' % (GAME_GROUP_QUOTA)
                json_request('sendMessage', {'chat_id': k,
                                             'text': respond_text,})
                GAME_OBJ.pop(k)
            elif (not game_ins['state'] & GAME_STATE_REMIND_BEGIN_OK) and (elapsed > GAME_WAIT_BEGIN - GAME_REMAINDER_BEGIN):
                respond_text = '%s detik lagi untuk bergabung!\n' % GAME_REMAINDER_BEGIN
                respond_text += 'Gunakan /game untuk bergabung.'
                json_request('sendMessage', {'chat_id': k,
                                             'text': respond_text,})
                game_ins['state'] |= GAME_STATE_REMIND_BEGIN_OK
            else:
                pass
        else:
            if game_ins['state'] & GAME_STATE_RUNNING:
                state = game_ins.get('state', False)
                if elapsed > GAME_DURATION:
                    # NOTES: game finished
                    respond_text = get_finish_text(game_ins)
                    json_request('sendMessage', {'chat_id': k,
                                                 'text': respond_text,})
                    to_save = {'chat_id': k}
                    game_ins['state'] |= GAME_STATE_FINISH
                    to_save.update(game_ins)
                    
                    game_to_saves.append(to_save)
                    
                elif (not state & GAME_STATE_REMIND_OK) and \
                    (elapsed > GAME_DURATION - GAME_REMAINDER):
                    respond_text = '%s detik lagi sebelum game selesai!' % GAME_REMAINDER
                    json_request('sendMessage', {'chat_id': k,
                                                 'text': respond_text,})
                    
                    game_ins['state'] |= GAME_STATE_REMIND_OK
                    
                else:
                    pass

    for game in game_to_saves:
        # NOTES: remove game from game instance object
        GAME_OBJ.pop(game['chat_id'])
        
        gm.store_game(game, POINTS)
    
    time.sleep(GAME_INTERVAL)



