# -*- coding: utf-8 -*-
"""
M4 | Desenvolvimento de Simulador para uma Fila
Disciplina: Simulacao e Metodos Analiticos

Simulador de eventos discretos para UMA fila G/G/c/K.

Conforme orientado no modulo, o codigo foi mantido propositalmente simples:
variaveis globais, funcoes soltas (sem classes) e parametros da fila
definidos diretamente no codigo (hardcode), sem entrada via terminal.

Etapas implementadas:
  Etapa 1 - Gerador de numeros pseudoaleatorios (Metodo Congruente Linear)
  Etapa 2 - Loop principal da simulacao
  Etapa 3 - Tratamento dos eventos de CHEGADA e SAIDA
  Etapa 4 - Calculo dos tempos acumulados e das probabilidades dos estados
  Etapa 5 - Analise e interpretacao dos resultados (ver README.md)
"""

# =============================================================================
# ETAPA 1 - GERADOR DE NUMEROS PSEUDOALEATORIOS (Metodo Congruente Linear)
# =============================================================================
#   Xn+1 = (a * Xn + c) mod M
# Parametros de Numerical Recipes: periodo completo M = 2^32 (a-1 multiplo de 4
# e c primo relativo a M), o que garante que os 100.000 numeros solicitados
# nunca repetem a sequencia.

A = 1664525           # multiplicador
C = 1013904223        # incremento
M = 4294967296        # modulo (2^32)
SEMENTE = 7           # valor inicial da sequencia (seed)

anterior = SEMENTE            # ultimo numero gerado da sequencia
aleatorios_restantes = 0      # contador de aleatorios (criterio de parada)
aleatorios_usados = 0         # quantos aleatorios foram efetivamente consumidos


def NextRandom():
    """Retorna o proximo pseudoaleatorio normalizado no intervalo [0, 1)."""
    global anterior, aleatorios_restantes, aleatorios_usados
    anterior = ((A * anterior) + C) % M
    aleatorios_restantes -= 1
    aleatorios_usados += 1
    return anterior / M


def temAleatorio():
    """Ainda restam numeros pseudoaleatorios a serem utilizados?"""
    return aleatorios_restantes > 0


def uniforme(menor, maior):
    """Sorteia um tempo uniformemente distribuido no intervalo [menor, maior]."""
    return menor + (maior - menor) * NextRandom()


# =============================================================================
# PARAMETROS DA FILA E ESTADO GLOBAL DA SIMULACAO
# =============================================================================

K = 5                 # capacidade total da fila (clientes no sistema)
SERVIDORES = 1        # quantidade de servidores (o "c" de G/G/c/K)

CHEGADA_MIN = 3.0     # intervalo entre chegadas
CHEGADA_MAX = 5.0
ATEND_MIN = 4.0       # tempo de atendimento
ATEND_MAX = 5.0

fila = 0              # numero de clientes atualmente no sistema (estado da fila)
tempo_global = 0.0    # relogio da simulacao
tempos = []           # tempos acumulados em cada estado (indices 0..K)
perdas = 0            # clientes perdidos (chegaram com a fila cheia)

escalonador = []      # lista de eventos agendados: (tempo, tipo, ordem)
ordem_insercao = 0    # desempate para eventos agendados no mesmo tempo

TIPO_CHEGADA = "CHEGADA"
TIPO_SAIDA = "SAIDA"


# =============================================================================
# ESCALONADOR DE EVENTOS
# =============================================================================

def agenda(tipo, tempo):
    """Agenda um evento no escalonador para o instante informado."""
    global ordem_insercao
    ordem_insercao += 1
    escalonador.append((tempo, tipo, ordem_insercao))


def NextEvent():
    """Retira do escalonador o evento agendado com o menor tempo."""
    menor = 0
    for i in range(1, len(escalonador)):
        if escalonador[i][0] < escalonador[menor][0]:
            menor = i
        elif escalonador[i][0] == escalonador[menor][0]:
            if escalonador[i][2] < escalonador[menor][2]:
                menor = i
    return escalonador.pop(menor)


def agendaChegada():
    """Agenda a proxima chegada, consumindo um numero pseudoaleatorio."""
    if temAleatorio():
        agenda(TIPO_CHEGADA, tempo_global + uniforme(CHEGADA_MIN, CHEGADA_MAX))


def agendaSaida():
    """Agenda a proxima saida, consumindo um numero pseudoaleatorio."""
    if temAleatorio():
        agenda(TIPO_SAIDA, tempo_global + uniforme(ATEND_MIN, ATEND_MAX))


# =============================================================================
# ETAPA 4 (parcial) - CONTABILIZACAO DOS TEMPOS ACUMULADOS
# =============================================================================

def acumulaTempo(tempo_do_evento):
    """Acumula, no estado atual da fila, o tempo decorrido ate o evento."""
    global tempo_global
    tempos[fila] += tempo_do_evento - tempo_global
    tempo_global = tempo_do_evento


# =============================================================================
# ETAPA 3 - TRATAMENTO DOS EVENTOS DE CHEGADA E SAIDA
# =============================================================================

def CHEGADA(tempo_do_evento):
    """Trata a chegada de um cliente na fila."""
    global fila, perdas
    acumulaTempo(tempo_do_evento)
    if fila < K:                      # ha espaco na fila
        fila += 1
        if fila <= SERVIDORES:        # ha servidor livre -> ja entra em atendimento
            agendaSaida()
    else:                             # fila cheia -> cliente perdido
        perdas += 1
    agendaChegada()                   # agenda a chegada do proximo cliente


def SAIDA(tempo_do_evento):
    """Trata a saida (fim de atendimento) de um cliente da fila."""
    global fila
    acumulaTempo(tempo_do_evento)
    fila -= 1
    if fila >= SERVIDORES:            # ainda ha cliente aguardando para ser atendido
        agendaSaida()


