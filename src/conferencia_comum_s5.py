"""Recálculo independente de métricas por pessoa, a partir de dados/brutos, para conferir segmentos.csv.

Módulo comum às conferências de 12 e de 96 registros. Não importa nada de preparar_diagnostico_s5.py nem de
clusterizacao_s5.py: as regras vêm de AGENTS.md, decisoes.md e do dicionário, para a conferência ser independente
do código do pipeline. Limite dessa independência: se uma REGRA documentada estiver errada, os dois lados erram juntos.

Regras aplicadas
- Corte exclusivo 01/10/2026 00:00 (Brasília); janela de 90 dias = [03/07, 01/10); 30 dias = [01/09, 01/10).
- Datas com sufixo Z são UTC (-3h); sem sufixo já são Brasília. Treinos do garmin gravam em UTC (-3h).
- Cópia do app = linha do app com mesmo tipo (como veio), mesma duração e início a até 5 min de uma linha de relógio.
- Treino válido: duração > 0, não é cópia, em 2026 antes do corte. Vídeo = força, funcional, HIIT, ioga
  (após padronizar run/walk/strength/ride para português).
- Assinatura: a linha ativa de assinaturas.csv. Receita = última cobrança aprovada (sem duplicadas
  user_id + instante + valor), ÷ 12 no plano anual, menos taxa do método (app_store/google_play 15%,
  cartão 3,5%, pix 0,99%).
- segmentos.csv guarda os valores ANTES do tratamento do K-means. Por isso se comparam:
    * variação de treinos: valor bruto (30d - 30d anteriores); o zero para contas com menos de 60 dias
      só vale na matriz do K-means (a tendência incompleta é conferida à parte);
    * recência: vazia para quem não treinou em 2026 (o 273 só existe na matriz do K-means).

Sorteios (importa a ordem das chamadas ao gerador aleatório e a ordem das linhas de segmentos.csv):
- `sortear_12`: seed 42; por segmento A (rng.choice), B (rng.shuffle de garmin; 1º dos 400 primeiros com cópia do app
  e treino em 90 dias) e C (rng.choice entre os casos de borda).
- `sortear_96`: seed 96; quotas por persona (8 A + 8 B + 4 C1 + 4 C2), sem os registros da amostra de 12.
Ambos são sorteios por QUOTAS, com bordas escolhidas de propósito: não são amostras probabilísticas da base, e zero
falhas NÃO autoriza limite populacional de erro (a regra de três só vale para amostra aleatória simples).
"""
import datetime as dt
import random
import re
import unicodedata

import pandas as pd

CUT = dt.datetime(2026, 10, 1)
D90, D60, D30 = CUT - dt.timedelta(days=90), CUT - dt.timedelta(days=60), CUT - dt.timedelta(days=30)
IN2026 = dt.datetime(2026, 1, 1)
NOMES = {0: "Adormecidos", 1: "Rotina em casa", 2: "Rua e ritmo", 3: "Novatos"}
TIPO_EN = {"run": "corrida", "walk": "caminhada", "strength": "forca", "ride": "pedal"}
VIDEO = {"forca", "funcional", "hiit", "yoga"}
FEE = {"app_store": 0.15, "google_play": 0.15, "cartao": 0.035, "pix_automatico": 0.0099}
COLS_ATIVIDADES = ["atividade_id", "user_id", "inicio", "tipo", "duracao_min", "origem"]


def when(s):
    s = str(s).strip()
    if s.endswith("Z"):
        return dt.datetime.fromisoformat(s[:-1]).replace(tzinfo=None) - dt.timedelta(hours=3)
    return dt.datetime.fromisoformat(s)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"\s+", " ", s)


