from flask import Flask, render_template, request, jsonify, session
import os, random, sqlite3
from datetime import datetime, timezone

try:
    import psycopg
except ImportError:
    psycopg = None

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

QUESTIONS = [
    {"q":"¿Qué es un sumidero de carbono?","a":["Un ecosistema que captura más CO₂ del que emite","Una industria que produce madera","Un animal que almacena carbono","Una fuente de contaminación"],"c":0,"d":1},
    {"q":"¿En qué zona de Chile se centra el proyecto?","a":["Norte Grande","Patagonia chilena","Zona Central","Archipiélago Juan Fernández"],"c":1,"d":1},
    {"q":"¿Qué especie invasora aparece como una de las causas principales?","a":["Castor norteamericano","Zorro culpeo","Puma","Cóndor"],"c":0,"d":1},
    {"q":"¿Qué ocurre cuando disminuye la cobertura de bosque nativo?","a":["Aumenta la capacidad de captura de CO₂","Se pierde parte de su capacidad como sumidero","No cambia nada","Desaparece el CO₂ de la atmósfera"],"c":1,"d":1},
    {"q":"¿Qué regiones se mencionan principalmente?","a":["Aysén y Magallanes","Arica y Tarapacá","Maule y Ñuble","Coquimbo y Valparaíso"],"c":0,"d":1},
    {"q":"¿Cuánto disminuyó la cobertura de bosque nativo en los últimos 30 años, según el documento?","a":["5,5%","10%","15,5%","25,5%"],"c":2,"d":1},
    {"q":"¿Qué actividad humana se identifica como causa de la pérdida de cobertura?","a":["Tala e industria maderera","Pesca artesanal","Turismo astronómico","Minería submarina"],"c":0,"d":1},
    {"q":"¿Qué consecuencia ambiental se destaca?","a":["Menor captura de CO₂","Mayor biodiversidad automáticamente","Mayor superficie forestal","Menos necesidad de conservación"],"c":0,"d":1},
    {"q":"¿Qué institución ejecuta la ENCCRV?","a":["CONAF","Banco Central","SERNAC","Dirección Meteorológica"],"c":0,"d":1},
    {"q":"¿Qué tipo de causa representa al castor invasor?","a":["Biológica","Económico-productiva","Geológica","Astronómica"],"c":0,"d":1},
    {"q":"¿Qué tipo de causa representa la tala y la industria maderera?","a":["Biológica","Económico-productiva","Climática exclusivamente","Natural"],"c":1,"d":1},
    {"q":"¿Qué se recomienda consumir respecto de la madera?","a":["Madera certificada","Solo madera importada","Madera sin origen conocido","Madera de cualquier procedencia"],"c":0,"d":1},
    {"q":"Según el CR2, ¿qué proporción de la pérdida de cobertura se atribuyó al castor?","a":["44%","46%","54%","56%"],"c":3,"d":2},
    {"q":"Según el CR2, ¿qué proporción de la pérdida de cobertura se atribuyó a la actividad forestal?","a":["44%","54%","56%","64%"],"c":0,"d":2},
    {"q":"En términos de carbono perdido, ¿qué proporción se atribuye aproximadamente al castor?","a":["44%","46%","54%","56%"],"c":2,"d":2},
    {"q":"En términos de carbono perdido, ¿qué proporción se atribuye aproximadamente a la actividad forestal?","a":["44%","46%","54%","56%"],"c":1,"d":2},
    {"q":"¿Qué estudio citado señala que los bosques nativos de Chiloé pueden almacenar más de mil toneladas de carbono por hectárea?","a":["Un estudio de la Universidad de Chile/Instituto de Ecología y Biodiversidad","Un informe de turismo","Un estudio de pesca","Un informe del Banco Central"],"c":0,"d":2},
    {"q":"¿Qué instrumento climático de Chile fija metas de recuperación y forestación?","a":["La NDC ante el Acuerdo de París","Un reglamento municipal","La ley de tránsito","El censo"],"c":0,"d":2},
    {"q":"¿Cuántas hectáreas de bosque nativo busca recuperar la meta mencionada en la NDC?","a":["20.000","100.000","200.000","500.000"],"c":2,"d":2},
    {"q":"¿Cuántas hectáreas adicionales se busca forestar según la meta citada?","a":["50.000","100.000","200.000","400.000"],"c":2,"d":2},
    {"q":"¿Cuánto CO₂ equivalente al año se busca capturar desde 2030 según el documento?","a":["0,15–0,18 millones de toneladas","1,5–1,8 millones de toneladas","15–18 millones de toneladas","150–180 millones de toneladas"],"c":1,"d":2},
    {"q":"¿Por qué el castor es especialmente problemático en la zona descrita?","a":["Es una especie introducida sin depredadores naturales en la zona","Porque es nativo de Aysén","Porque elimina la industria forestal","Porque aumenta el bosque nativo"],"c":0,"d":2},
    {"q":"¿Qué efecto sobre la biodiversidad se menciona?","a":["Pérdida de hábitat y biodiversidad asociada al bosque nativo","Aumento garantizado de especies nativas","Creación de nuevos ecosistemas sin impactos","Ningún efecto"],"c":0,"d":2},
    {"q":"¿Por qué se plantea cooperación binacional con Argentina?","a":["El castor no respeta fronteras","Porque la NDC es argentina","Porque CONAF está en Argentina","Porque los bosques de Chiloé están en Argentina"],"c":0,"d":2},
    {"q":"¿Cuál es la diferencia clave entre 56%/44% y 54%/46% presentada en el documento?","a":["La primera distribución se refiere a pérdida de cobertura y la segunda a pérdida de carbono","Ambas son exactamente el mismo indicador","La primera es sobre biodiversidad y la segunda sobre población","La segunda se refiere a hectáreas recuperadas"],"c":0,"d":3},
    {"q":"Aunque el castor destruye más cobertura, ¿qué interpretación hace el documento sobre la pérdida de carbono?","a":["Ambos factores pesan de forma comparable","La actividad forestal no influye","El castor explica casi todo el carbono perdido","No existe pérdida de carbono"],"c":0,"d":3},
    {"q":"¿Qué conjunto reúne correctamente actores identificados en el problema?","a":["Industria forestal, especie invasora y Estado","Solo turistas y pescadores","Solo universidades","Solo comunidades extranjeras"],"c":0,"d":3},
    {"q":"¿Cuál es la relación planteada entre pérdida de bosque y cambio climático?","a":["Menos bosque implica menor captura de CO₂, agravando el problema climático","Más pérdida de bosque implica más captura","No existe relación","El bosque produce CO₂ exclusivamente"],"c":0,"d":3},
    {"q":"¿Qué combinación corresponde a las medidas estructurales propuestas?","a":["Política forestal, financiamiento para control del castor, fiscalización y cooperación con Argentina","Solo plantar árboles en casas","Reducir el turismo y cerrar parques","Importar más madera"],"c":0,"d":3},
    {"q":"¿Qué fuente recomienda el documento como evidencia científica sobre la pérdida de bosque durante 30 años?","a":["Policy Brief N°15 del CR2","Wikipedia","Blogs personales","Notas de opinión gremiales"],"c":0,"d":3},
    {"q":"¿Cuál de estas afirmaciones refleja mejor la propuesta del juego 'Guardabosques de Carbono'?","a":["Tomar decisiones sobre una hectárea con presupuesto limitado y observar cambios en carbono capturado","Competir por quién corta más árboles","Simular solamente el clima","Responder preguntas sin consecuencias"],"c":0,"d":3},
    {"q":"¿Qué acciones individuales aparecen como parte de la respuesta propuesta?","a":["Apoyar campañas contra invasoras, no liberar especies exóticas, consumir madera certificada y reforestar con nativas","Comprar cualquier madera disponible y liberar mascotas","Ignorar especies invasoras","Reemplazar bosques nativos por especies exóticas"],"c":0,"d":3},
    {"q":"¿Qué tensión plantea la reflexión final del podcast?","a":["Cómo la actividad productiva y la introducción de una especie exótica pueden comprometer compromisos climáticos y qué responsabilidad corresponde al Estado y empresas","Si el bosque debería eliminarse","Si el castor es una mascota ideal","Si Chile debería abandonar la ciencia"],"c":0,"d":3},
]

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def using_postgres():
    return bool(DATABASE_URL)

