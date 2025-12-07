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
    Normaliza singular e gênero com proteção contra "Testa" -> "Testo".
    """
    if nlp is None: return palavra
    
    palavra = palavra.strip().lower()
    doc = nlp(palavra)
    token = doc[0]
    
    # 1. Singular via spaCy
    sugestao_singular = token.lemma_

    if sugestao_singular == palavra:
        resultado = palavra
    else:
        # Prova Real
        doc_teste = nlp(sugestao_singular)
        if doc_teste[0].is_oov:
            resultado = palavra
        else:
            resultado = sugestao_singular

    # 2. Correção de Plural Feminino ('as')
    if resultado.endswith('as'):
        sem_s = resultado[:-1] 
        if not nlp(sem_s)[0].is_oov:
            resultado = sem_s

    # 3. Masculinização Controlada
    if resultado.endswith('a'):
        
        # A) Tenta apenas REMOVER o 'a' (Programadora -> Programador)
        # É a regra mais segura.
        tentativa_cortada = resultado[:-1]
        terminacoes_validas = ('r', 's', 'z', 'l', 'm', 'n')
        
        if (len(tentativa_cortada) > 2 
            and not nlp(tentativa_cortada)[0].is_oov 
            and tentativa_cortada.endswith(terminacoes_validas)):
            return tentativa_cortada
            
        # B) Tenta trocar 'a' por 'o', MAS SÓ PARA SUFIXOS SEGUROS
        # Isso evita Testa->Testo, Mesa->Meso, Porta->Porto
        # Aceita: Engenheira->Engenheiro, Usuária->Usuário, Aluna->Aluno
        sufixos_seguros = ('eira', 'ria', 'na', 'oa')
        
        if resultado.endswith(sufixos_seguros):
            tentativa_o = resultado[:-1] + 'o'
            if not nlp(tentativa_o)[0].is_oov:
                return tentativa_o

    return resultado