def atividades_do_usuario(rows):
    """rows: lista de dicts crus de atividades.parquet. Devolve (linhas anotadas, métricas)."""
    ann = []
    for r in rows:
        ts = when(r["inicio"])
        if r["origem"] == "garmin":
            ts -= dt.timedelta(hours=3)
        ann.append(dict(r, ts=ts, tipo_pt=TIPO_EN.get(r["tipo"], r["tipo"]), copia=False))
    relogio = [a for a in ann if a["origem"] != "app"]
    for a in ann:
        if a["origem"] == "app":
            for w in relogio:
                if (w["tipo"] == a["tipo"] and w["duracao_min"] == a["duracao_min"]
                        and abs((a["ts"] - w["ts"]).total_seconds()) <= 300):
                    a["copia"] = True
                    break
    for a in ann:
        a["valido"] = bool(a["duracao_min"] and a["duracao_min"] > 0 and not a["copia"] and IN2026 <= a["ts"] < CUT)
        a["video"] = a["tipo_pt"] in VIDEO
        a["na_janela90"] = a["valido"] and a["ts"] >= D90
    v90 = [a for a in ann if a["na_janela90"]]
    v_all = [a for a in ann if a["valido"]]
    m = {
        "treinos_90d": len(v90),
        "dias_ativos_90d": len({a["ts"].date() for a in v90}),
        "min_por_treino_90d": (sum(a["duracao_min"] for a in v90) / len(v90)) if v90 else None,
        "proporcao_video_90d": (sum(a["video"] for a in v90) / len(v90)) if v90 else None,
        "treinos_30d": sum(1 for a in v_all if a["ts"] >= D30),
        "treinos_30d_anteriores": sum(1 for a in v_all if D60 <= a["ts"] < D30),
        "recencia_dias": round((CUT - max(a["ts"] for a in v_all)).total_seconds() / 86400, 2) if v_all else None,
        "copias_removidas": sum(1 for a in ann if a["copia"]),
        "duracao_zero": sum(1 for a in ann if not (a["duracao_min"] and a["duracao_min"] > 0)),
    }
    return ann, m


def bate(mine, pipe, tol):
    """tol None = igualdade exata (texto); senão diferença absoluta máxima. Vazio só bate com vazio."""
    if tol is None:
        return (mine == pipe) or (mine is None and pipe is None)
    if mine is None or (isinstance(mine, float) and pd.isna(mine)):
        return pipe is None or pd.isna(pipe)
    if pipe is None or pd.isna(pipe):
        return False
    return abs(float(mine) - float(pipe)) <= tol


def diferenca(mine, pipe):
    try:
        return abs(float(mine) - float(pipe))
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ dados
def carregar_segmentos(raiz):
    """segmentos.csv + colunas de cadastro usadas nos sorteios (mantém a ordem das linhas de segmentos.csv)."""
    usu = pd.read_csv(raiz / "dados/brutos/usuarios.csv")
    seg = pd.read_csv(raiz / "dados/processados/s5_leo/segmentos.csv")
    return seg.merge(usu[["user_id", "data_cadastro", "relogio_conectado", "canal_aquisicao"]], on="user_id", how="left")


def indexar_atividades(raiz):
    """Devolve (tabela de atividades, função rows_de(user_id) -> lista de dicts crus)."""
    atv = pd.read_parquet(raiz / "dados/brutos/atividades.parquet", columns=COLS_ATIVIDADES)
    idx = atv.set_index("user_id").sort_index()

    def rows_de(u):
        try:
            return idx.loc[[u]].reset_index().to_dict("records")
        except KeyError:
            return []

    return atv, rows_de


def carregar_brutos(B, ids):
    """Lê os brutos e filtra só as pessoas conferidas. B = pasta dados/brutos."""
    ids = set(ids)
    ass = pd.read_csv(B / "assinaturas.csv")
    ass = ass[ass.user_id.isin(ids) & (ass.status_atual == "ativa")].set_index("user_id")
    ev = pd.read_csv(B / "eventos_assinatura.csv")
    pg = pd.read_csv(B / "pagamentos.csv", dtype=str)
    fp = pd.read_csv(B / "feed_posts.csv", usecols=["post_id", "user_id", "data_hora"])
    tk = pd.read_csv(B / "tickets_suporte.csv", usecols=["ticket_id", "user_id", "aberto_em"])
    am = pd.read_csv(B / "amizades.csv")
    ob = pd.read_csv(B / "onboarding.csv")
    cm = pd.read_csv(B / "campanha_ago26.csv")
    usu = pd.read_csv(B / "usuarios.csv")
    return dict(
        ass=ass,
        ev=ev[ev.user_id.isin(ids)],
        pg=pg[pg.user_id.isin(ids) & (pg.status == "aprovado")],
        fp=fp[fp.user_id.isin(ids)],
        tk=tk[tk.user_id.isin(ids)],
        am=am[am.seguido_id.isin(ids)],
        ob=ob[ob.user_id.isin(ids)].set_index("user_id"),
        cm=cm[cm.user_id.isin(ids)],
        usu=usu[usu.user_id.isin(ids)].set_index("user_id"),
    )