def db():
    if using_postgres():
        if psycopg is None:
            raise RuntimeError("psycopg no está instalado")
        return psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row)
    con = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "visitors.db"))
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    if using_postgres():
        con.execute("""CREATE TABLE IF NOT EXISTS visitors (id BIGSERIAL PRIMARY KEY, alias TEXT UNIQUE NOT NULL, first_seen TIMESTAMPTZ NOT NULL, quiz_played INTEGER NOT NULL DEFAULT 0)""")
    else:
        con.execute("""CREATE TABLE IF NOT EXISTS visitors (id INTEGER PRIMARY KEY AUTOINCREMENT, alias TEXT UNIQUE NOT NULL, first_seen TEXT NOT NULL, quiz_played INTEGER DEFAULT 0)""")
    con.commit(); con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.post('/api/register')
def register():
    data=request.get_json(silent=True) or {}; alias=(data.get('alias') or '').strip()
    if len(alias)<2 or len(alias)>40:
        return jsonify(ok=False,error='Usa un nombre o alias de 2 a 40 caracteres.'),400
    con=db()
    try:
        if using_postgres():
            row=con.execute('SELECT id, alias FROM visitors WHERE lower(alias)=lower(%s)',(alias,)).fetchone()
        else:
            row=con.execute('SELECT id, alias FROM visitors WHERE lower(alias)=lower(?)',(alias,)).fetchone()
        if row:
            return jsonify(ok=False,already=True,error='Este nombre o alias ya tiene un registro.'),409
        if using_postgres():
            con.execute('INSERT INTO visitors(alias,first_seen) VALUES(%s,%s)',(alias,datetime.now(timezone.utc)))
        else:
            con.execute('INSERT INTO visitors(alias,first_seen) VALUES(?,?)',(alias,now_iso()))
        con.commit()
    finally:
        con.close()
    session['visitor']=alias
    return jsonify(ok=True,alias=alias)

@app.get('/api/questions')
def questions():
    by={1:[],2:[],3:[]}
    for q in QUESTIONS: by[q['d']].append(q)
    selected=random.sample(by[1],3)+random.sample(by[2],4)+random.sample(by[3],3)
    return jsonify(questions=[{'q':x['q'],'a':x['a'],'d':x['d']} for x in selected])

@app.post('/api/quiz-finished')
def quiz_finished():
    alias=session.get('visitor')
    if not alias: return jsonify(ok=False),401
    con=db()
    try:
        if using_postgres(): con.execute('UPDATE visitors SET quiz_played=quiz_played+1 WHERE lower(alias)=lower(%s)',(alias,))
        else: con.execute('UPDATE visitors SET quiz_played=quiz_played+1 WHERE lower(alias)=lower(?)',(alias,))
        con.commit()
    finally: con.close()
    return jsonify(ok=True)

@app.get('/health')
def health():
    try:
        con=db(); con.execute('SELECT 1'); con.close()
        return jsonify(status='ok', database='postgres' if using_postgres() else 'sqlite')
    except Exception as exc:
        return jsonify(status='error', error=str(exc)),500

init_db()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
