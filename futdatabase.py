# type: ignore[union-attr]

from messages import match_results_msg
import random
import pymongo
from pymongo import MongoClient

# Read .env file
from dotenv import load_dotenv
import os


load_dotenv()

client = pymongo.MongoClient(os.getenv('MONGO_CLIENT_URL'))
db = client["TheFutDatabase"]
tb_jogadores = db["Jogadores"]
tb_futs = db["Futs"]

home_placar = None
away_placar = None
placar_message_id = None
convidado_message_id = None

convidado_nome = ''
convidado_rank = 0
convidado_goleiro = False


class TeamBuilderJogador:
    def __init__(self, id_jogador, rank, goleiro, peita_credits):
        self.id_jogador = id_jogador
        self.rank = rank
        self.goleiro = goleiro
        self.peita_credits = peita_credits

class TeamBuilderTeam:
    def __init__(self, jogadores, goleiro, rank, peita_credits):
        self.jogadores = jogadores
        self.goleiro = goleiro
        self.rank = rank
        self.peita_credits = peita_credits
        


def add_jogador(id_jogador, goleiro):
    jogador_existente = tb_jogadores.find_one({"_id": id_jogador})

    if jogador_existente == None:
        tb_jogadores.insert_one({
            "_id": id_jogador,
            "mensalista": False,
            "goleiro": goleiro,
            "rank": 500,
            "partidas": {
                "total": 0,
                "vitorias": 0,
                "empates": 0,
                "derrotas": 0
            },
            "saldo_gols": {
                "gols_feitos": 0,
                "gols_sofridos": 0
            },
            "peita_credits": 0
            })
        return True
    else:
        tb_jogadores.update_one({"_id": id_jogador}, {"$set":{"goleiro": goleiro}})
        return False

def convert_to_mensalista(id_jogador):
    
    jogador_existente = tb_jogadores.find_one({"_id": id_jogador})
    
    if jogador_existente != None:
        tb_jogadores.update_one({"_id": id_jogador}, {"$set":{"mensalista": True}})
        return True

    return False


def convert_to_diarista(id_jogador):
    
    jogador_existente = tb_jogadores.find_one({"_id": id_jogador})
    
    if jogador_existente != None:
        tb_jogadores.update_one({"_id": id_jogador}, {"$set":{"mensalista": False}})
        return True
    
    return False


def create_fut():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        mensalistas_in_db = tb_jogadores.find({"mensalista": True})
        mensalistas = []
        for pymongo_mensalista in mensalistas_in_db:
            mensalistas.append(pymongo_mensalista["_id"])

        tb_futs.insert_one({
            "_id": "chamada_pro_fut",
            "message_id": None,
            "confirmados": mensalistas,
            "convidados":[],
            "times":{
                "home":[],
                "away":[]
            }
        })

    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    confirmados = chamada_fut["confirmados"]

    return confirmados


def set_vemprofut_message_id(message_id):
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    tb_futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"message_id": message_id}})

def get_vemprofut_message_id():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    return None if chamada_fut == None else chamada_fut["message_id"]

def cancela_fut():

    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return False

    tb_futs.delete_one({"_id": "chamada_pro_fut"})
    return True


def going_to_fut(id_jogador):
    
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    
    for confirmado in confirmados:
        if confirmado == id_jogador:
            return confirmados

    confirmados.append(id_jogador)
    tb_futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"confirmados": confirmados}})
    return confirmados


def not_going_to_fut(id_jogador):
    
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    if (len(confirmados) == 0):
        return confirmados

    confirmados.remove(id_jogador)
    tb_futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"confirmados": confirmados}})

    return confirmados


def invite():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})

    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    for confirmado in confirmados:
        if confirmado == convidado_nome:
            return confirmados


    convidados = chamada_fut["convidados"]
    convidados.append([convidado_nome, calculate_convidado_rank(), convidado_goleiro])

    confirmados.append(convidado_nome)

    tb_futs.update_one({"_id": "chamada_pro_fut"},{
        "$set":{
            "confirmados": confirmados,
            "convidados": convidados
            }
        })

    return confirmados


def uninvite(conv_nome):
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    if (len(confirmados) == 0):
        return confirmados

    confirmados.remove(conv_nome)

    convidados = chamada_fut["convidados"]
    for i in range(len(convidados)):
        if convidados[i][0] == conv_nome:
            del convidados[i]
    
    tb_futs.update_one({"_id": "chamada_pro_fut"},{
        "$set":{
            "confirmados": confirmados,
            "convidados": convidados
            }
        })

    return confirmados


def calculate_convidado_rank():
    jogadores = tb_jogadores.find()
    max_rank = 0
    min_rank = 9999
    for jogador in jogadores:
        curr_rank = jogador["rank"]
        if curr_rank > max_rank:
            max_rank = curr_rank
        if curr_rank < min_rank:
            min_rank = curr_rank

    print(f'min: {min_rank} max: {max_rank}')
    
    conv_rank = ((max_rank - min_rank) * convidado_rank) + min_rank

    return conv_rank


def get_convidados_nomes():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})

    if chamada_fut == None:
        return None

    convidados = chamada_fut["convidados"]
    convidados_nomes = []
    for convidado in convidados:
        convidados_nomes.append(convidado[0])

    return convidados_nomes


def get_confirmados():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    return confirmados


