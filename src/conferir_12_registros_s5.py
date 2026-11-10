"""Conferência de 12 registros (3 por persona, seed 42), recalculando do bruto com lógica independente.

Uso (na raiz):  .venv/bin/python src/conferir_12_registros_s5.py [--saida PASTA]
Entrada: dados/processados/s5_leo/segmentos.csv (gerado por src/clusterizacao_s5.py --k 4) e dados/brutos/.
Saída (padrão dados/saidas/s5_kiril/): conferencia_tres_registros.md e conferencia_registros/<user_id>_atividades.csv.
Não altera dados/brutos. Regras e sorteio: ver src/conferencia_comum_s5.py.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conferencia_comum_s5 import bate, carregar_brutos, carregar_segmentos, comparar, indexar_atividades, sortear_12  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NOMES = {0: "Adormecidos (Distantes)", 1: "Rotina em casa (Engajados em casa)",
         2: "Rua e ritmo (Engajados ao ar livre)", 3: "Novatos (Recém-chegados)"}


def formatar(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{v:.4f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=ROOT / "dados/saidas/s5_kiril")
    out = ap.parse_args().saida
    csv_dir = out / "conferencia_registros"
    csv_dir.mkdir(parents=True, exist_ok=True)

    seg = carregar_segmentos(ROOT)
    _, rows_de = indexar_atividades(ROOT)
    alvo = sortear_12(seg, rows_de)
    print("sorteados:", len(alvo))

    T = carregar_brutos(ROOT / "dados/brutos", alvo)
    seg_i = seg.set_index("user_id")
    blocos, resumo = [], []
    for u in sorted(alvo, key=lambda x: (alvo[x][0], alvo[x][1])):
        k, papel = alvo[u]
        s = seg_i.loc[u]
        comp, x = comparar(u, s, rows_de(u), T)
        pd.DataFrame([{
            "atividade_id": a["atividade_id"], "origem": a["origem"], "inicio_bruto": a["inicio"],
            "inicio_brasilia": a["ts"].strftime("%Y-%m-%d %H:%M"), "tipo_bruto": a["tipo"], "tipo_pt": a["tipo_pt"],
            "duracao_min": a["duracao_min"], "video": a["video"], "copia_do_app": a["copia"],
            "valido": a["valido"], "na_janela_90d": a["na_janela90"]} for a in sorted(x["ann"], key=lambda a: a["ts"])]
        ).to_csv(csv_dir / f"{u}_atividades.csv", index=False)
        linhas = [(nome, mine, pipe, bate(mine, pipe, tol)) for nome, mine, pipe, tol in comp]
        resumo.append((NOMES[k], papel, u, sum(1 for *_, b in linhas if b), len(linhas), [n for n, *_, b in linhas if not b]))
        ult, m, sa = x["ult"], x["m"], x["sa"]
        bloco = [f"### {u}  ·  {NOMES[k]}  ·  {papel}", "",
                 f"- Segmento atribuído pelo K-means: **{NOMES[k]}** (não dá para refazer à mão; confira se o perfil abaixo é coerente com a tabela do segmento).",
                 f"- Cadastro: {x['cad']:%d/%m/%Y}; assinatura ativa desde {x['inicio']:%d/%m/%Y} ({sa.plano_atual}, {sa.canal_cobranca}); relógio: {s.relogio_conectado}; canal de aquisição: {s.canal_aquisicao}.",
                 f"- Treinos brutos: {x['n_rows']} (cópias do app removidas: {m['copias_removidas']}; duração zero: {m['duracao_zero']}). Linhas em `conferencia_registros/{u}_atividades.csv`.",
                 f"- Última cobrança aprovada: {ult.ts:%d/%m/%Y %H:%M} · R$ {ult.cent / 100:.2f} · {ult.metodo}.",
                 f"- Renovação desligada: retrato={x['ren_snap']}; último evento de renovação={x['ren_ev']}.",
                 f"- Valor da variação de treinos que entrou no K-means: {x['var30_kmeans']} (regra do Leo: só é zerada quando a conta tem menos de 60 dias).",
                 f"- Objetivo declarado (onboarding): {x['obj']!r}.", "",
                 "| Métrica | Recalculado do bruto | Base do grupo | Confere |", "|---|---:|---:|:---:|"]
        bloco += [f"| {nome} | {formatar(mine)} | {formatar(pipe)} | {'✓' if bom else '✗'} |" for nome, mine, pipe, bom in linhas]
        blocos.append("\n".join(bloco) + "\n")

    cab = ["# Conferência de 3 registros por persona", "",
           "Recalculado do `dados/brutos/` com lógica independente do pipeline do grupo (regras do `AGENTS.md`, `decisoes.md` e dicionário). Seed 42.", "",
           "**Critério de escolha (por segmento):** A = sorteio simples; B = pessoa com relógio garmin e pelo menos uma cópia do app (exercita a correção de fuso e a deduplicação); C = caso de borda do segmento.", "",
           "| Persona | Papel | user_id | Confere |", "|---|---|---|---:|"]
    for nome, papel, u, n_ok, n, falhas in resumo:
        cab.append(f"| {nome} | {papel.split(' (')[0]} | `{u}` | {n_ok}/{n}" + (f" — ✗ {', '.join(falhas)}" if falhas else "") + " |")
    (out / "conferencia_tres_registros.md").write_text("\n".join(cab) + "\n\n" + "\n".join(blocos), encoding="utf-8")
    print("\n".join(cab))


if __name__ == "__main__":
    main()
