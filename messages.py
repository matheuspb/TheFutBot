def vem_pro_fut_msg(confirmados):
    confirmados_string = ""
    for confirmado in confirmados:
        confirmados_string = confirmados_string + ("✅ " + confirmado + "\n")

    return f"""VEM PRO FUT

{len(confirmados)} Confirmados:
{confirmados_string}
Mensalistas são automaticamente confirmados para cada Fut.
"""