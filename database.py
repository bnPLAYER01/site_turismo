import sqlite3
import os

# Nome do banco atualizado para o estado todo
DATABASE = os.path.join(os.path.dirname(__file__), 'turismo_espírito_santo.db')

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

def obter_comentarios_do_ponto(id_ponto):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT usuarios.nome, avaliacoes.nota, avaliacoes.comentario, avaliacoes.data_publicacao
        FROM avaliacoes 
        JOIN usuarios ON avaliacoes.id_usuario = usuarios.id 
        WHERE avaliacoes.id_ponto_turistico = ?
        ORDER BY avaliacoes.data_publicacao DESC
    """
    cursor.execute(query, (id_ponto,))
    comentarios = cursor.fetchall()
    conn.close()
    return comentarios
    

def init_db():
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Criando as tabelas
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categorias (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       nome TEXT NOT NULL 
    );

    CREATE TABLE IF NOT EXISTS pontos_turisticos(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       nome TEXT NOT NULL,
       descricao TEXT,
       latitude REAL NOT NULL,
       longitude REAL NOT NULL,
       categoria_id INTEGER NULL,
       endereco TEXT,
       imagem TEXT,   
       FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS pontos_onibus(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       nome TEXT NOT NULL,
       linha TEXT,
       latitude REAL NOT NULL,
       longitude REAL NOT NULL,
       endereco TEXT,
       observacoes TEXT
    );

    CREATE TABLE IF NOT EXISTS empreendedores(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       nome TEXT NOT NULL,
       tipo TEXT,
       descricao TEXT,
       telefone TEXT,
       instagram TEXT,
       latitude REAL,
       longitude REAL,
       endereco TEXT,
       categoria_id INTEGER NULL,
       FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ponto_turistico INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        nota INTEGER CHECK(nota >= 1 AND nota <= 5),
        comentario TEXT,
        data_publicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_ponto_turistico) REFERENCES pontos_turisticos(id) ON DELETE CASCADE,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
    );
    """)
    
    # 1. Categorias
    cursor.execute("SELECT COUNT(*) FROM categorias")
    res_cat = cursor.fetchone()
    if res_cat and res_cat[0] == 0:
        categorias = [('Praia',), ('Cultura',), ('Natureza',), ('Transporte',), ('Serviços',)]
        cursor.executemany("INSERT INTO categorias (nome) VALUES (?)", categorias)

        cursor.execute("SELECT COUNT(*) FROM usuarios")
    res_user = cursor.fetchone()
    if res_user and res_user[0] == 0:
        cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)", 
                       ('Turista Capixaba', 'turista@es.com.br'))
        

    # 2. Pontos Turísticos (Corrigido erro do Farol e texto da Pedra da Cebola)
    cursor.execute("SELECT COUNT(*) FROM pontos_turisticos")
    res_pontos = cursor.fetchone()
    if res_pontos and res_pontos[0] == 0:
        dados_es = [
            ('Convento da Penha', 'Principal ícone religioso do ES', -20.3292, -40.2872, 2, 'Vila Velha - ES', 'convento da penha.webp'),
            ('Pedra Azul', 'Famosa formação rochosa nas montanhas', -20.4035, -41.0114, 3, 'Domingos Martins - ES', 'Pedra azul.webp'),
            ('Praia do Morro', 'Uma das praias mais famosas do estado', -20.6500, -40.4880, 1, 'Guarapari - ES', 'Praia do morro-guarapari.webp'),
            ('Mosteiro Zen Budista', 'Primeiro mosteiro zen da América Latina', -19.8322, -40.3995, 2, 'Ibiraçu - ES', 'Buda.webp'),
            ('Parque Nacional do Caparaó', 'Abriga o Pico da Bandeira', -20.4281, -41.7961, 3, 'Dores do Rio Preto - ES', 'Parque do caparaó.webp'),
            ('Parque Pedra da Cebola', 'Localizado em Vitória, possui vasta área verde, lagos e o icônico rochedo que dá nome ao parque.', -20.2797, -40.2966, 3, 'Mata da Praia, Vitória - ES', 'pedra da cebola.webp'),
            ('Morro do Moreno', 'Monumento natural com trilhas e vista panorâmica da Baía de Vitória.', -20.3290, -40.2840, 3, 'Praia da Costa, Vila Velha - ES', 'morro do moreno.webp'),
            ('Farol Santa Luzia', 'Torre de ferro fundido de 1871, fabricada na Escócia, orienta a entrada do canal de Vitória.', -20.3036, -40.2831, 2, 'Praia da Costa, Vila Velha - ES', 'Farol santa luzia.webp'),
            ('Parque Botânico Vale', 'Área verde com 33 hectares, trilhas ecológicas e orquidário. Aberto Ter-Dom, 08h-17h.', -20.2586, -40.2603, 3, 'Av. dos Expedicionários, s/n - Jardim Camburi, Vitória - ES', 'Parque botanico vale.webp'),
            ('Palácio Anchieta', 'Sede do governo estadual e monumento histórico. Aberto Ter-Sex (09h-17h) e Sáb-Dom (09h-16h).', -20.3218, -40.3394, 2, 'Praça João Clímaco, s/n - Centro, Vitória - ES', 'Palacio anchieta.webp'),
            ('Praia da Sereia', 'Enseada de águas calmas e rasas, ideal para famílias e crianças. Aberto 24h.', -20.3363, -40.2881, 1, 'Praia da Costa, Vila Velha - ES, 29101-735', 'Praia da sereia.webp'),
            ('Praia da Costa', 'Uma das praias urbanas mais queridas, com excelente infraestrutura de quiosques e calçadão. Aberto 24h.', -20.3373, -40.2812, 1, 'Av. Antônio Gil Veloso, Praia da Costa, Vila Velha - ES', 'Praia da costa.webp'),
            ('Curva da Jurema', 'Praia de águas calmas com excelente infraestrutura de quiosques e vista para a Ilha do Boi. Aberto 24h.', -20.3041, -40.2917, 1, 'Av. José Miranda Machado, Enseada do Suá, Vitória - ES', 'curva da jurema.webp'),
            ('Ilha do Boi', 'Bairro nobre com pequenas praias de águas cristalinas, como a Praia da Direita e a Praia da Esquerda. Aberto 24h.', -20.3114, -40.2861, 1, 'Ilha do Boi, Vitória - ES', 'Ilha do boi.webp'),
            ('Praia do Canto', 'Bairro nobre e boêmio de Vitória, famoso pelo Triângulo das Bermudas, gastronomia e vida noturna. Aberto 24h.', -20.3015, -40.2911, 1, 'Praia do Canto, Vitória - ES', 'praia do canto.webp'),
            ('Praia de Camburi', 'A maior praia da capital, com 6km de orla ideal para caminhadas, esportes e quiosques gastronômicos. Aberto 24h.', -20.2667, -40.2833, 1, 'Av. Dante Michelini, Vitória - ES', 'Praia do canto.webp'),
            ('Três Ilhas', 'Arquipélago paradisíaco ideal para mergulho e observação da vida marinha. Acesso via passeio de barco. Aberto 24h.', -20.5919, -40.3853, 1, 'Arquipélago de Três Ilhas (Acesso via mar), Guarapari - ES', 'Praia de camburi.webp'),
            ('Praia do Morro', 'Uma das praias mais populares e urbanizadas do estado, famosa pelo monumento do Marlim Azul. Aberto 24h.', -20.6511, -40.5067, 1, 'Av. Beira Mar, Praia do Morro, Guarapari - ES', 'Tres ilhas.webp'),
            ('Parque Estadual do Forno Grande', 'Reserva de Mata Atlântica com trilhas, mirantes e o imponente Pico do Forno Grande. Aberto diariamente, 08h-16h.', -20.5167, -41.0833, 3, 'Forno Grande, Castelo - ES, 29360-000', 'Parque estadual de forno grande.webp'),
            ('Mestre Álvaro', 'Um dos maiores morros litorâneos do Brasil, com 833 metros de altitude e trilhas com vista panorâmica da Grande Vitória. Aberto 24h (recomenda-se guia).', -20.1772, -40.3117, 3, 'Acesso principal por Serra Sede ou Jardim Tropical, Serra - ES', 'Mestre alvaro.webp'),
            ('Igreja e Residência dos Reis Magos', 'Patrimônio histórico do século XVI, com arquitetura jesuítica e vista privilegiada para a foz do Rio Reis Magos. Aberto Ter-Dom, 09h-17h.', -19.9292, -40.1917, 2, 'Rua Reis Magos, s/n, Nova Almeida, Serra - ES', 'Reis magos.webp'),
            ('Balneário de Nova Almeida', 'Região turística famosa por suas praias de águas calmas, falésias e a tradicional gastronomia local. Aberto 24h.', -19.9255, -40.1944, 1, 'Orla de Nova Almeida, Serra - ES', 'Balneário-de-nova-almeida.webp'),
            ('Praia de Jacaraípe', 'Famosa pelo surf e pelo movimento em sua orla, abriga o monumento da Baleia e diversas opções de quiosques. Aberto 24h.', -20.1603, -40.1889, 1, 'Av. Abido Saadi, Jacaraípe, Serra - ES', 'Praia de jacaraípe.webp'),
            ('Itaúnas', 'Famosa por suas dunas de areia de até 30 metros, praias selvagens e o tradicional festival de forró. Aberto 24h (Vila).', -18.4251, -39.7032, 3, 'Vila de Itaúnas, Conceição da Barra - ES', 'itaúnas.webp'),
            ('Praia de Conceição da Barra', 'Praia urbana famosa pelas suas castanheiras, águas mornas e o histórico Farol da Barra. Aberto 24h.', -18.5912, -39.7289, 1, 'Orla Marítima, Conceição da Barra - ES', 'Praia Barra.webp'),
            ('Ilha de Guriri', 'Um dos balneários mais animados do norte capixaba, com águas mornas e sede do Projeto Tamar. Aberto 24h.', -18.7303, -39.7431, 1, 'Guriri, São Mateus - ES', 'Ilha de guriri.webp'),
            ('Porto de São Mateus', 'Sítio histórico com casarios coloniais do século XVIII e XIX às margens do Rio São Mateus. Aberto para visitação externa.', -18.7153, -39.8647, 2, 'Rua da Bica, Porto, São Mateus - ES', 'Porto são mateus.webp'),
            ('Praia Secreta', 'Pequena enseada de águas calmas próxima ao Farol de Santa Luzia. Acesso via linhas de ônibus 651, 662 e 611.', -20.3267, -40.2709, 2, 'R. Praia Secreta - Praia da Costa, Vila Velha - ES', 'Praia secreta.webp'),
            ('Shopping Vitória', 'Shopping amplo com redes de lojas famosas, um cinema e diversas opções gastronômicas casuais.', -20.3129, -40.2870, 2, 'Av. Américo Buaiz, 200 - Enseada do Suá, Vitória - ES, 29050-902', 'Shopping vitória.webp'),
            ('Shopping Mestre Álvaro', 'Shopping de vários andares com lojas, restaurantes e opções de lazer, além de academia e salão de beleza.', -20.2392, -40.2753, 2, 'Av. João Palácio, 300 - Eurico Salles, Serra - ES, 29160-161', 'Shopping mestre alvaro.webp'),
            ('Shopping Montserrat', 'Shopping grande com vários andares que oferece lojas de varejo, praça de alimentação e cinema.', -20.1936, -40.2654, 2, 'Av. Eldes Scherrer Souza, 2162 - Colina de Laranjeiras, Serra - ES, 29167-080', 'Shopping montserrat.webp'),
            ('Shopping Vila Velha', 'Grande shopping coberto com uma variedade de lojas de varejo, cinema, lanchonetes e atividades infantis.', -20.3481, -40.2987, 2, 'Av. Luciano das Neves, 2418 - Divino Espírito Santo, Vila Velha - ES, 29107-010', 'Shopping vila velha.webp'),
            ('Shopping Moxuara', 'Shopping tranquilo de quatro andares com mais de 200 lojas, grande praça de alimentação e um cinema multiplex.', -20.3104, -40.3865, 2, 'Av. Mário Gurgel, 5353 - São Francisco, Cariacica - ES, 29140-000', 'Shopping moxuara.webp'),
            ('Shopping Praia da Costa', 'Shopping com lojas de marcas do mundo todo, restaurantes, cinema e área de recreação. Permite animais desde 2002.', -20.3348, -40.2839, 2, 'Av. Dr. Olivio Lira, 353 - Praia da Costa, Vila Velha - ES, 29101-950', 'Shopping praia da costa.webp'),
            ('Sítio Gava', 'Ambiente de paz, lazer e tranquilidade para família e amigos. Uma das opções para curtir o verão em Viana.', -20.3968, -40.4753, 2, 'Rua Projetada s/n - Piapitangui, Viana - ES, 29135-000', 'sitio gava.webp'),
            ('Fazenda Camping', 'Área de lazer ao ar livre em um camping com toboáguas, arena de paintball e churrascarias.', -20.4335, -40.3756, 2, 'Rod. do Sol, 2231 - km 19 - Jucu, Vila Velha - ES, 29129-750', 'Fazenda camping.webp'),
            ('Sesc Praia Formosa', 'Centro de turismo social e lazer com parque aquático, áreas verdes e praças temáticas. Oferece trilhas ecológicas, acesso à praia e regime de pensão completa.', -19.8733, -40.2206, 2, 'Rodovia ES-010, Km 35 - Santa Cruz, Aracruz - ES, 29199-548', 'sesc.webp'),
            ('Poço do Egito', 'Jóia natural da região do Caparaó, localizada na divisa entre os estados de Minas Gerais e Espírito Santo.', -20.3415, -41.5260, 2, 'J5P7+4G - São João do Príncipe, Iúna - ES, 29390-000', 'poço do egito.webp'),
            ('Eco Park Itabira', 'Natureza e aventura ao lado do Pico do Itabira com trilhas, passeios de jardineira, paisagismo moderno e cafeteria.', -20.8916, -41.1578, 2, 'Estrada para Itabira - Alto Itabira, Cachoeiro de Itapemirim - ES, 29321-800', 'Ecopark.webp'),
            ('Zoo Park da Montanha', 'Parque zoológico para conservação aberto desde 2012, com grandes felinos, aves exóticas e primatas.', -20.4236, -40.7790, 2, 'Estrada do Rio Fundo, s/n - Rodovia Municipal Romeu Nunes Vieira, Mal. Floriano - ES, 29255-000', 'zoo park da montanha.webp'),
            ('Thermas Internacional do Espírito Santo', 'Parque aquático com diversas piscinas, toboáguas e a maior cachoeira artificial da América Latina. Possui restaurante e lanchonetes.', -20.5013, -40.4098, 2, 'Rod. do Sol, s/n - Km 29 - Guarapari, Palmeiras - ES, 29220-730', 'thermas.webp'),
            ('Gruta da Onça', 'Parque natural no centro de Vitória com Mata Atlântica, trilhas e mirantes voltados à preservação e educação ambiental.', -20.3194, -40.3378, 2, 'Rua Barão de Monjardim, 240 - Centro, Vitória - ES, 29010-390', 'Mseu Valente.webp'),
            ('Museu Vale', 'Espaço cultural em antiga estação ferroviária com exposições de arte contemporânea e vista para a Baía de Vitória.', -20.3297, -40.3386, 2, 'Av. Jerônimo Monteiro, s/n - Centro, Vila Velha - ES, 29100-901', 'Museu vale.webp'),
            ('Praia de Setiba', 'Praia de natureza preservada com águas claras e boas ondas para surf, ideal para quem busca tranquilidade e contato com o mar.', -20.6734, -40.4620, 2, 'Rodovia do Sol - Setiba, Guarapari - ES, 29222-360', 'Praia de setiba.webp'),
            ('Parque Estadual Paulo César Vinha', 'Reserva de restinga com lagoas, trilhas ecológicas e fauna protegida. Importante espaço para ecoturismo e pesquisa.', -20.6775, -40.4479, 2, 'Rodovia do Sol, Km 37 - Setiba, Guarapari - ES, 29222-360', 'Parque estadual.webp'),
            ('Lagoa Juparanã', 'Uma das maiores lagoas de água doce do Brasil, ideal para esportes aquáticos, passeios de barco e turismo regional.', -19.4017, -40.0697, 2, 'Lagoa Juparanã - Linhares - ES, 29900-000', 'Lago juparana.webp'),
            ('Monte Aghá', 'Montanha no litoral sul capixaba procurada para trilhas e escaladas, com vista panorâmica impressionante do mar.', -21.0083, -40.8247, 2, 'Rodovia ES-060 - Itapemirim - ES, 29330-000', 'Monte aguá.webp'),
            ('Cachoeira de Matilde', 'Uma das cachoeiras mais conhecidas do sul do estado, com grande queda d’água cercada por vegetação e um mirante natural.', -20.6356, -40.7419, 2, 'BR-482, Distrito de Matilde, Alfredo Chaves - ES, 29240-000', 'Cachoeiro de matilde.webp'),
            ('Parque Cultural Casa do Governador', 'Espaço cultural e ambiental com obras de arte ao ar livre, trilhas ecológicas e vista panorâmica da Baía de Vitória.', -20.1953, -40.1624, 2, 'Rua Santa Luzia, s/n - Praia da Costa, Vila Velha - ES, 29101-100', 'casa cultural.webp'),
            ('Praia de Castelhanos', 'Praia extensa com águas claras e paisagem natural preservada, sendo um dos destinos mais tradicionais para famílias no litoral sul.', -20.8032, -40.6425, 2, 'Rodovia ES-060 - Castelhanos, Anchieta - ES, 29230-000', 'Praia de castelhanos.webp'),
            ('Parque Pedra das Flores', 'Área de preservação no Caparaó com montanhas, vegetação de altitude e trilhas em meio à natureza.', -20.5297, -41.1182, 2, 'Zona Rural, Castelo - ES, 29360-000', 'Parque pedra das flores.webp'),
            ('Cachoeira Alta', 'Cachoeira com grande volume de água e área de lazer em meio à natureza, sendo um dos pontos turísticos mais visitados da região sul.', -20.8735, -41.1143, 2, 'Distrito de Coutinho, Cachoeiro de Itapemirim - ES, 29311-899', 'cacheira alta.webp'),
            ('Praia de Manguinhos', 'Famosa pelos restaurantes de frutos do mar e pelo clima tranquilo de vila de pescadores, oferecendo um ambiente charmoso e acolhedor.', -20.1832, -40.1864, 2, 'Av. Atapoã - Manguinhos, Serra - ES, 29173-087', 'Praia de manguinhos.webp'),
            ('Falésias de Nova Almeida', 'Imponentes paredões à beira-mar com vista panorâmica para a foz do Rio Reis Magos. Um dos melhores pontos para fotos e contemplação no estado.', -19.9240, -40.1895, 3, 'Nova Almeida, Serra - ES', 'falesias.webp'),



        ]
        cursor.executemany("""
            INSERT INTO pontos_turisticos (nome, descricao, latitude, longitude, categoria_id, endereco, imagem) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""", dados_es)
        
        cursor.execute("SELECT COUNT(*) FROM avaliacoes")
    res_aval = cursor.fetchone()
    if res_aval and res_aval[0] == 0:
        cursor.execute("""
            INSERT INTO avaliacoes (id_ponto_turistico, id_usuario, nota, comentario) 
            VALUES (1, 1, 5, 'Vista maravilhosa e muita paz!')
        """)

    # 3. Ônibus
    cursor.execute("SELECT COUNT(*) FROM pontos_onibus")
    res_bus = cursor.fetchone()
    if res_bus and res_bus[0] == 0:
        dados_onibus = [
            ('Terminal de Laranjeiras', '504, 505, 507', -20.1471, -40.2713, 'Av. Civit, Serra - ES', 'Conexão principal da Serra'),
            ('Terminal de Jacaraípe', '802, 810, 818', -20.1558, -40.2015, 'Av. Abido Saadi, Serra - ES', 'Acesso às praias do norte'),
            ('Rodoviária de Vitória', 'Intermunicipais', -20.3216, -40.3396, 'Ilha do Príncipe, Vitória - ES', 'Portão de entrada terrestre'),
            ('Ponto - Convento da Penha', '635, 611', -20.3265, -40.2845, 'R. Vasco Coutinho, Vila Velha - ES', 'Subida para o Convento'),
            ('Ponto - Convento da Penha', '635, 611', -20.3265, -40.2845, 'R. Vasco Coutinho, Vila Velha - ES', 'Subida para o Convento'),
            ('Parque Pedra da Cebola', '541, 591, 123, 506, 503, 597, 559, 501, 509, 519, 535, 516, 553, 518, 504, 507, 539, 527, 122, 161, 121, 241, 163, 214', -20.2758, -40.2974, 'Entre as ruas João Baptista Celestino e Paulo Pereira Gomes, Mata da Praia, Vitória - ES', 'Parque municipal e ponto de lazer com ampla área verde'),
            ('Convento da Penha', '635, 402 (AQUAVIÁRIO)', -20.3292, -40.2871, 'R. Vasco Coutinho, Prainha, Vila Velha - ES', 'Principal ponto turístico religioso do ES, acesso via Prainha'),
            ('Morro do Moreno', '662, 611, 651', -20.3283, -40.2798, 'R. João Joaquim da Mota, Praia da Costa, Vila Velha - ES', 'Ponto turístico para trilhas e vista panorâmica de Vitória e Vila Velha'),
            ('Farol de Santa Luzia', '651, 662, 611', -20.3235, -40.2711, 'R. Elpídio Pimentel, Praia da Costa, Vila Velha - ES', 'Farol histórico com vista panorâmica da entrada da Baía de Vitória'),
            ('Parque Botânico Vale', '121, 164, 103, 161, 111, 211, 310, 241', -20.2523, -40.2575, 'Av. dos Expedicionários, s/n - Jardim Camburi, Vitória - ES', 'Área de preservação com orquidário, trilhas e atividades de lazer gratuitas'),
            ('Parque Moscoso / Palácio Anchieta', '164, 572, 519, 559, 121, 516, 503, 522, 513, 103, 558, 529, 597, 161, 171, 573', -20.3201, -40.3405, 'Av. Cleto Nunes, s/n - Centro, Vitória - ES', 'Parque histórico mais antigo da capital, próximo ao Palácio Anchieta'),
            ('Praia da Sereia', '615, 662, 650, 611', -20.3275, -40.2831, 'Av. Antônio Gil Veloso, Praia da Costa, Vila Velha - ES', 'Praia de águas calmas localizada na base do Morro do Moreno'),
            ('Praia da Costa', '662, 650, 611, 651', -20.3291, -40.2845, 'Av. Antônio Gil Veloso, Praia da Costa, Vila Velha - ES', 'Uma das praias mais famosas do estado, com ampla infraestrutura e calçadão'),
            ('Praia da Curva da Jurema', '522, 044, 203, 031, 212, 211, 572, 512, 515, 560, 103, 074, 505, 510, 213, 073, 508', -20.2978, -40.2892, 'Av. José Miranda Machado, Enseada do Suá, Vitória - ES', 'Praia de águas calmas na Enseada do Suá, próxima ao Shopping Vitória'),
            ('Ilha do Boi', '203', -20.2989, -40.2831, 'R. Renato Nascimento Daher Carneiro, Ilha do Boi, Vitória - ES', 'Bairro nobre com praias de águas limpas e vista para a Terceira Ponte'),
            ('Praia do Canto', '160, 523, 515, 572, 211, 505, 510, 112, 512, 839, 560, 212, 213, 508, 111', -20.3015, -40.2931, 'Av. Nossa Senhora da Penha / Triângulo das Bermudas, Vitória - ES', 'Bairro com forte polo gastronômico, vida noturna e praças de lazer'),
            ('Praia de Camburi', '160, 523, 515, 572, 211, 505, 510, 112, 512, 839, 560, 212, 213, 508, 111, 537, 528', -20.2878, -40.2925, 'Av. Dante Michelini, Jardim da Penha / Mata da Praia, Vitória - ES', 'Maior orla da capital, ideal para esportes, eventos e lazer ao ar livre'),
            ('Três Ilhas - Passeio Marítimo', '672 (Passeios de Escuna/Lancha)', -20.6652, -40.4855, 'Av. Beira Mar (Ponto de Escunas), Praia do Morro, Guarapari - ES', 'Arquipélago paradisíaco acessível por passeios marítimos saindo da Praia do Morro ou Setiba'),
            ('Praia do Morro', '008, 672, Alvorada (Intermunicipal)', -20.6653, -40.4872, 'Av. Beira Mar, Praia do Morro, Guarapari - ES', 'Uma das praias mais extensas e urbanizadas de Guarapari, muito procurada por turistas'),
            ('Parque Estadual do Forno Grande', 'Águia Branca, Carro (Uber/Particular)', -20.5289, -41.1119, 'Estrada de Forno Grande, Zona Rural, Castelo - ES', 'Unidade de conservação com trilhas, mirantes e o icônico Pico do Forno Grande'),
            ('Ponto Mestre Álvaro', '591, 834, 814', -20.1750, -40.3050, 'Serra Sede / Jardim Tropical, Serra - ES', 'Ponto de partida para trilhas guiadas'),
            ('Ponto Reis Magos / Nova Almeida', '806, 854, 873', -19.9285, -40.1925, 'R. Reis Magos, Nova Almeida, Serra - ES', 'Acesso à Igreja histórica e falésias'),
            ('Terminal Jacaraípe (Praia)', '810, 818, 863', -20.1585, -40.1950, 'Av. Abido Saadi, Serra - ES', 'Acesso à Praia de Jacaraípe e Monumento da Baleia'),
            ('Vila de Itaúnas (Praça)', 'Viação Águia Branca / Regional', -18.4250, -39.7030, 'Vila de Itaúnas, Conceição da Barra - ES', 'Ponto final na vila das dunas'),
            ('Guriri - Centro', 'Circular São Mateus', -18.7310, -39.7450, 'Ilha de Guriri, São Mateus - ES', 'Próximo ao Projeto Tamar'),
            ('Rodoviária de Linhares', 'Intermunicipal', -19.3950, -40.0650, 'Centro, Linhares - ES', 'Conexão para a Lagoa Juparanã'),
            ('Ponto Shopping Vitória', '211, 212, 505, 508, 510', -20.3125, -40.2880, 'Enseada do Suá, Vitória - ES', 'Ponto na entrada principal do shopping'),
            ('Ponto Manguinhos', '821, 883', -20.1840, -40.1870, 'Av. Atapoã, Manguinhos, Serra - ES', 'Acesso aos restaurantes de frutos do mar'),
            ('Rodoviária de Guarapari', 'Viação Alvorada / Planeta', -20.6620, -40.4980, 'Muquiçaba, Guarapari - ES', 'Acesso às praias de Setiba e Morro'),
            ('Ponto Aracruz (Sesc)', 'Viação Cordial / Expresso Aracruz', -19.8740, -40.2215, 'Rodovia ES-010, Santa Cruz, Aracruz - ES', 'Em frente ao Sesc Praia Formosa'),
            ('Ponto Shopping Vitória', '515, 523, 528, 541, 103, 211', -20.3120, -40.2885, 'Av. Américo Buaiz, Enseada do Suá, Vitória - ES', 'Ponto principal em frente à entrada sul'),
            ('Ponto Shopping Mestre Álvaro', '505, 508, 510, 800', -20.2395, -40.2760, 'Av. João Palácio, Serra - ES', 'Acesso direto pela passarela'),
            ('Ponto Shopping Montserrat', '541, 800, 814', -20.1940, -40.2660, 'Av. Eldes Scherrer Souza, Colina de Laranjeiras, Serra - ES', 'Ponto em frente ao shopping'),
            ('Ponto Shopping Vila Velha', '501, 508, 557, 650', -20.3475, -40.2995, 'Av. Luciano das Neves, Vila Velha - ES', 'Ponto próximo à entrada da UVV'),
            ('Ponto Shopping Moxuara', '591, 700, 727', -20.3108, -40.3870, 'Rodovia BR-262, Cariacica - ES', 'Acesso via passarela ou marginal'),
            ('Ponto Shopping Praia da Costa', '650, 662, 501', -20.3345, -40.2845, 'Av. Dr. Olivio Lira, Vila Velha - ES', 'Ponto na lateral do shopping'),
            ('Ponto Sítio Gava', '912, 913', -20.3970, -40.4760, 'Rua Projetada, Piapitangui, Viana - ES', 'Linhas rurais de Viana'),
            ('Ponto Fazenda Camping', '613, 619, 669', -20.4340, -40.3760, 'Rod. do Sol, Km 19, Vila Velha - ES', 'Ponto na Rodovia do Sol (entrada do Jucu)'),
            ('Rodoviária de Iúna', 'Viação Águia Branca / Real', -20.3450, -41.5300, 'Centro, Iúna - ES', 'Conexão para transporte local até o Poço do Egito'),
            ('Ponto Zoo Park', 'Viação Planeta (Intermunicipal)', -20.4240, -40.7800, 'BR-262, Marechal Floriano - ES', 'Descer na entrada de Rio Fundo e seguir via táxi/local')
            
        ]
        cursor.executemany("""
            INSERT INTO pontos_onibus (nome, linha, latitude, longitude, endereco, observacoes) 
            VALUES (?, ?, ?, ?, ?, ?)""", dados_onibus)
        
    # 4. Empreendedores (Adicionado o comando de inserção que faltava)
    # 4. Empreendedores (Corrigido contagem de colunas e erros de vírgula)
    cursor.execute("SELECT COUNT(*) FROM empreendedores")
    res_emp = cursor.fetchone()
    if res_emp and res_emp[0] == 0:
        dados_empreendedores = [
            ('Kaffa Cafeteria', 'Cafeteria', 'Especializada em cafés especiais e artesanais', None, '@kaffacafeteria', -20.2976, -40.2958, 'Praia do Canto, Vitória – ES', 5),
            ('Café Bamboo', 'Cafeteria e bistrô', 'Cafeteria tradicional na Praia do Canto, oferece cafés, brunch, bolos e refeições leves.', None, '@cafebamboo', -20.2949, -40.2923, 'Praia do Canto, Vitória – ES', 5),
            ('Terrafé Jardim Camburi', 'Cafeteria especializada', 'Pequena cafeteria com foco em cafés especiais e experiência sensorial do café capixaba.', None, '@espiritocafe', -20.2970, -40.2920, 'Vitória – ES', 5),
            ('Realcafé', 'Torrefação e cafeteria', 'Empresa capixaba de torrefação com atuação no mercado de cafés especiais e estrutura para visitação e degustação.', None, '@realcafeoficial', -20.3647, -40.4964, 'Viana – ES', 5),
            ('Artesanato Brasil', 'Loja de artesanato', 'Espaço que reúne diversos produtos feitos à mão, com peças decorativas e típicas capixabas.', '+55 27 3222-1373', None, -20.3202822, -40.3357877, 'Praça Costa Pereira, 226 – Centro, Vitória – ES', 2),
            ('Loja Artesanato Capixaba', 'Comércio de artesanato regional', 'Vitrine de produtos artesanais típicos capixabas, com peças em cerâmica e madeira.', '+55 27 99602-5367', None, -20.3168248, -40.2990504, 'Enseada do Suá, Vitória – ES', 2),
            ('Armarinho Celga', 'Loja de materiais artesanais', 'Armarinho tradicional oferecendo materiais para artesanato, bordados e costura.', '+55 27 99961-3192', None, -20.3027778, -40.2977778, 'Praia do Canto, Vitória – ES', 2),
            ('Casa do Artesanato & Rendas', 'Loja de artesanato tradicional', 'Espaço que oferece peças artesanais e rendas de bilros em Guarapari.', '+55 27 99705-1963', None, -20.736825, -40.540554, 'Meaípe, Guarapari – ES', 2),
            ('Artesanato da Terra', 'Loja de produtos artesanais', 'Loja com diversos itens artesanais, souvenirs e produtos locais.', '+55 27 9299-8888', None, -20.2941861, -40.3013244, 'Barro Vermelho, Vitória – ES', 2),
            ('Empório das Artes', 'Loja de artesanato', 'Produtos artesanais variados feitos por micro e pequenos produtores locais.', '+55 28 99978-4964', None, -20.8491515, -41.1118172, 'Cachoeiro de Itapemirim – ES', 2),
            ('Arts & Embroidery Brazil', 'Loja de artesanato', 'Loja que atende artesãos com grande variedade de produtos para bordado e pintura.', '+55 27 99782-8508', None, -20.3420299, -40.383147, 'Campo Grande, Cariacica – ES', 2),
            ('Quiosque Alegria', 'Quiosque de Praia', 'Oferecendo petiscos, porções e bebidas à beira-mar.', None, '@quiosquealegria', -20.2976, -40.2928, 'Praia do Canto, Vitória – ES', 1),
            ('Projeto Tamar Vitória', 'Centro Cultural e Ambiental', 'Preservação das tartarugas marinhas, com exposições educativas.', '(27) 3340-1234', '@projetotamaroficial', -20.3155, -40.2894, 'Praça do Papa, Vitória – ES', 2),
            ('VIX Logística', 'Transporte e Logística', 'Empresa especializada em transporte rodoviário e soluções logísticas.', '(27) 2121-0000', '@vixlogistica', -20.3150, -40.3128, 'Vitória – ES', 4),
            ('Restaurante Papaguth', 'Restaurante', 'Especializado em frutos do mar e culinária capixaba.', '(27) 3325-2525', '@papaguth', -20.2979, -40.2934, 'Praia do Canto, Vitória – ES', 5),
            ('Ateliê Arte Capixaba', 'Artesanato (MEI)', 'Peças decorativas com temática capixaba e materiais naturais.', '(27) 99754-3344', '@atelieartecapixaba', -20.3344, -40.2920, 'Centro, Vila Velha – ES', 2),
            ('Caparaó Trilhas', 'Guia de Turismo (MEI)', 'Serviço de guia local para trilhas no Caparaó e Pico da Bandeira.', '(28) 99921-7788', '@caparaotrilhas', -20.4400, -41.8300, 'Alto Caparaó – ES', 3),
            ('Carlos Transporte', 'Transporte Executivo (MEI)', 'Transfers para aeroporto e eventos na Grande Vitória.', '(27) 99812-5566', '@carlostransporte', -20.3155, -40.3128, 'Vitória – ES', 4),
            ('Doce Sabor da Ju', 'Confeitaria Artesanal (MEI)', 'Bolos, doces e sobremesas para festas e encomendas.', '(27) 99788-4455', '@docesabordaju', -20.3297, -40.2925, 'Jardim da Penha, Vitória – ES', 5),
            ('SM Receptivo Tour ES','Serviço de turismo (agência receptiva)','Agência de turismo receptivo em Vila Velha que organiza passeios guiados e roteiros personalizados pelo Espírito Santo, incluindo city tours e experiências com visitas a praias, centros históricos e atrações culturais.','+55 27 99528-0787','smreceptiv.es',-20.3563,-40.2949,'R. Deolindo Perim, 371 – Itaparica, Vila Velha – ES, 29102-050',5),
            ('City Tour Vitória e Vila Velha', 'Serviço de passeio turístico', 'Serviço de passeios guiados em van/ônibus por pontos culturais e turísticos.', '+55 27 3325-2000', '@agencia_local', -20.2872, -40.2947, 'Av. Anísio Fernandes Coelho, 631 – Jardim da Penha, Vitória – ES', 5),
            ('Ruraltur-ES', 'Agroturismo', 'Feira de experiências de turismo rural em Pindobas, com trilhas, degustações e gastronomia típica.', 'Consulte site oficial', '@ruraltures', -20.3934, -41.1434, 'Rod. Pedro Cola, km 9 – Pindobas, Venda Nova do Imigrante – ES', 3),
            ('Tero Brasa e Vinho', 'Restaurante Brasileiro', 'Churrasco e cozinha contemporânea com ambiente animado na Praia do Canto.', '+55 27 3100-9660', '@terobrasaevinho', -20.3040, -40.2960, 'R. Eugênio Netto, 326 – Praia do Canto, Vitória – ES', 5),
            ('Mahai', 'Cozinha Contemporânea/Havaiana', 'Pratos diferenciados e saudáveis, ideal para quem frequenta as praias de Vitória.', '+55 27 3100-0011', '@restaurantemahai', -20.3016, -40.2973, 'R. Aleixo Netto, 577 – Praia do Canto, Vitória – ES', 5),
            ('Ilha do Caranguejo', 'Restaurante de Frutos do Mar', 'Clássico de Vitória com ambiente temático, famoso pelo caranguejo e pratos típicos capixabas.', '+55 27 3395-0244', '@ilhadocaranguejo', -20.2549, -40.2692, 'R. Alcino Pereira Neto, 570 – Jardim Camburi, Vitória – ES', 5),
            ('Restaurante El Gitano', 'Restaurante Variado', 'Localizado na Enseada do Suá, ideal para almoços durante passeios por centros culturais e mirantes.', '+55 27 99248-9096', '@elgitanovitoria', -20.3094, -40.2879, 'Av. José Miranda Machado, 345 – Enseada do Suá, Vitória – ES', 5),
            ('Restaurante Papaguth', 'Frutos do Mar e Eventos', 'Localizado na Praça do Papa, oferece culinária capixaba com uma vista panorâmica da Baía de Vitória e do Convento da Penha.', '+55 27 3225-5773', '@papaguth', -20.3183, -40.2955, 'Praça do Papa, Enseada do Suá, Vitória – ES', 5),
            ('Restaurante Pirão', 'Frutos do Mar e Típica', 'Um dos destaques tradicionais da Praia do Canto, famoso pela moqueca e pratos à base de frutos do mar.', '+55 27 3227-1165', '@restaurantepirao', -20.2954, -40.2915, 'R. Joaquim Lírio, 753 – Praia do Canto, Vitória – ES', 5),
            ('Coco Bambu Vila Velha', 'Restaurante de Frutos do Mar', 'Localizado no Shopping Praia da Costa, oferece um menu extenso de frutos do mar em um ambiente amplo e sofisticado.', '+55 27 3141-9100', '@cocobambu.vilavelha', -20.3419, -40.2888, 'Av. Dr. Olivio Lira, 353 – Praia da Costa, Vila Velha – ES', 5),
            ('Restaurante Atlântica Praia da Costa', 'Frutos do Mar e Típica', 'Ambiente tradicional e descontraído na orla da Praia da Costa, famoso por sua moqueca e vista para o mar.', '+55 27 3329-2341', '@restauranteatlantica', -20.3316, -40.2745, 'Av. Antônio Gil Veloso, 80 – Praia da Costa, Vila Velha – ES', 5),
            ('WE Salão de Beleza', 'Salão de Beleza', 'Serviços completos de cabelo e estética localizados no coração de Laranjeiras, Serra.', '+55 27 99995-8784', '@wesalaodebeleza', -20.1960, -40.2592, 'R. Santos Dumont, 210 – Parque Res. Laranjeiras, Serra – ES', 5),
            ('Salão Espírito Santo', 'Salão de Beleza', 'Salão de beleza tradicional e acolhedor localizado no bairro Ibes, Vila Velha.', '+55 27 3239-8029', '@salaoespiritosanto', -20.3523, -40.3164, 'R. Nelson Monteiro, 127 – Ibes, Vila Velha – ES', 5),
            ('Be Spa Urbano', 'Salão de Beleza e Spa', 'Experiência de bem-estar e estética de alto padrão localizada no coração da Praia do Canto.', '+55 27 99698-0173', '@bespaurbano', -20.3046, -40.2949, 'R. Eugênio Netto, 180 – Praia do Canto, Vitória – ES', 5),
            ('Salão Emilia Coiffeur & Rainha das Loiras', 'Salão de Beleza / Especialista', 'Referência em loiros e serviços variados de beleza, localizado estrategicamente na Enseada do Suá.', '+55 27 99846-5920', '@emiliacoiffeur', -20.3147, -40.2952, 'R. Clóvis Machado, 155 – Enseada do Suá, Vitória – ES', 5),
            ('Beauty Lounge - Salão Express', 'Salão de Beleza Express', 'Serviços ágeis e atendimento personalizado no coração do polo comercial da Glória.', '+55 27 99270-3333', '@beautylounge_express', -20.3367, -40.3047, 'R. Dom Pedro II, 549 – Glória, Vila Velha – ES', 5),
            ('Belezura Fast Beauty', 'Salão de Beleza Fast', 'Serviços de cabelo e estética com foco em agilidade no coração da Praia do Canto.', '+55 27 99503-1497', '@belezurafastbeauty', -20.2991, -40.2936, 'R. Chapot Presvot, 149 – Praia do Canto, Vitória – ES', 5),
            ('Nales - Salão de Beleza', 'Salão de Beleza', 'Serviços especializados de cabelo e estética em localização privilegiada na Praia do Canto.', '+55 27 3019-1596', '@nalessalao', -20.2948, -40.2950, 'R. Afonso Cláudio, 452 – Praia do Canto, Vitória – ES', 5),
            ('Salão de beleza La Beauté', 'Salão de Beleza', 'Atendimento especializado em estética e beleza localizado na região de maior crescimento de Vila Velha, a Praia de Itaparica.', '+55 27 99183-8660', '@labeauteitaparica', -20.3626, -40.2974, 'R. Itapemirim, 45 – Praia de Itaparica, Vila Velha – ES', 5),
            ('Salão Edy Penteado', 'Salão de Beleza e Penteados', 'Especialista em penteados e serviços de estética, localizado no bairro Novo Horizonte, em Linhares.', '+55 27 99932-6531', '@edypenteado', -19.3823, -40.0575, 'Av. Pref. Manoel Salustiano de Souza, 93 – Novo Horizonte, Linhares – ES', 5),
            ('Salão Imagem CABELO & ESTÉTICA', 'Salão de Beleza', 'Salão completo com serviços de estética e cabelo em uma das avenidas mais movimentadas de Jardim da Penha.', '+55 27 98829-1274', '@salaoimagemjp', -20.2796, -40.2957, 'Av. Hugo Viola, 931 – Jardim da Penha, Vitória – ES', 5),
            ('Instituto Beleza Natural Vila Velha', 'Salão de Beleza / Rede Especializada', 'Localizado no Shopping Vila Velha, referência em cuidados para cabelos crespos e cacheados.', '+55 21 98555-4235', '@belezanatural', -20.3509, -40.2982, 'Av. Luciano das Neves, 2418 – Divino Espírito Santo, Vila Velha – ES', 5),
            ('Beauty Club Salon', 'Salão de Beleza', 'Espaço de beleza completo localizado na movimentada Rua da Lama, em Jardim da Penha.', '+55 27 3025-2079', '@beautyclubsalon', -20.2876, -40.2942, 'Av. Anísio Fernandes Coelho, 661 – Jardim da Penha, Vitória – ES', 5),
            ('Tetobeauty', 'Salão de Beleza / Horário Estendido', 'Salão com atendimento em horários diferenciados, localizado na principal via de acesso de Vitória, a Reta da Penha.', '+55 27 99202-4321', '@tetobeauty', -20.2881, -40.3038, 'Av. Nossa Sra. da Penha, 2796 – Santa Luíza, Vitória – ES', 5),
            ('Studio Walace Menezes', 'Salão de Beleza / Alto Padrão', 'Referência em cortes e coloração na Praia do Canto, com atendimento personalizado e ambiente sofisticado.', '+55 27 99144-4717', '@studiowm', -20.3014, -40.2924, 'R. Moacir Avidos, 47 – Praia do Canto, Vitória – ES', 5),
            ('Studio Jhessica Ribeiro Lash Designer', 'Design de Cílios e Estética', 'Estúdio especializado em extensão de cílios e estética avançada com avaliação máxima em Vila Velha.', '+55 27 99879-8521', '@jhessicaribeiro.lash', -20.3504, -40.3034, 'R. Vital Brasil, 490 – Soteco, Vila Velha – ES', 5),
            ('IlhasTour Turismo Náutico', 'Turismo Náutico / Passeios', 'Mais de 10 anos realizando roteiros de lancha pelas ilhas e praias do litoral capixaba.', '+55 27 99760-6418', '@ilhastour', -20.3517, -40.2878, 'Praia da Costa, Vila Velha – ES', 5),
            ('Barco Nativo Guarapari', 'Turismo Náutico / Lazer', 'Passeios e aluguel de embarcações para mergulhos e tours exclusivos pelas praias e ilhas de Guarapari.', '+55 27 99775-2289', '@barconativo', -20.6685, -40.4986, 'Tv. Antônio Laurindo de Souza, 217 – Itapebussu, Guarapari – ES', 5),
            ('Escuna em Guarapari-ES', 'Turismo Náutico / Escuna', 'Passeios tradicionais de escuna e lancha partindo do Centro de Guarapari, com roteiros pelas principais praias.', '+55 27 99878-8333', '@escunaguarapari', -20.6681, -40.4979, 'Cais das Escunas – Centro, Guarapari – ES', 5),
            ('Capitão Grilo – Turismo Náutico', 'Turismo Náutico / Lancha', 'Passeios de lancha personalizados partindo da Enseada do Suá, com roteiros pelas ilhas e cartões-postais de Vitória.', 'Consulte no Instagram', '@capitaogriloes', -20.3185, -40.2989, 'Píer dos Pescadores, Enseada do Suá – Vitória – ES', 5),
            ('Summer Vix – Aluguel de Lancha', 'Aluguel de Lancha / Passeios', 'Locação de lanchas e roteiros náuticos premium atendendo Vitória e Vila Velha, com foco em lazer e eventos marítimos.', '+55 27 99877-5147', '@summervix', -20.3498, -40.2842, 'Av. Antônio Gil Veloso, 2558 – Praia da Costa, Vila Velha – ES', 5),
            ('Escuna Princesinha do Mar', 'Turismo Náutico / Escuna', 'Passeios de escuna pelo Rio Piraqueaçu e orla de Aracruz, unindo história, natureza e lazer marítimo.', '+55 27 99851-9642', '@escunaprincesinhadomar', -19.9475, -40.1523, 'R. Gazir Sérvulo dos Santos, Pontal do Piraqueaçu, Aracruz – ES', 5),
            ('Netuno Cotas Náuticas', 'Serviço Náutico / Aluguel', 'Especialista em cotas náuticas e aluguel de barcos no Pontal de Camburi, ideal para lazer e esportes aquáticos.', '+55 27 99511-0047', '@netunocotasnauticas', -20.2890, -40.3000, 'R. Thereza Zanoni Caser, 221 – Pontal de Camburi, Vitória – ES', 5),
            ('Restaurante do Mestre', 'Gastronomia', 'Comida caseira para trilheiros após a descida do Mestre Álvaro.', '(27) 99900-1122', '@restdomestre', -20.1780, -40.3120, 'Serra Sede, Serra - ES', 5),
            ('Quiosque do Peixe - Nova Almeida', 'Quiosque', 'Especialista em Peroá frito com vista para as falésias.', None, '@quiosquenovalameda', -19.9250, -40.1940, 'Orla de Nova Almeida, Serra - ES', 5),
            ('Pousada das Dunas Itaúnas', 'Hospedagem', 'Pousada rústica e charmosa próxima ao local do Festival de Forró.', '(27) 3762-1100', '@pousadaitaunas', -18.4255, -39.7035, 'Vila de Itaúnas, Conceição da Barra - ES', 5),
            ('Artesanato de São Mateus', 'Loja de Artesanato', 'Venda de peças em barro e palha produzidas por comunidades locais.', None, '@artesãomateus', -18.7155, -39.8650, 'Porto de São Mateus, ES', 2),
            ('Guia Caparaó Adventure', 'Guia de Turismo', 'Especialista em trilhas para o Poço do Egito e Pico da Bandeira.', '(28) 99888-7766', '@caparaoadventure', -20.3420, -41.5270, 'Iúna - ES', 5),
            ('Restaurante Recanto de Manguinhos', 'Restaurante', 'Famoso pelo arroz de marisco e moqueca capixaba.', '(27) 3243-1122', '@recantomanguinhos', -20.1835, -40.1860, 'Manguinhos, Serra - ES', 5),
            ('Café com Vista - Matilde', 'Cafeteria', 'Cafés da região das montanhas com vista para a cachoeira.', None, '@cafematilde', -20.6350, -40.7425, 'Matilde, Alfredo Chaves - ES', 5),
            ('Aluguel de Caiaque Juparanã', 'Lazer e Esporte', 'Aluguel de equipamentos para explorar a Lagoa Juparanã.', '(27) 99777-4433', '@juparanakayak', -19.4020, -40.0700, 'Linhares - ES', 5),
            ('Doces de Castelo', 'Produtos Regionais', 'Venda de doces caseiros, queijos e embutidos próximos ao Forno Grande.', None, '@docescastelo', -20.5170, -41.0840, 'Castelo - ES', 5),
            ('Surfe Jacaraípe School', 'Escola de Surfe', 'Aulas de surfe para iniciantes na Praia de Jacaraípe.', '(27) 99665-4433', '@surfejacaraipe', -20.1600, -40.1895, 'Jacaraípe, Serra - ES', 5),
            ('Gelateria do Porto - Shopping Vitória', 'Gastronomia', 'Sorvetes artesanais italianos localizados na praça de alimentação.', None, '@gelatoportovix', -20.3129, -40.2870, 'Shopping Vitória, ES', 5),
            ('Livraria Leitura - Mestre Álvaro', 'Comércio', 'Livraria completa com espaço para café e eventos culturais.', '(27) 3211-0000', '@leituramestrealvaro', -20.2392, -40.2753, 'Serra - ES', 2),
            ('Brinquedoteca Magic Games', 'Lazer Infantil', 'Espaço de diversão para crianças dentro do Shopping Vila Velha.', None, '@magicgamesoficial', -20.3481, -40.2987, 'Vila Velha - ES', 5),
            ('Restaurante Argento Parrilla', 'Gastronomia', 'Especializado em cortes de carnes argentinas na Praia da Costa.', '(27) 3329-0000', '@argentoparrilla', -20.3348, -40.2839, 'Shopping Praia da Costa, ES', 5),
            ('Açaí do Gava', 'Lanchonete', 'Quiosque de açaí e lanches naturais dentro do sítio.', None, '@acaigava', -20.3968, -40.4753, 'Piapitangui, Viana - ES', 5),
            ('Guia Ecológico Itabira', 'Serviço de Turismo', 'Condutores locais para trilhas de escalada no Pico do Itabira.', '(28) 99955-2211', '@ecoparkitabira_guias', -20.8916, -41.1578, 'Cachoeiro de Itapemirim - ES', 3),
            ('Lojinha do Zoo Park', 'Souvenirs', 'Venda de bichinhos de pelúcia e lembranças do zoológico.', None, '@zooparkmontanha', -20.4236, -40.7790, 'Marechal Floriano - ES', 2),
            ('Restaurante Thermas', 'Gastronomia', 'Self-service e porções que atende os visitantes do parque aquático.', '(27) 3262-0011', '@thermasinternacional', -20.5013, -40.4098, 'Guarapari - ES', 5),
            ('Iúna Adventure', 'Agência Receptiva', 'Transfer e passeios para o Poço do Egito e Hidrolândia.', '(28) 99881-0099', '@iunaadventure', -20.3415, -41.5260, 'Iúna - ES', 5),
            ('Cafeteria Montserrat', 'Cafeteria', 'Grãos selecionados das montanhas capixabas no Shopping Montserrat.', None, '@cafemontserrat', -20.1936, -40.2654, 'Serra - ES', 5)

        ]
        cursor.executemany("""
            INSERT INTO empreendedores (nome, tipo, descricao, telefone, instagram, latitude, longitude, endereco, categoria_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", dados_empreendedores)
    


    conn.commit()
    conn.close()
    print("Banco de dados do Espírito Santo configurado com sucesso!")

if __name__ == "__main__":
    init_db()
 