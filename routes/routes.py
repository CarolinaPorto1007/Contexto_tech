from flask import Blueprint, render_template, request, jsonify
import random
import spacy
import numpy as np
import requests

main_bp = Blueprint('main', __name__)

# 🔤 Carrega o modelo de linguagem português médio do spaCy
nlp = spacy.load("pt_core_news_md")

# 🧠 Busca automática de palavras da Wikipédia
def buscar_palavras_tecnologia():
    """
    Busca automaticamente títulos da Wikipédia sobre tecnologia.
    Se falhar, retorna uma lista de palavras reserva.
    """
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Categoria:Tecnologia",
        "cmlimit": "500",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "query" not in data or "categorymembers" not in data["query"]:
            raise ValueError("Resposta inesperada da Wikipédia")

        artigos = [item["title"].lower() for item in data["query"]["categorymembers"]]
        artigos_filtrados = [a for a in artigos if len(a) > 10]
        if not artigos_filtrados:
            raise ValueError("Lista vazia.")

        return artigos_filtrados

    except Exception as e:
        print(f"⚠️ Erro ao buscar palavras online: {e}")
        return [
            "inteligência artificial",
            "realidade aumentada",
            "computação quântica",
            "aprendizado profundo",
            "visão computacional",
            "processamento de linguagem natural",
            "robótica industrial",
            "engenharia de software",
            "tecnologia da informação",
            "computação em nuvem",
            "sistemas embarcados",
            "redes neurais convolucionais",
            "big data e análise preditiva",
            "cibersegurança e criptografia",
            "internet das coisas"
        ]

# 🔒 Estado inicial do jogo
PALAVRAS_TEC = []
palavra_secreta = ""
vetor_secreto = None
jogo_finalizado = False

def inicializar_jogo():
    global PALAVRAS_TEC, palavra_secreta, vetor_secreto, jogo_finalizado
    PALAVRAS_TEC = buscar_palavras_tecnologia()
    palavra_secreta = random.choice(PALAVRAS_TEC)
    vetor_secreto = nlp(palavra_secreta).vector
    jogo_finalizado = False

# Inicializa o jogo na importação
inicializar_jogo()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/tentar', methods=['POST'])
def tentar():
    global jogo_finalizado

    if jogo_finalizado:
        return jsonify({"erro": "O jogo já terminou! Clique em Reiniciar para jogar novamente."})

    tentativa = request.json['palavra'].lower().strip()
    doc_tentativa = nlp(tentativa)

    if not doc_tentativa.vector_norm:
        return jsonify({"erro": "Palavra desconhecida pelo modelo."})

    vetor_tentativa = doc_tentativa.vector

    # Produto escalar e similaridade do cosseno
    produto_escalar = np.dot(vetor_tentativa, vetor_secreto)
    norma_tentativa = np.linalg.norm(vetor_tentativa)
    norma_secreto = np.linalg.norm(vetor_secreto)
    similaridade = produto_escalar / (norma_tentativa * norma_secreto)
    similaridade = round(similaridade * 100, 2)

    venceu = tentativa == palavra_secreta
    if venceu:
        jogo_finalizado = True

    return jsonify({
        "similaridade": similaridade,
        "venceu": venceu,
        "palavra_secreta": palavra_secreta if venceu else None
    })

@main_bp.route('/reiniciar', methods=['POST'])
def reiniciar():
    inicializar_jogo()
    return jsonify({"nova_palavra": "gerada"})