# ------------------------------------------------------------------ sorteios
def sortear_12(seg, rows_de, seed=42):
    """Seed 42: 3 pessoas por segmento. Devolve {user_id: (segmento, papel)}."""
    rng = random.Random(seed)
    alvo = {}
    for k in range(4):
        pool = seg[seg.segmento == k]
        alvo[rng.choice(list(pool.user_id))] = (k, "A. sorteio simples (seed 42)")
        cand = list(pool[pool.relogio_conectado == "garmin"].user_id)
        rng.shuffle(cand)
        achou = None
        for u in cand[:400]:
            if u in alvo:
                continue
            _, m = atividades_do_usuario(rows_de(u))
            if m["copias_removidas"] >= 1 and m["treinos_90d"] >= 1:
                achou = u
                break
        alvo[achou] = (k, "B. com garmin e cópia do app (exercita fuso e duplicidade)")
        if k == 0:
            c = pool[(pool.sem_treino_90d == 1) & ~pool.user_id.isin(alvo)]
            papel = "C. borda: nenhum treino em 90 dias"
        elif k == 3:
            c = pool[(pool.exposicao_dias < 90) & ~pool.user_id.isin(alvo)]
            papel = "C. borda: conta com menos de 90 dias"
        else:
            c = pool[(pool.renovacao_desligada_retrato == 1) & ~pool.user_id.isin(alvo)]
            papel = "C. borda: renovação automática desligada"
        alvo[rng.choice(list(c.user_id))] = (k, papel)
    return alvo


BORDAS_96 = {
    0: [("C1", "borda: sem treino em 90 dias", lambda d: d.sem_treino_90d == 1),
        ("C2", "borda: renovação desligada, com treino", lambda d: (d.renovacao_desligada_retrato == 1) & (d.sem_treino_90d == 0))],
    1: [("C1", "borda: renovação desligada", lambda d: d.renovacao_desligada_retrato == 1),
        ("C2", "borda: ticket em 90 dias", lambda d: d.tickets_90d >= 1)],
    2: [("C1", "borda: renovação desligada", lambda d: d.renovacao_desligada_retrato == 1),
        ("C2", "borda: ticket em 90 dias", lambda d: d.tickets_90d >= 1)],
    3: [("C1", "borda: conta com menos de 30 dias", lambda d: d.exposicao_dias < 30),
        ("C2", "borda: conta de 30 a 89 dias", lambda d: (d.exposicao_dias >= 30) & (d.exposicao_dias < 90))],
}


def sortear_96(seg, atv_all, excluidos, seed=96):
    """Seed 96: 24 por segmento, sem os `excluidos`. seg deve estar na ordem de segmentos.csv.
    Devolve {user_id: (segmento, papel, rótulo)}."""
    seg = seg[~seg.user_id.isin(excluidos)]
    rng = random.Random(seed)
    cand_garmin = {}
    for k in range(4):  # os 4 embaralhamentos vêm antes de qualquer sorteio
        c = list(seg[(seg.segmento == k) & (seg.relogio_conectado == "garmin")].user_id)
        rng.shuffle(c)
        cand_garmin[k] = c[:250]
    todos = [u for k in cand_garmin for u in cand_garmin[k]]
    atv_cand = {u: g.to_dict("records") for u, g in atv_all[atv_all.user_id.isin(todos)].groupby("user_id")}
    alvo = {}
    for k in range(4):
        pool = seg[seg.segmento == k]
        for u in rng.sample(list(pool.user_id), 8):
            alvo[u] = (k, "A", "sorteio simples")
        n = 0
        for u in cand_garmin[k]:
            if u in alvo:
                continue
            _, m = atividades_do_usuario(atv_cand.get(u, []))
            if m["copias_removidas"] >= 1 and m["treinos_90d"] >= 1:
                alvo[u] = (k, "B", "garmin + cópia do app")
                n += 1
                if n == 8:
                    break
        assert n == 8, (k, n)
        for letra, rotulo, mask in BORDAS_96[k]:
            c = pool[mask(pool) & ~pool.user_id.isin(alvo)]
            for u in rng.sample(list(c.user_id), 4):
                alvo[u] = (k, letra, rotulo)
    assert len(alvo) == 96 and not (set(alvo) & set(excluidos))
    return alvo


