from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

app = Flask(__name__)

# --- LOGIKA FUZZY (OTAK SISTEM) ---
def hitung_lampu_hijau(val_kepadatan, val_antrean):
    # 1. Semesta Pembicaraan (Batas nilai)
    kepadatan = ctrl.Antecedent(np.arange(0, 101, 1), 'kepadatan') # 0-100 kendaraan
    antrean = ctrl.Antecedent(np.arange(0, 151, 1), 'antrean')     # 0-150 meter
    durasi = ctrl.Consequent(np.arange(0, 61, 1), 'durasi')        # 0-60 detik

    # 2. Himpunan Fuzzy (Membership Function)
    kepadatan['sepi'] = fuzzy.trimf(kepadatan.universe, [0, 0, 50])
    kepadatan['normal'] = fuzzy.trimf(kepadatan.universe, [25, 50, 75])
    kepadatan['ramai'] = fuzzy.trimf(kepadatan.universe, [50, 100, 100])

    antrean['pendek'] = fuzzy.trimf(antrean.universe, [0, 0, 75])
    antrean['sedang'] = fuzzy.trimf(antrean.universe, [40, 75, 110])
    antrean['panjang'] = fuzzy.trimf(antrean.universe, [75, 150, 150])

    durasi['cepat'] = fuzzy.trimf(durasi.universe, [0, 0, 30])
    durasi['sedang'] = fuzzy.trimf(durasi.universe, [15, 30, 45])
    durasi['lama'] = fuzzy.trimf(durasi.universe, [30, 60, 60])

    # 3. Aturan Pakar (Rules)
    rule1 = ctrl.Rule(kepadatan['ramai'] | antrean['panjang'], durasi['lama'])
    rule2 = ctrl.Rule(kepadatan['normal'], durasi['sedang'])
    rule3 = ctrl.Rule(kepadatan['sepi'] & antrean['pendek'], durasi['cepat'])

    # 4. Mesin Inferensi
    sistem_kontrol = ctrl.ControlSystem([rule1, rule2, rule3])
    simulasi = ctrl.ControlSystemSimulation(sistem_kontrol)

    # 5. Masukkan nilai dari user
    simulasi.input['kepadatan'] = val_kepadatan
    simulasi.input['antrean'] = val_antrean
    
    # 6. Hitung hasil defuzzifikasi
    simulasi.compute()
    return simulasi.output['durasi']

# --- ROUTING WEB (TAMPILAN) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    kepadatan = 0
    antrean = 0
    
    if request.method == 'POST':
        # Ambil data dari form HTML
        kepadatan = int(request.form.get('kepadatan', 0))
        antrean = int(request.form.get('antrean', 0))
        
        # Masukkan ke fungsi Fuzzy
        hasil_mentah = hitung_lampu_hijau(kepadatan, antrean)
        hasil = round(hasil_mentah, 1) # Bulatkan 1 angka di belakang koma
        
    return render_template('index.html', hasil=hasil, kepadatan=kepadatan, antrean=antrean)

if __name__ == '__main__':
    # Pakai port 8000 biar aman dari error bawaan Windows
    app.run(debug=True, port=8000)