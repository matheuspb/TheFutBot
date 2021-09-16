
# type: ignore[union-attr]

import passwords
import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient(passwords.MONGO_CLIENT_URL)
db = client["TheFutDatabase"]
jogadores = db["Jogadores"]
futs = db["Futs"]

def add_jogador(id_jogador, goleiro):
    jogador_existente = jogadores.find_one({"_id": id_jogador})

    if jogador_existente == None:
        jogadores.insert_one({
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
            }})
        return True
    else:
        jogadores.update_one({"_id": id_jogador}, {"$set":{"goleiro": goleiro}})
        return False

def convert_to_mensalista(id_jogador):
    
    jogador_existente = jogadores.find_one({"_id": id_jogador})
    
    if jogador_existente != None:
        jogadores.update_one({"_id": id_jogador}, {"$set":{"mensalista": True}})
        return True

    return False


def convert_to_diarista(id_jogador):
    
    jogador_existente = jogadores.find_one({"_id": id_jogador})
    
    if jogador_existente != None:
        jogadores.update_one({"_id": id_jogador}, {"$set":{"mensalista": False}})
        return True
    
    return False


def create_fut():

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        mensalistas_in_db = jogadores.find({"mensalista": True})
        mensalistas = []
        for pymongo_mensalista in mensalistas_in_db:
            mensalistas.append(pymongo_mensalista["_id"])

        futs.insert_one({
            "_id": "chamada_pro_fut",
            "confirmados": mensalistas
        })

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    confirmados = chamada_fut["confirmados"]

    return confirmados


def cancela_fut():

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return False

    futs.delete_one({"_id": "chamada_pro_fut"})
    return True


def going_to_fut(id_jogador):
    
    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    
    for confirmado in confirmados:
        if confirmado == id_jogador:
            return confirmados

    confirmados.append(id_jogador)
    futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"confirmados": confirmados}})
    return confirmados


def not_going_to_fut(id_jogador):
    
    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    
    if chamada_fut == None:
        return None

    confirmados = chamada_fut["confirmados"]
    if (len(confirmados) == 0):
        return confirmados

    confirmados.remove(id_jogador)
    futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"confirmados": confirmados}})

    return confirmados