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

    return f"""Home 🟥  🆚  🟨 Away 

Home 🟥     ⚽️{times[0]["rank"]}
{home_string}
Away 🟨     ⚽️{times[1]["rank"]}
{away_string}

Jogadores do time Home não se esqueçam de trazer a peita VERMELHA 🟥
Jogadores do time Away não se esqueçam de trazer a peita AMARELA 🟨

Jogadores ainda podem marcar e desmarcar presença no Fut com os comandos /going e /notgoing
"""