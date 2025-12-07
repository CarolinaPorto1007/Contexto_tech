import spacy

# Carrega o modelo
try:
    print("📚 Carregando validador ortográfico (spaCy)...")
    nlp = spacy.load("pt_core_news_md")
except OSError:
    nlp = None

# 📝 LISTA VIP: Únicas palavras curtas (menos de 4 letras) permitidas
# Adicione aqui qualquer sigla de tecnologia que lembrar.
WHITELIST_CURTAS = {
    "api", "app", "web", "bot", "bug", "dev", "git", "hub", "net", 
    "sql", "ssl", "ssh", "tcp", "udp", "vpn", "wan", "lan", "dns",
    "mac", "ip",  "cpu", "gpu", "ram", "rom", "ssd", "hdd", "usb", 
    "led", "lcd", "iot", "xml", "json", "jar", "zip", "rar", "exe",
    "bin", "hex", "bit", "byte", "log", "npm", "pip", "kde", "gnome",
    "ux",  "ui",  "seo", "aws", "gcp", "azure", "poo", "mvc", "dao"
}

def palavra_existe(palavra):
    """
    Filtro híbrido:
    - Palavras curtas (< 4): Só aceita se estiver na whitelist manual.
    - Palavras longas (>= 4): Aceita se o spaCy reconhecer.
    """
    if nlp is None: return True

    palavra = palavra.strip().lower()

    print(palavra)

    # REGRA 1: Filtro de tamanho e Whitelist
    # Se for menor que 4 letras, SÓ passa se estiver na nossa lista VIP.
    # Isso bloqueia: "asf", "wer", "dg", "se", "re"
    if len(palavra) < 4:
        if palavra in WHITELIST_CURTAS:
            return True
        else:
            return False

    # REGRA 2: Verificação do SpaCy para palavras normais (4+ letras)
    doc = nlp(palavra)
    token = doc[0]

    # Rejeita se não existe no dicionário (is_oov) ou se não é letra (123, ???)
    if token.is_oov or not token.is_alpha:
        return False
        
    # Rejeita se o spaCy classificar como "X" (indefinido/ruído)
    if token.pos_ == "X":
        return False

    return True


def obter_singular(palavra):
    """
    Tenta passar para o singular. Se o resultado for uma palavra
    que não existe (ex: 'onibu'), mantém a original.
    """
    if nlp is None: return palavra
    
    palavra = palavra.strip().lower()
    doc = nlp(palavra)
    token = doc[0]
    
    sugestao_singular = token.lemma_

    # Se o spaCy não mudou nada, retorna logo
    if sugestao_singular == palavra:
        return palavra

    # 🧠 A MÁGICA (Prova Real):
    # Verifica se a palavra nova (ex: "onibu") existe no vocabulário
    doc_teste = nlp(sugestao_singular)
    
    # Se a sugestão for desconhecida (is_oov), o spaCy "quebrou" a palavra.
    # Nesse caso, ignoramos a sugestão e devolvemos a original.
    if doc_teste[0].is_oov:
        return palavra

    # Se a sugestão existe (ex: "carro"), retorna ela.
    return sugestao_singular