from flask import Flask, jsonify, request, Response, json
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder='app', static_url_path="/app")
CORS(app)


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.route('/wacc', methods=['GET', 'POST'])
@cross_origin()
def WACC():
    data = request.get_json(force=True)
    W_s_val = float(data.get('Ws', None))
    K_s_val = float(data.get('Ks', None))
    W_d_val = float(data.get('Wd', None))
    K_d_val = float(data.get('Kd', None))
    T_val = float(data.get('T', None))
    if not all([W_d_val, W_s_val, K_d_val, K_s_val, T_val]):
        return Response("Not enough data", 400)
    return Response(str(float(W_s_val * K_s_val + W_d_val * K_d_val * (1 - T_val))), 200)


@app.route('/nopat', methods=['GET', 'POST'])
@cross_origin()
def NOPAT():
    data = request.get_json(force=True)
    EBIT_val = float(data.get('EBIT', None))
    T_val = float(data.get('T', None))
    if not all([EBIT_val, T_val]):
        return Response("Not enough data", 400)
    return Response(str(float(EBIT_val * (1 - T_val))), 200)


@app.route('/ebi', methods=['GET', 'POST'])
@cross_origin()
def EBI():
    data = request.get_json(force=True)
    NI_val = float(data.get('NI', None))
    I_val = float(data.get('I', None))
    T_val = float(data.get('T', None))
    if not all([NI_val, I_val, T_val]):
        return Response("Not enough data", 400)
    return Response(str(float(NI_val + I_val * (1 - T_val))), 200)


@app.route('/rv', methods=['GET', 'POST'])
@cross_origin()
def RV():
    # data = request.get_json(force=True)
    WACC_val = WACC().get_json(force=True)
    EBI_val = EBI().get_json(force=True)
    if not all([WACC_val, EBI_val]):
        return Response("Not enough data", 400)
    resp = {'WACC': WACC_val,
            'EBI': EBI_val}
    resp.update({'RV': str(float(EBI_val / WACC_val))})
    return Response(json.dumps(resp), 200)


@app.route('/ncf', methods=['GET', 'POST'])
@cross_origin()
def NCF():
    data = request.get_json(force=True)
    I_val = float(data.get('I', None))
    EBI_val = EBI().get_json(force=True)
    if not all([EBI_val, I_val]):
        return Response("Not enough data", 400)
    resp = {'EBI': EBI_val}
    resp.update({'NCF': str(float(EBI_val - I_val))})
    return Response(json.dumps(resp), 200)


@app.route('/ed', methods=['GET', 'POST'])
@cross_origin()
def ED():
    data = request.get_json(force=True)
    N_val = float(data.get('N', None))
    GFA_val = float(data.get('GFA', None))
    WACC_val = WACC().get_json(force=True)
    if not all([N_val, GFA_val, WACC_val]):
        return Response("Not enough data", 400)
    resp = {'WACC': WACC_val}
    resp.update({'ED': str(float((GFA_val * WACC_val) / ((1 + WACC_val) ** N_val - 1)))})
    return Response(json.dumps(resp), 200)


@app.route('/cbi', methods=['GET', 'POST'])
@cross_origin()
def CBI():
    data = request.get_json(force=True)
    Dep_val = float(data.get('DEP', None))
    ED_temp = ED().get_json(force=True)
    ED_val = float(ED_temp['ED'])
    WACC_val = float(ED_temp['WACC'])
    EBI_val = EBI().get_json(force=True)
    if not all([Dep_val, ED_val, EBI_val]):
        return Response("Not enough data", 400)
    resp = {'ED': ED_val,
            'WACC': WACC_val,
            'EBI': EBI_val}
    resp.update({'CBI': str(float(EBI_val + Dep_val - ED_val))})
    return Response(json.dumps(resp), 200)


@app.route('/sva', methods=['GET', 'POST'])
@cross_origin()
def SVA():
    data = request.get_json(force=True)
    NCF_temp = NCF().get_json(force=True)
    NCF_val = float(NCF_temp['NCF'])
    EBI_val = float(NCF_temp['EBI'])
    WACC_val = float(WACC().get_json(force=True))
    RV_val = float(RV().get_json(force=True)['RV'])
    N_val = float(data['N'])
    if not all([N_val, NCF_val, EBI_val, WACC_val, RV_val]):
        return Response("Not enough data", 400)
    resp = {'NCF': NCF_val,
            'WACC': WACC_val,
            'EBI': EBI_val,
            'RV': RV_val}
    resp.update({'SVA': str(float((NCF_val / (1 + WACC_val)**N_val) + (RV_val / (1 + WACC_val)**N_val) - (RV_val / (1 + WACC_val)**(N_val - 1))))})
    return Response(json.dumps(resp), 200)


@app.route('/cva', methods=['GET', 'POST'])
@cross_origin()
def CVA():
    data = request.get_json(force=True)
    CBI_temp = CBI().get_json(force=True)
    CBI_val = float(CBI_temp['CBI'])
    ED_val = float(CBI_temp['ED'])
    EBI_val = float(CBI_temp['EBI'])
    NA_val = float(data['NA'])
    WACC_val = float(WACC().get_json(force=True))
    if not all([CBI_val, ED_val, EBI_val, WACC_val, NA_val]):
        return Response("Not enough data", 400)
    resp = {'CBI': CBI_val,
            'WACC': WACC_val,
            'EBI': EBI_val,
            'ED': ED_val}
    resp.update({'CVA': str(float(CBI_val - NA_val * WACC_val))})
    return Response(json.dumps(resp), 200)


@app.route('/cfroi', methods=['GET', 'POST'])
@cross_origin()
def CFROI():
    data = request.get_json(force=True)
    CF_val = float(data.get('CF', None))
    CI_val = float(data.get('CI', None))
    if not all([CF_val, CI_val]):
        return Response("Not enough data", 400)
    return Response(str(float(CF_val/CI_val)), 200)


@app.route('/tsr', methods=['GET', 'POST'])
@cross_origin()
def TSR():
    data = request.get_json(force=True)
    q0 = float(data.get('Q0', None))
    qN = float(data.get('QN', None))
    p0 = float(data.get('P0', None))
    pN = float(data.get('PN', None))
    if not all([q0, qN, p0, pN]):
        return Response("Not enough data", 400)
    return Response(str(float(pN*qN - p0*q0)), 200)


if __name__ == '__main__':
    app.run()