# ------------------------------------------------------------------ recálculo por pessoa
def comparar(u, s, rows, T):
    """Recalcula as 17 métricas de uma pessoa. s = linha de segmentos.csv; rows = atividades cruas da pessoa.
    Devolve (lista de (nome, recalculado, base, tolerância), extras)."""
    ann, m = atividades_do_usuario(rows)
    sa = T["ass"].loc[u]
    inicio = dt.datetime.fromisoformat(str(sa.inicio)[:10])
    ren_snap = int(str(sa.renovacao_automatica).lower() == "nao")
    e_u = T["ev"][T["ev"].user_id == u].copy()
    e_u["ts"] = e_u.data_hora.map(when)
    e_ren = e_u[e_u.evento.isin(["renovacao_automatica_desligada", "renovacao_automatica_religada", "cancelamento_web"])].sort_values("ts")
    ren_ev = None if e_ren.empty else int(e_ren.iloc[-1].evento in ("renovacao_automatica_desligada", "cancelamento_web"))

    p = T["pg"][T["pg"].user_id == u].copy()
    p["ts"] = p.data_hora.map(when)
    p["cent"] = p.valor.map(lambda v: round(float(str(v).replace("R$", "").replace(" ", "").replace(",", ".")) * 100))
    p = p.drop_duplicates(["ts", "cent"]).sort_values("ts", kind="stable")
    ult = p.iloc[-1]
    receita = ult.cent / 100 / (12 if sa.plano_atual == "anual" else 1) * (1 - FEE[ult.metodo])

    posts90 = sum(1 for t in (when(x) for x in T["fp"][T["fp"].user_id == u].data_hora) if D90 <= t < CUT)
    tick90 = sum(1 for t in (when(x) for x in T["tk"][T["tk"].user_id == u].aberto_em) if D90 <= t < CUT)
    segs = sum(1 for t in (when(x) for x in T["am"][T["am"].seguido_id == u].desde) if t < CUT)

    cad = when(T["usu"].loc[u].data_cadastro)
    exp_a = min(90, (CUT - cad).days + 1)
    exp_b = min(90, (CUT.date() - cad.date()).days + 1)
    exposicao = exp_a if exp_a == s.exposicao_dias else exp_b
    obu = T["ob"].loc[u] if u in T["ob"].index else None
    nivel = obu.nivel if obu is not None else None
    obj = obu.objetivo_texto if obu is not None else None
    taxa = (m["dias_ativos_90d"] / exposicao) if exposicao else None
    var30 = m["treinos_30d"] - m["treinos_30d_anteriores"]
    dias_conta_mais_1 = (CUT - cad).days + 1
    var30_kmeans = 0 if dias_conta_mais_1 < 60 else var30

    comp = [
        ("dias com treino em 90 dias", m["dias_ativos_90d"], s.dias_ativos_90d, 0),
        ("minutos por treino (média, 90d)", m["min_por_treino_90d"], s.min_por_treino_90d if m["treinos_90d"] else None, 1e-6),
        ("proporção em vídeo (90d)", m["proporcao_video_90d"], s.proporcao_video_90d if m["treinos_90d"] else None, 1e-6),
        ("dias desde o último treino", m["recencia_dias"], s.recencia_dias, 0.011),
        ("variação de treinos (30d − 30d anteriores)", var30, s.variacao_treinos_30d, 0),
        ("tendência incompleta (conta < 60 dias)", int(dias_conta_mais_1 < 60), s.tendencia_incompleta, 0),
        ("exposição (dias de conta, máx. 90)", exposicao, s.exposicao_dias, 0),
        ("frequência (dias ativos ÷ exposição)", taxa, s.taxa_dias_ativos_90d, 1e-6),
        ("posts em 90 dias", posts90, s.posts_90d, 0),
        ("seguidores no corte", segs, s.seguidores_corte, 0),
        ("tickets em 90 dias", tick90, s.tickets_90d, 0),
        ("tempo de assinatura (dias)", (CUT - inicio).days, s.tempo_assinatura_dias, 1),
        ("plano", sa.plano_atual, s.plano, None),
        ("canal de cobrança", sa.canal_cobranca, s.canal_cobranca, None),
        ("renovação desligada (retrato 01/10)", ren_snap, s.renovacao_desligada_retrato, 0),
        ("receita líquida mensal equivalente (R$)", round(receita, 4), round(float(s.receita_liquida_mensal_equivalente_proxy), 4), 1e-3),
        ("nível (onboarding)", norm(nivel) if nivel is not None and not pd.isna(nivel) else None,
         norm(s.nivel) if not pd.isna(s.nivel) else None, None),
    ]
    extras = dict(ann=ann, m=m, sa=sa, inicio=inicio, ren_snap=ren_snap, ren_ev=ren_ev, ult=ult, cad=cad,
                  obj=obj, var30_kmeans=var30_kmeans, n_rows=len(rows))
    return comp, extras
