import json
import random
import sqlite3
import time

import game_logic

SEED = long(str(long(time.time()*1000))[-5:])

def db_con():
    con = sqlite3.connect(r'data/game_data.db')
    
    return con

def get_last_grid_id():
    con = db_con()
    cur = con.cursor()
    query = '''\
select id from grid order by id desc limit 1;'''
    cur.execute(query)
    res = cur.fetchone()
    grid_id = res[0] + 1
    
    return grid_id

def create_grid(last_id=False):
    con = db_con()
    if not last_id:
        grid_id = get_last_grid_id() + 1
    
    try:
        game = game_logic.make_game()
    except:
        cur.close()
        con.close()

        return False
    
    data = json.dumps(game)
    
    cur = con.cursor()
    query = '''\
insert into grid (id, json) values (?, ?);'''
    cur.execute(query, (grid_id, data))
    con.commit()    
    
    cur.close()
    con.close()
    
    return True
 
def get_available_grid(chat_id):
    con = db_con()
    cur = con.cursor()
    query = '''\
select id from grid a 
where not id in (
    select grid_id from game_instance where chat_id = ?)'''
    cur.execute(query, (chat_id,))
    res = cur.fetchall()
    result = random.choice([x[0] for x in res])
    
    con.close()
    return result
 
def get_game(chat_id):
    '''\
{u'grid': u'rntf utma aagl shna',
 'id': 9,
 u'keywords': u'mahatur,untal,lang',
 u'solutions': u'aga,agah,agal,agam,agama,agan,agas,ahsan,ala,alaf,alam,alamah,alamas,alamat,alang,alat,alga,ama,amah,amal,aman,amang,amat,ana,anal,angah,asa,asah,asam,asan,asana,atas,atau,atma,atman,atur,aur,fam,gah,gala,galan,galat,gam,gama,gamal,gaman,gamat,gana,ganal,ganas,gas,gaun,gaut,ham,hama,hamal,hana,hang,hangat,has,hasan,hatta,hatur,haur,laga,lagam,lagan,lagau,lam,lama,laman,lamang,lana,lanau,lang,langah,langau,lat,latma,mag,mah,maha,mahatur,mal,mala,malan,malang,man,mana,mang,mas,masa,mat,mata,matu,matur,mau,maut,naga,nagam,nah,nahas,nal,nala,nalam,nama,nas,natur,nur,nutan,rua,ruah,ruam,ruang,ruas,ruat,runtas,saat,saga,sah,saham,sahan,sahang,sama,sana,sang,sanga,sangat,sangha,sat,satang,satu,sau,saur,saut,taf,tagal,tagan,tah,tahan,tahana,tahang,tal,tala,talang,tam,tamah,taman,tamat,tan,tang,tas,tasa,tau,taun,taur,tua,tuah,tuam,tuan,tuang,tuas,tun,tur,uan,uang,unta,untal,utama,utang,utas'}'''    

    grid_id = get_available_grid(chat_id)
    
    con = db_con()
    cur = con.cursor()
    query = '''\
select * from grid where id = ?'''
    cur.execute(query, (grid_id,))
    
    res = cur.fetchone()
    if not res:
        game = {'id': grid_id, 'error': 'not_found'}
    else:
        game = {'id': res[0],}
        game.update(json.loads(res[1]))    
        
    cur.close()
    con.close()
    
    return game

def store_game(game, points):
    # {'chat_type': u'private', 
    #  'game': {'id': 67,}, 
    #  'create_date': 1472467820.975, 
    #  'chat_id': -242989999, 
    #  'answer': {u'-xxx-$666986515': [u'gila', u'kita'],
    #             u'-yyy-$999986515': [u'aku', u'hilaf']}, 
    #  'state': int}
    # 
    # structure
    # create table game_instance (id integer primary key, grid_id integer, chat_type text,  chat_id integer, state text, create_date real);
    #
    # create table answer (game_id integer, user_name text, user_id int, score int);
    result = True
    game_id = long(str(long(game['create_date']*1000))[-5:]) + SEED
    con = db_con()
    cur = con.cursor()
    query = '''\
insert into game_instance (id, grid_id, chat_type, chat_id, state, create_date) values
(?, ?, ?, ?, ?, ?);'''

    try:
        cur.execute(query, (game_id, game['game']['id'], game['chat_type'], 
                            game['chat_id'], str(game['state']), game['create_date']))

        for user, ans in game['answer'].items():
        
            user_name, user_id = user.split('$')
            user_id = int(user_id)
            score = sum([points[len(x)] for x in ans])

            query2 = '''\
insert into answer (game_id, user_name, user_id, score) values
(?, ?, ?, ?);'''
        
            cur.execute(query2, (game_id, user_name, user_id, score))
                
        con.commit()
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]
        print query
        print query2
        result = False
    
    con.close()
           
    return result

def get_score(chat_id):
    # get sorted top score
    con = db_con()
    cur = con.cursor()
    query = '''\
select b.user_name, sum(b.score) score from game_instance a 
left join answer b on a.id = b.game_id 
where chat_id = ? and b.score is not null
group by b.user_id
order by score desc
limit 10;'''
    cur.execute(query, (chat_id,))
    res = cur.fetchall()
    result = []
    for r in res:
        result.append({'user_name': r[0],
                       'score': r[1]})
    return result
    
if __name__ == '__main__':
    # testing
    POINTS = {3: 1,
          4: 1,
          5: 2,
          6: 3,
          7: 5,
          8: 11}
    game = {'chat_type': u'private', 
            'game': {'id': 67,}, 
            'create_date': 1472467820.975, 
            'chat_id': -242989999, 
            'answer': {u'-xxx-$666986515': [u'gila', u'kita'],
                       u'-yyy-$999986515': [u'aku', u'hilaf']}, 
            'state': 5}
    # store_game(game, POINTS)
    
    # chat_id = 242986515#-173640045
    # res = get_score(chat_id)
    # print res
    
    # print get_available_grid(-242989999)
    # print get_game(-242989999)
    