# You must run `setupenv.sh` separately

# 1. GET RAW DATA
python 01Get/01-Reanalysis.py
python 01Get/02-Rainfall.py
python 01Get/03-S2S-Data.py
python 01Get/04-DailyIndices.py
python 01Get/05-MonthlyIndices.py
python 01Get/06-Anomalies.py

# 2. RUN ANALYSIS
function JUPCONV(){
  jupyter nbconvert --execute $1
}
JUPCONV 02Analysis/01-StudyArea.ipynb
JUPCONV 02Analysis/02-Climatology-Anomalies.ipynb
JUPCONV 02Analysis/03-Get-WTs.ipynb
JUPCONV 02Analysis/04-WT-Plots.ipynb
JUPCONV 02Analysis/05-Lagged-Rain.ipynb
JUPCONV 02Analysis/06-S2S-Skill.ipynb
JUPCONV 02Analysis/07-Jet-Extension.ipynb

# 3. WRITEUP
latexmk -cd -e -f -pdf -interaction=nonstopmode "03Writeup/paper.tex"
