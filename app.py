from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

app = Flask(__name__)

def hitung_lampu_hijau(val_kepadatan, val_antrean):
    kepadatan = ctrl.Antecedent(np.arange(0, 101, 1), 'kepadatan')
    antrean   = ctrl.Antecedent(np.arange(0, 151, 1), 'antrean')
    durasi = ctrl.Consequent(np.arange(0, 61, 1), 'durasi', defuzzify_method='mom')

    kepadatan['sepi']   = fuzzy.trimf(kepadatan.universe, [0, 0, 50])
    kepadatan['normal'] = fuzzy.trimf(kepadatan.universe, [25, 50, 75])
    kepadatan['ramai']  = fuzzy.trimf(kepadatan.universe, [50, 100, 100])

    antrean['pendek']  = fuzzy.trimf(antrean.universe, [0, 0, 75])
    antrean['sedang']  = fuzzy.trimf(antrean.universe, [40, 75, 110])
    antrean['panjang'] = fuzzy.trimf(antrean.universe, [75, 150, 150])

    durasi['cepat']  = fuzzy.trimf(durasi.universe, [0, 0, 30])
    durasi['sedang'] = fuzzy.trimf(durasi.universe, [15, 30, 45])
    durasi['lama']   = fuzzy.trimf(durasi.universe, [30, 60, 60])

    rule1 = ctrl.Rule(kepadatan['ramai'] | antrean['panjang'], durasi['lama'])
    rule2 = ctrl.Rule(kepadatan['normal'], durasi['sedang'])
    rule3 = ctrl.Rule(kepadatan['sepi'] & antrean['pendek'], durasi['cepat'])

    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem([rule1, rule2, rule3]))
    sim.input['kepadatan'] = val_kepadatan
    sim.input['antrean']   = val_antrean
    sim.compute()
    return sim.output['durasi']

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    kepadatan = 0
    antrean = 0
    if request.method == 'POST':
        kepadatan = int(request.form.get('kepadatan', 0))
        antrean   = int(request.form.get('antrean', 0))
        hasil = round(hitung_lampu_hijau(kepadatan, antrean), 1)
    return render_template('index.html', hasil=hasil, kepadatan=kepadatan, antrean=antrean)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
