"""Reproduz as frentes S5 a partir do data room local, sem publicar dados.

Requer requirements-revisao-kiril.txt. Limita threads para reprodução do K-means.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
STEPS=[['preparar_diagnostico_s5.py'],['checagens_qualidade_s5.py'],
       ['valor_priorizacao_s5.py'],['clusterizacao_s5.py','--k','4'],
       ['levantar_personas_s5.py'],['calcular_risco_janela_s5.py'],
       ['conferir_12_registros_s5.py'],['conferir_96_registros_s5.py'],
       ['revisar_personas_kiril_s5.py','--amostras-seeds'],
       ['complementar_entregas_personas_s5.py']]

def main():
    env=os.environ.copy()
    for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','LOKY_MAX_CPU_COUNT']:
        env[name]='1'
    for args in STEPS:
        print('Executando:',args[0],flush=True)
        subprocess.run([sys.executable,str(ROOT/'src'/args[0]),*args[1:]],cwd=ROOT,env=env,check=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,env=env,check=True)
    print('Reprodução concluída. As saídas individuais permanecem em dados/, fora do Git.')

if __name__=='__main__':main()