# =============================================================================
# ETAPA 2 - LOOP PRINCIPAL DA SIMULACAO
# =============================================================================

def simula(servidores, capacidade, chegada_min, chegada_max,
           atend_min, atend_max, qtd_aleatorios, semente, primeira_chegada):
    """Prepara o estado global, executa o laco principal e devolve o resultado."""
    global SERVIDORES, K, CHEGADA_MIN, CHEGADA_MAX, ATEND_MIN, ATEND_MAX
    global fila, tempo_global, tempos, perdas, escalonador, ordem_insercao
    global anterior, aleatorios_restantes, aleatorios_usados

    # --- configuracao da fila ------------------------------------------------
    SERVIDORES = servidores
    K = capacidade
    CHEGADA_MIN = chegada_min
    CHEGADA_MAX = chegada_max
    ATEND_MIN = atend_min
    ATEND_MAX = atend_max

    # --- estado inicial: fila vazia ------------------------------------------
    fila = 0
    tempo_global = 0.0
    tempos = [0.0] * (K + 1)
    perdas = 0
    escalonador = []
    ordem_insercao = 0

    # --- gerador -------------------------------------------------------------
    anterior = semente
    aleatorios_restantes = qtd_aleatorios
    aleatorios_usados = 0

    # --- primeiro cliente chega no tempo informado (nao consome aleatorio) ----
    agenda(TIPO_CHEGADA, primeira_chegada)

    # --- laco principal: executa enquanto houver aleatorios a utilizar -------
    count = aleatorios_restantes
    while count > 0 and len(escalonador) > 0:
        tempo_do_evento, tipo, _ = NextEvent()
        if tipo == TIPO_CHEGADA:
            CHEGADA(tempo_do_evento)
        elif tipo == TIPO_SAIDA:
            SAIDA(tempo_do_evento)
        count = aleatorios_restantes

    return {
        "tempos": list(tempos),
        "tempo_global": tempo_global,
        "perdas": perdas,
        "aleatorios_usados": aleatorios_usados,
        "K": K,
        "servidores": SERVIDORES,
    }


# =============================================================================
# ETAPA 4 - RELATORIO: TEMPOS ACUMULADOS E DISTRIBUICAO DE PROBABILIDADES
# =============================================================================

def relatorio(titulo, r, chegada_min, chegada_max, atend_min, atend_max,
              semente, primeira_chegada):
    linhas = []
    p = linhas.append
    p("=" * 72)
    p(titulo)
    p("=" * 72)
    p("")
    p("  Modelo ..................: G/G/%d/%d" % (r["servidores"], r["K"]))
    p("  Chegadas ................: entre %.1f e %.1f" % (chegada_min, chegada_max))
    p("  Atendimento .............: entre %.1f e %.1f" % (atend_min, atend_max))
    p("  Primeira chegada ........: %.1f" % primeira_chegada)
    p("  Estado inicial da fila ..: vazia")
    p("  Gerador (MCL) ...........: a=%d  c=%d  M=%d  seed=%d" % (A, C, M, semente))
    p("  Numeros aleatorios ......: %d" % r["aleatorios_usados"])
    p("")
    p("  " + "-" * 66)
    p("  %-8s %20s %22s" % ("Estado", "Tempo acumulado", "Probabilidade"))
    p("  " + "-" * 66)
    total = r["tempo_global"]
    for i in range(r["K"] + 1):
        prob = (r["tempos"][i] / total * 100.0) if total > 0 else 0.0
        p("  %-8d %20.4f %21.4f%%" % (i, r["tempos"][i], prob))
    p("  " + "-" * 66)
    soma = sum(r["tempos"])
    p("  %-8s %20.4f %21.4f%%" % ("TOTAL", soma, (soma / total * 100.0) if total else 0.0))
    p("")
    p("  Tempo global da simulacao .....: %.4f" % r["tempo_global"])
    p("  Numero de perdas de clientes ..: %d" % r["perdas"])
    p("")
    return "\n".join(linhas)


# =============================================================================
# MAIN
# =============================================================================

def main():
    QTD_ALEATORIOS = 100000
    SEED = SEMENTE
    PRIMEIRA_CHEGADA = 3.0

    # Cenarios solicitados no enunciado da entrega:
    #   G/G/1/5, chegadas entre 3...5, atendimento entre 4...5
    #   G/G/2/5, chegadas entre 3...5, atendimento entre 4...5
    cenarios = [
        ("SIMULACAO 1  |  G/G/1/5  |  chegadas 3...5  |  atendimento 4...5",
         1, 5, 3.0, 5.0, 4.0, 5.0),
        ("SIMULACAO 2  |  G/G/2/5  |  chegadas 3...5  |  atendimento 4...5",
         2, 5, 3.0, 5.0, 4.0, 5.0),
    ]

    saida = []
    for titulo, srv, cap, cmin, cmax, amin, amax in cenarios:
        r = simula(servidores=srv, capacidade=cap,
                   chegada_min=cmin, chegada_max=cmax,
                   atend_min=amin, atend_max=amax,
                   qtd_aleatorios=QTD_ALEATORIOS, semente=SEED,
                   primeira_chegada=PRIMEIRA_CHEGADA)
        saida.append(relatorio(titulo, r, cmin, cmax, amin, amax,
                               SEED, PRIMEIRA_CHEGADA))

    texto = "\n".join(saida)
    print(texto)

    import os
    os.makedirs("resultados", exist_ok=True)
    with open(os.path.join("resultados", "resultados.txt"), "w", encoding="utf-8") as f:
        f.write(texto)


if __name__ == "__main__":
    main()
