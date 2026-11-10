"""Revisão técnica das personas de Kiril; evidências individuais somente em dados/.

Não implementa o conferidor original de Kiril: faz uma nova checagem independente
das pessoas selecionadas por seeds ou PDFs locais, contra o pipeline de Leo reproduzido.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess
import types

import numpy as np
import pandas as pd
from pypdf import PdfReader
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
LEO_SHA = "eafaf08a246ed5470d31dce7c63fd2c196788fc3"
BASE_SHA = "8d408862735fb1faec3cd43c8fbbf338544be484"
CUT = pd.Timestamp("2026-10-01")
NAMES = {0: "Adormecidos", 1: "Rotina em casa", 2: "Rua e ritmo", 3: "Novatos"}
FEES = {"app_store": .15, "google_play": .15, "cartao": .035, "pix_automatico": .0099}


def local_time(value):
    t = pd.Timestamp(value)
    return t.tz_convert("America/Sao_Paulo").tz_localize(None) if t.tzinfo else t


def cents(value):
    return int(Decimal(str(value).replace("R$", "").strip().replace(",", ".")) * 100)


def sample_ids(path, count):
    text = "\n".join(p.extract_text() for p in PdfReader(path).pages)
    ids = re.findall(r"\bu_[0-9a-f]{8}\b", text)
    assert len(ids) == len(set(ids)) == count, "Amostra ausente, duplicada ou incompleta"
    return ids


def independent_metrics(uid, raw):
    """Recálculo por pessoa, sem chamar funções de preparação/clusterização."""
    u = raw["usuarios"].loc[lambda d: d.user_id.eq(uid)].iloc[0]
    sub = raw["assinaturas"].loc[lambda d: d.user_id.eq(uid) & d.status_atual.eq("ativa")]
    assert len(sub) == 1
    sub = sub.iloc[0]
    rows = []
    for r in raw["atividades"].loc[lambda d: d.user_id.eq(uid)].to_dict("records"):
        r["time"] = local_time(r["inicio"]) - pd.Timedelta(hours=3 if r["origem"] == "garmin" else 0)
        rows.append(r)
    # Matches use original spelling, before normalization, and conserve the watch.
    watches = {}
    for r in rows:
        if r["origem"] != "app":
            watches.setdefault((r["tipo"], r["duracao_min"]), []).append(r["time"])
    clean = [r for r in rows if not (r["origem"] == "app" and any(
        abs((r["time"] - t).total_seconds()) <= 300
        for t in watches.get((r["tipo"], r["duracao_min"]), [])))]
    valid = [r for r in clean if r["duracao_min"] > 0 and pd.Timestamp("2026-01-01") <= r["time"] < CUT]
    window = [r for r in valid if r["time"] >= CUT - pd.Timedelta(days=90)]
    recent = sum(r["time"] >= CUT - pd.Timedelta(days=30) for r in valid)
    earlier = sum(CUT - pd.Timedelta(days=60) <= r["time"] < CUT - pd.Timedelta(days=30) for r in valid)
    exposure = min(90, (CUT - local_time(u.data_cadastro)).days + 1)
    days = len({r["time"].date() for r in window})
    videos = {"forca", "strength", "funcional", "hiit", "yoga"}
    def count_window(table, col):
        return sum(CUT - pd.Timedelta(days=90) <= local_time(v) < CUT
                   for v in raw[table].loc[lambda d: d.user_id.eq(uid), col])
    payments = []
    for r in raw["pagamentos"].loc[lambda d: d.user_id.eq(uid) & d.status.eq("aprovado")].to_dict("records"):
        r["time"] = local_time(r["data_hora"])
        if r["time"] < CUT:
            payments.append(r)
    # Duplicates have the same amount and timestamp; keeping one preserves last charge.
    p = sorted(payments, key=lambda r: r["time"])[-1]
    revenue = cents(p["valor"]) / 100 / (12 if sub.plano_atual == "anual" else 1) * (1 - FEES[p["metodo"]])
    ob = raw["onboarding"].loc[lambda d: d.user_id.eq(uid)]
    ob = ob[ob.respondido_em.map(local_time).lt(CUT)]
    assert len(ob) <= 1
    friends = raw["amizades"].loc[lambda d: d.seguido_id.eq(uid)]
    return {
        "dias_ativos_90d": days,
        "min_por_treino_90d": np.mean([r["duracao_min"] for r in window]) if window else np.nan,
        "proporcao_video_90d": sum(r["tipo"] in videos for r in window) / len(window) if window else np.nan,
        "recencia_dias": (CUT - max(r["time"] for r in valid)).total_seconds() / 86400 if valid else np.nan,
        "variacao_treinos_30d": recent - earlier,
        "tendencia_incompleta": int((CUT - local_time(u.data_cadastro)).days + 1 < 60),
        "exposicao_dias": exposure,
        "taxa_dias_ativos_90d": days / exposure,
        "posts_90d": count_window("feed_posts", "data_hora"),
        "seguidores_corte": sum(local_time(v) < CUT for v in friends.desde),
        "tickets_90d": count_window("tickets_suporte", "aberto_em"),
        "tempo_assinatura_dias": (CUT - local_time(sub.inicio)).days,
        "plano": sub.plano_atual,
        "canal_cobranca": sub.canal_cobranca,
        "renovacao_desligada_retrato": int(sub.renovacao_automatica == "nao"),
        "receita_liquida_mensal_equivalente_proxy": revenue,
        "nivel": ob.iloc[0].nivel if len(ob) else np.nan,
    }


def agrees(actual, expected, tolerance=0):
    if pd.isna(actual) or pd.isna(expected):
        return bool(pd.isna(actual) and pd.isna(expected))
    if isinstance(actual, str) or isinstance(expected, str):
        return actual == expected
    return abs(actual - expected) <= tolerance


def load_leo():
    source = subprocess.check_output(["git", "show", f"{LEO_SHA}:src/clusterizacao_s5.py"], cwd=ROOT, text=True)
    mod = types.ModuleType("leo_referencia")
    mod.__file__ = str(ROOT / "src/clusterizacao_s5.py")
    exec(compile(source, f"leo@{LEO_SHA}", "exec"), mod.__dict__)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf-12", type=Path)
    ap.add_argument("--pdf-96", type=Path)
    ap.add_argument("--amostras-seeds", action="store_true", help="Reproduzir amostras pelas seeds 42/96 sem PDFs")
    args = ap.parse_args()
    reference = subprocess.check_output(["git", "show", f"{BASE_SHA}:src/preparar_diagnostico_s5.py"], cwd=ROOT)
    assert reference == (ROOT / "src/preparar_diagnostico_s5.py").read_bytes(), "Preparação mudou: revisar a referência"
    prepared = json.loads((ROOT / "dados/processados/s5_john/manifesto_validacao.json").read_text())
    out = ROOT / "dados/saidas/s5_kiril_revisao"
    out.mkdir(parents=True, exist_ok=True)
    if not args.amostras_seeds and (args.pdf_12 is None or args.pdf_96 is None):
        ap.error("Informe --amostras-seeds ou os dois PDFs de referência")
    paths = {p.stem: p for p in (ROOT / "dados/brutos").glob("*.csv")}
    paths["atividades"] = ROOT / "dados/brutos/atividades.parquet"
    hashes = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in paths.items()}
    assert all(hashes[k] == value for k, value in prepared["sha256_brutos"].items()), "Fontes diferem da preparação"
    raw = {k: pd.read_csv(p, keep_default_na=False, na_values=[""], low_memory=False)
           for k, p in paths.items() if k != "atividades"}
    raw["atividades"] = pd.read_parquet(paths["atividades"])
    leo = load_leo()
    base, context = leo.carregar()
    f, x, treatments = leo.preparar(base, context)
    with threadpool_limits(limits=1):
        z = leo.padronizar(x)
        # Full sweep preserves RNG advancement of the published k=4 stability test.
        sweep = leo.varrer_k(z)
        labels = leo.ajustar(z, 4)
        order = pd.Series(f.taxa_dias_ativos_90d.values).groupby(labels).mean().sort_values().index
        labels = pd.Series(labels).map({old: new for new, old in enumerate(order)}).to_numpy()
        profile, detailed = leo.perfil(f, context, labels)
        ward = leo.comparar_ward(z, labels, 4)
    detailed.to_csv(out / "segmentos_reproduzidos.csv", index=False)
    sweep.to_csv(out / "varredura_reproduzida.csv", index=False)
    assert profile.assinantes.tolist() == [2783, 4315, 4793, 2862]
    assert len(detailed) == detailed.user_id.nunique() == 14753
    if args.amostras_seeds:
        from conferencia_comum_s5 import indexar_atividades, sortear_12, sortear_96
        all_activities, rows_for = indexar_atividades(ROOT)
        sample_context = detailed.merge(raw["usuarios"][["user_id", "data_cadastro", "relogio_conectado", "canal_aquisicao"]], on="user_id", validate="1:1")
        first = sortear_12(sample_context, rows_for)
        samples = {12: list(first), 96: list(sortear_96(sample_context, all_activities, set(first)))}
    else:
        samples = {12: sample_ids(args.pdf_12, 12), 96: sample_ids(args.pdf_96, 96)}
    assert not set(samples[12]) & set(samples[96]), "Amostras se sobrepõem"
    checks = []
    tolerances = {"min_por_treino_90d": 1e-6, "proporcao_video_90d": 1e-6,
                  "taxa_dias_ativos_90d": 1e-6, "recencia_dias": .01,
                  "tempo_assinatura_dias": 1, "receita_liquida_mensal_equivalente_proxy": .001}
    for n, ids in samples.items():
        assert set(ids) <= set(detailed.user_id)
        assert detailed[detailed.user_id.isin(ids)].groupby("segmento").size().tolist() == [n // 4] * 4
        indexed = detailed.set_index("user_id")
        for uid in ids:
            metrics = independent_metrics(uid, raw)
            assert len(metrics) == 17
            for name, actual in metrics.items():
                expected = indexed.loc[uid, name]
                checks.append({"amostra": n, "user_id": uid, "metrica": name,
                               "recalculado": actual, "pipeline": expected,
                               "confere": agrees(actual, expected, tolerances.get(name, 0))})
    checks = pd.DataFrame(checks)
    checks.to_csv(out / "comparacoes_individuais.csv", index=False)
    per_metric = checks.groupby(["amostra", "metrica"]).confere.agg(["size", "sum"])
    per_metric.to_csv(out / "conferencia_agregada.csv")
    # Context enrichment for persona tables; no individual text is exported publicly.
    users = raw["usuarios"].copy()
    demo = detailed.merge(users, on="user_id", validate="1:1")
    demo["idade"] = (CUT - pd.to_datetime(demo.data_nascimento, errors="coerce")).dt.days / 365.25
    demo["relogio"] = demo.relogio_conectado.notna() & ~demo.relogio_conectado.astype(str).str.lower().isin(["nenhum", "nao", "não", ""])
    demo["influenciador"] = demo.canal_aquisicao.eq("influenciador")
    demo["mulher"] = demo.sexo.astype("string").str.strip().str.lower().isin(["f", "fem", "feminino"])
    demo["homem"] = demo.sexo.astype("string").str.strip().str.lower().isin(["m", "masc", "masculino"])
    demo["ios"] = demo.sistema.astype("string").str.strip().str.lower().eq("ios")
    demo["sudeste"] = demo.uf.isin(["SP", "RJ", "MG", "ES"])
    extras = demo.groupby("segmento").agg(idade_mediana=("idade", "median"),
        relogio_pct=("relogio", lambda s: s.mean() * 100),
        influenciador_pct=("influenciador", lambda s: s.mean() * 100),
        mulheres_pct=("mulher", lambda s: s.mean() * 100),
        homens_pct=("homem", lambda s: s.mean() * 100),
        ios_pct=("ios", lambda s: s.mean() * 100),
        sudeste_pct=("sudeste", lambda s: s.mean() * 100))
    profile.join(extras).to_csv(out / "perfil_revisado.csv")
    campaign = raw["campanha_ago26"].merge(detailed[["user_id", "segmento"]], on="user_id", validate="1:1")
    campaign[campaign.grupo.ne("controle")].groupby(["segmento", "grupo"]).agg(
        destinatarios=("user_id", "size"), cliques=("clicou", "sum"),
        clique_pct=("clicou", lambda s: s.mean() * 100)).to_csv(out / "campanha_revisada.csv")
    # Historical cadence can challenge, but cannot confirm, a future renewal date.
    events = raw["eventos_assinatura"].copy()
    events["ts"] = events.data_hora.map(local_time)
    events = events[events.ts.lt(CUT)]
    annual = events[events.plano.eq("anual") & events.evento.eq("renovacao")].merge(
        raw["assinaturas"][["user_id", "inicio"]], on="user_id", validate="many_to_one")
    annual["same_month_day"] = annual.ts.dt.strftime("%m-%d").eq(pd.to_datetime(annual.inicio).dt.strftime("%m-%d"))
    # Reproduce Kiril's anniversary scenario, explicitly a hypothetical window.
    scenario = detailed.merge(raw["assinaturas"][["user_id", "inicio"]], on="user_id", validate="1:1")
    scenario["anniversary_2026"] = pd.to_datetime(scenario.inicio).map(lambda t: t.replace(year=2026) if (t.month, t.day) != (2, 29) else t.replace(year=2026, day=28))
    dormant_off = scenario[scenario.segmento.eq(0) & scenario.renovacao_desligada_retrato.eq(1)]
    window = dormant_off[dormant_off.plano.eq("anual") & dormant_off.anniversary_2026.between("2026-10-01", "2026-11-29")]
    off = detailed[detailed.renovacao_desligada_retrato.eq(1)]
    manifest = {
        "pipeline_base_sha": BASE_SHA,
        "pipeline_leo_sha": LEO_SHA, "sha256_brutos": hashes,
        "sha256_segmentos": hashlib.sha256((out / "segmentos_reproduzidos.csv").read_bytes()).hexdigest(),
        "sha256_base_clusterizacao": hashlib.sha256((ROOT / "dados/processados/s5_john/base_clusterizacao.csv").read_bytes()).hexdigest(),
        "sha256_contexto": hashlib.sha256((ROOT / "dados/processados/s5_john/base_assinantes_corte.csv").read_bytes()).hexdigest(),
        "sha256_pdf_12": hashlib.sha256(args.pdf_12.read_bytes()).hexdigest() if args.pdf_12 else None,
        "sha256_pdf_96": hashlib.sha256(args.pdf_96.read_bytes()).hexdigest() if args.pdf_96 else None,
        "origem_amostras": "seeds 42/96" if args.amostras_seeds else "PDFs",
        "versoes": {"pandas": pd.__version__, "numpy": np.__version__, "sklearn": __import__("sklearn").__version__},
        "comparacoes": {str(n): {"total": int((checks.amostra == n).sum()), "concordantes": int(checks.loc[checks.amostra.eq(n), "confere"].sum())} for n in samples},
        "recencia_ausente": int(f.recencia_dias.isna().sum()),
        "tendencia_incompleta": int(f.tendencia_incompleta.sum()),
        "diferenca_assinatura_amostra": Counter(int(v) for v in (
            checks.loc[checks.metrica.eq("tempo_assinatura_dias"), "recalculado"].astype(float).to_numpy() -
            checks.loc[checks.metrica.eq("tempo_assinatura_dias"), "pipeline"].astype(float).to_numpy())),
        "estabilidade_k4": sweep[sweep.k.eq(4)].iloc[0].to_dict(), "ari_ward": ward,
        "renovacao_desligada_total": len(off),
        "renovacao_desligada_por_segmento": off.groupby("segmento").size().to_dict(),
        "proxy_total": float(detailed.receita_liquida_mensal_equivalente_proxy.sum()),
        "adormecidos_desligados_proxy": float(dormant_off.receita_liquida_mensal_equivalente_proxy.sum()),
        "adormecidos_desligados_anuais": int(dormant_off.plano.eq("anual").sum()),
        "cenario_aniversario_pessoas": len(window),
        "cenario_aniversario_proxy": float(window.receita_liquida_mensal_equivalente_proxy.sum()),
        "eventos_apos_corte": int((raw["eventos_assinatura"].data_hora.map(local_time) >= CUT).sum()),
        "renovacoes_anuais_historicas": len(annual),
        "renovacoes_anuais_mes_dia_inicio": int(annual.same_month_day.sum()),
        "tratamentos": treatments,
    }
    assert hashes == {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in paths.items()}, "Bruto alterado"
    (out / "manifesto.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in manifest.items() if k not in {"sha256_brutos", "tratamentos"}}, indent=2, ensure_ascii=False))
    assert checks.confere.all(), "Divergências: consultar somente o arquivo local de comparações"


if __name__ == "__main__":
    main()
