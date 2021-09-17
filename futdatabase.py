
# type: ignore[union-attr]

import passwords
import random
import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient(passwords.MONGO_CLIENT_URL)
db = client["TheFutDatabase"]
tb_jogadores = db["Jogadores"]
tb_futs = db["Futs"]


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
            "rank": random.randint(0,1000),
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
            "peita_credits": random.randint(0,3)
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
            "message_id": None
            "confirmados": mensalistas,
            "times":{
                "home":[],
                "away":[]
            }
        })

    chamada_fut = tb_futs.find_one({"_id": "chamada_pro_fut"})
    confirmados = chamada_fut["confirmados"]

    return confirmados


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

    times = [TeamBuilderTeam([],None,0,0), TeamBuilderTeam([],None,0,0)]

    id_confirmados = chamada_fut["confirmados"]
    limite_jogadores = len(id_confirmados)/2
    print(f"Limite de jogadores: {limite_jogadores}")
    if (limite_jogadores == 0):
        return None

    confirmados = []
    for id_confirmado in id_confirmados:
        confirmado_data = tb_jogadores.find_one({"_id": id_confirmado})
        confirmado = TeamBuilderJogador(id_jogador=id_confirmado, rank=confirmado_data["rank"], goleiro=confirmado_data["goleiro"], peita_credits=confirmado_data["peita_credits"])
        confirmados.append(confirmado)

    confirmados.sort(key=lambda x: x.rank, reverse=True)

    for confirmado in confirmados:
        if not confirmado.goleiro:
            continue

        id_time = 0 if len(times[0].jogadores) == 0 else 1
        times[id_time].jogadores.append(confirmado.id_jogador)
        times[id_time].rank += confirmado.rank
        times[id_time].peita_credits += confirmado.peita_credits
        times[id_time].goleiro = confirmado.id_jogador

        print(f"Adicionando {confirmado.id_jogador} ao Time {id_time} como goleiro")

    for confirmado in confirmados:
        if confirmado.goleiro:
            continue
        
        id_time = 0
        if len(times[0].jogadores) == limite_jogadores and len(times[1].jogadores) < limite_jogadores:
            id_time = 1
        elif len(times[1].jogadores) == limite_jogadores and len(times[0].jogadores) < limite_jogadores:
            id_time = 0
        else:
            id_time = 0 if times[0].rank <= times[1].rank else 1
        
        times[id_time].jogadores.append(confirmado.id_jogador)
        times[id_time].rank += confirmado.rank
        times[id_time].peita_credits += confirmado.peita_credits

        print(f"Adicionando {confirmado.id_jogador} ao Time {id_time}")

    for time in times:
        time.jogadores.sort()

    print(f'Time 0 ({len(times[0].jogadores)}): {times[0].jogadores}, Rank: {times[0].rank}, Peita Credits: {times[0].peita_credits},')
    print(f'Time 1 ({len(times[1].jogadores)}): {times[1].jogadores}, Rank: {times[1].rank}, Peita Credits: {times[1].peita_credits},')

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

    print(f'Home: {home}')
    print(f'Away: {away}')

    tb_futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"times": {"home": home["jogadores"], "away": away["jogadores"]}}})

    return [home, away]