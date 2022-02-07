def vem_pro_fut_msg(confirmados):
    confirmados_string = ""
    for confirmado in confirmados:
        confirmados_string = confirmados_string + ("✅ " + confirmado + "\n")

    return f"""VEM PRO FUT

{len(confirmados)} Confirmados:
{confirmados_string}

Para marcar ou desmarcar presença no fut, use os comandos /going e /notgoing, respectivamente.
Mensalistas são automaticamente confirmados para cada Fut.

Quando estiverem prontos, use o comando /times para criar os times.
"""

def times_msg(times):
    home_string = ""
    if times[0]["goleiro"] != None:
        home_string = home_string + ("🧤" + times[0]["goleiro"] + "\n")
    for jogador_home in times[0]["jogadores"]:
        if jogador_home != times[0]["goleiro"]:
            home_string = home_string + (jogador_home + "\n")

    away_string = ""
    if times[1]["goleiro"] != None:
        away_string = away_string + ("🧤" + times[1]["goleiro"] + "\n")
    for jogador_away in times[1]["jogadores"]:
        if jogador_away != times[1]["goleiro"]:
            away_string = away_string + (jogador_away + "\n")

    return f"""🟥 Home    x    Away 🟨 

Home 🟥     ⚽️{times[0]["rank"]}
{home_string}
Away 🟨     ⚽️{times[1]["rank"]}
{away_string}

Jogadores do time Home não se esqueçam de trazer a peita VERMELHA 🟥
Jogadores do time Away não se esqueçam de trazer a peita AMARELA 🟨

Jogadores ainda podem marcar e desmarcar presença no Fut com os comandos /going e /notgoing e o Fut ainda pode ser  cancelado com o comando /cancelafut

Após o Fut, informe o placar com o comando /placar
"""

def placar_input_msg(placar_home, placar_away, error):
    return f"""🟥 Home {'__' if placar_home == None else placar_home} x {'__' if placar_away == None else placar_away} Away 🟨

{'O placar deve conter apenas números' if error else ''}

Por favor, informe o placar do time {'🟥 Home' if placar_home == None else '🟨 Away'}
"""

def match_results_msg(match_results):

    rank_str = ""
    
    if match_results["placar"][0] > match_results["placar"][1]:
        rank_str = "Jogadores do time 🟥 Home ganharam ⚽️{0}.\nJogadores do time 🟨 Away perderam ⚽️{0}.".format((match_results["placar"][0] - match_results["placar"][1]) * 10)
    elif match_results["placar"][0] < match_results["placar"][1]:
        rank_str = "Jogadores do time 🟨 Away ganharam ⚽️{0}.\nJogadores do time 🟥 Home perderam ⚽️{0}.".format((match_results["placar"][1] - match_results["placar"][0]) * 10)
    else:
        rank_str = "Os ranks permanecem os mesmos."


    return f"""⚽️ Resultado ⚽️
    
🟥 Home {match_results["placar"][0]} x {match_results["placar"][1]} Away 🟨

{rank_str}
"""