def fazer_times():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return None

    convidados = chamada_fut["convidados"]

    times = [TeamBuilderTeam([],None,0,0), TeamBuilderTeam([],None,0,0)]

    id_confirmados = chamada_fut["confirmados"]
    limite_jogadores = len(id_confirmados)/2
    print(f"Limite de jogadores: {limite_jogadores}")
    if (limite_jogadores == 0):
        return None

    confirmados = []
    for id_confirmado in id_confirmados:
        if id_confirmado[:1] == '@':
            print (f"encontrado {id_confirmado} entre mensalistas")

            confirmado_data = tb_jogadores.find_one({"_id": id_confirmado})
            confirmado = TeamBuilderJogador(id_jogador=id_confirmado, rank=confirmado_data["rank"], goleiro=confirmado_data["goleiro"], peita_credits=confirmado_data["peita_credits"])
            confirmados.append(confirmado)
        else:
            confirmado_data = []
            for convidado in convidados:
                if convidado[0] == id_confirmado:
                    
                    print (f"encontrado {id_confirmado} entre convidados")
                    
                    confirmado = TeamBuilderJogador(id_jogador=id_confirmado, rank=convidado[1], goleiro=convidado[2], peita_credits=0)
                    confirmados.append(confirmado)
            
    confirmados.sort(key=lambda x: x.rank, reverse=True)

    for confirmado in confirmados:
        if not confirmado.goleiro or (len(times[0].jogadores) > 0 and len(times[1].jogadores) > 0):
            continue

        id_time = 0 if len(times[0].jogadores) == 0 else 1
        times[id_time].jogadores.append(confirmado.id_jogador)
        times[id_time].rank += confirmado.rank
        times[id_time].peita_credits += confirmado.peita_credits
        times[id_time].goleiro = confirmado.id_jogador

    for confirmado in confirmados:
        if confirmado.id_jogador == times[0].goleiro or confirmado.id_jogador == times[1].goleiro:
            continue
        
        id_time = 0
        if len(times[0].jogadores) >= limite_jogadores and len(times[1].jogadores) < limite_jogadores:
            id_time = 1
        elif len(times[1].jogadores) >= limite_jogadores and len(times[0].jogadores) < limite_jogadores:
            id_time = 0
        else:
            id_time = 0 if times[0].rank <= times[1].rank else 1
        
        times[id_time].jogadores.append(confirmado.id_jogador)
        times[id_time].rank += confirmado.rank
        times[id_time].peita_credits += confirmado.peita_credits

    for time in times:
        time.jogadores.sort()

    home_id = 0
    away_id = 1
    if times[0].peita_credits > times[1].peita_credits:
        home_id = 1
        away_id = 0
    
    home = {
        "rank": times[home_id].rank,
        "goleiro": times[home_id].goleiro,
        "jogadores": times[home_id].jogadores
    }
    away = {
        "rank": times[away_id].rank,
        "goleiro": times[away_id].goleiro,
        "jogadores": times[away_id].jogadores
    }

    tb_futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"times": {"home": home["jogadores"], "away": away["jogadores"]}}})

    return [home, away]

def get_times():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return None

    return [chamada_fut["times"]["home"],chamada_fut["times"]["home"]]


def register_match():
    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return False

    tb_futs.insert_one({
        "times":{
            "home":chamada_fut["times"]["home"],
            "away":chamada_fut["times"]["away"],
        },
        "placar":{
            "home": home_placar,
            "away": away_placar,
        }
    })

    for id_jogador_home in chamada_fut["times"]["home"]:
        if id_jogador_home[:1] == '@':
            update_jogador(id_jogador_home, home_placar, away_placar, True)
    for id_jogador_away in chamada_fut["times"]["away"]:
        if id_jogador_away[:1] == '@':
            update_jogador(id_jogador_away, home_placar, away_placar, False)
    
    # away_placar = None
    # home_placar = None
    match_results_msg = None
    cancela_fut()

def update_jogador(id_jogador, home_placar, away_placar, is_jogador_home):
    jogador_in_tb = tb_jogadores.find_one({"_id": id_jogador})
    
    # Calcula novo rank
    rank_to_add = 0

    if home_placar > away_placar:
        rank_to_add += 50
    elif home_placar < away_placar:
        rank_to_add -= 50

    rank_to_add += (home_placar - away_placar) * 10
    
    if not is_jogador_home:
        rank_to_add *= -1

    new_rank = jogador_in_tb["rank"] + rank_to_add

    tb_jogadores.update_one({"_id": id_jogador}, {"$set":{
        "rank": new_rank,
        "peita_credits": jogador_in_tb["peita_credits"] + (1 if is_jogador_home else -1),
        "partidas": {
            "total": jogador_in_tb["partidas"]["total"] + 1,
            "vitorias": (jogador_in_tb["partidas"]["vitorias"] + 1) if home_placar > away_placar and is_jogador_home or home_placar < away_placar and not is_jogador_home else jogador_in_tb["partidas"]["vitorias"],
            "empates": (jogador_in_tb["partidas"]["empates"] + 1) if home_placar == away_placar else jogador_in_tb["partidas"]["empates"],
            "derrotas": (jogador_in_tb["partidas"]["derrotas"] + 1) if home_placar < away_placar and is_jogador_home or home_placar > away_placar and not is_jogador_home else jogador_in_tb["partidas"]["derrotas"]
        },
        "saldo_gols": {
            "gols_feitos": jogador_in_tb["saldo_gols"]["gols_feitos"] + (home_placar if is_jogador_home else away_placar),
            "gols_sofridos": jogador_in_tb["saldo_gols"]["gols_feitos"] + (home_placar if not is_jogador_home else away_placar)
        }
        }})