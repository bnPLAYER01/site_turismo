from flask import Flask, render_template, jsonify, request
from database import init_db, obter_comentarios_do_ponto
import sqlite3
import os

app = Flask(__name__)

# Configuração do caminho do banco (Ajustado para o nome do estado)
DATABASE = os.path.join(os.path.dirname(__file__), 'turismo_espírito_santo.db')

def get_connection():
    conn = sqlite3.connect(DATABASE)
    # Faz o SQLite retornar linhas que funcionam como dicionários
    conn.row_factory = sqlite3.Row 
    return conn

# Inicializa o banco ao rodar o app (Cria tabelas e insere dados iniciais)
init_db()



@app.route('/')
def index():
    # Rota limpa! Agora você pode usar os elementos de site no index.html
    return render_template('index.html')

@app.route('/turisticos')
def turisticos():
    conn = get_connection()
    cursor = conn.cursor()
    # Puxamos os pontos aqui para alimentar os cards da página de listagem
    cursor.execute("SELECT * FROM pontos_turisticos")
    pontos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('turisticos.html', pontos=pontos)

@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Busca os dados do Ponto Turístico
    cursor.execute("SELECT * FROM pontos_turisticos WHERE id = ?", (id,))
    row = cursor.fetchone()
    ponto = dict(row) if row else None
    conn.close()
    comentarios = obter_comentarios_do_ponto(id)
    return render_template('detalhes.html', ponto=ponto, comentarios=comentarios)


@app.route('/mapa')
def mapa():
    return render_template('mapa.html')

@app.route('/onibus')
def onibus():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pontos_onibus")
    pontos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('onibus.html', pontos=pontos)

@app.route('/empreendedores')
def empreendedores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empreendedores")
    # Nota: você pode mudar o nome da variável para 'lojas' se preferir no HTML
    lojas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('empreendedores.html', pontos=lojas)

@app.route('/api/pontos')
def api_pontos():
    conn = get_connection()
    cursor = conn.cursor()
    # Unificando pontos turísticos e empreendedores para o mapa
    query = """
        SELECT id, nome, latitude, longitude, 'turistico' as origem FROM pontos_turisticos
        UNION
        SELECT id, nome, latitude, longitude, 'empreendedor' as origem FROM empreendedores
    """
    cursor.execute(query)
    pontos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(pontos)

@app.route('/api/avaliar', methods=['POST'])
def avaliar():
    data = request.get_json()
    
    # Extraindo os dados do JSON enviado pelo JS
    id_ponto = data.get('id_ponto_turistico')
    nota = data.get('nota')
    comentario = data.get('comentario')
    id_usuario = data.get('id_usuario', 1) # Padrão para usuário 1 se não houver login

    if not id_ponto or not nota:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Inserindo a avaliação no banco
        cursor.execute("""
            INSERT INTO avaliacoes (id_ponto_turistico, id_usuario, nota, comentario)
            VALUES (?, ?, ?, ?)
        """, (id_ponto, id_usuario, nota, comentario))
        
        conn.commit()
        conn.close()
        
        return jsonify({"mensagem": "Avaliação salva com sucesso!"}), 201
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)