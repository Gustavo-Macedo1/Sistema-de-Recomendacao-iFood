# -*- coding: utf-8 -*-

import sqlite3

def init_db(db_name="ifood_dataset.db"):
    conn, cursor = connect_db(db_name)

    # Habilita suporte a chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Tabela MERCHANT (Estabelecimentos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS merchant (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK(status IN ('AVAILABLE', 'UNAVAILABLE', 'DISABLED')) DEFAULT 'AVAILABLE',
        distance REAL NOT NULL
    );
    """)

    # 2. Tabela ITEM (Produtos/Refeições)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL,
        status TEXT CHECK(status IN ('AVAILABLE', 'UNAVAILABLE')) DEFAULT 'AVAILABLE',
        
        price_value REAL NOT NULL,
        price_original_value REAL,
        discount REAL DEFAULT 0.0,
        
        is_vegetariano INTEGER DEFAULT 0 CHECK(is_vegetariano IN (0, 1)),
        is_vegano INTEGER DEFAULT 0 CHECK(is_vegano IN (0, 1)),
        is_organico INTEGER DEFAULT 0 CHECK(is_organico IN (0, 1)),
        is_sem_gluten INTEGER DEFAULT 0 CHECK(is_sem_gluten IN (0, 1)),
        is_sem_acucar INTEGER DEFAULT 0 CHECK(is_sem_acucar IN (0, 1)),
        is_zero_lactose INTEGER DEFAULT 0 CHECK(is_zero_lactose IN (0, 1))
    );
    """)

    # 3. Tabela CATALOG (Associação entre Merchant e Item)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalog (
        merchant_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        PRIMARY KEY (merchant_id, item_id),
        FOREIGN KEY (merchant_id) REFERENCES merchant(id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
    );
    """)

    # 4. Tabela AUXILIAR: REVIEWS (Fundamental para a inteligência da sua LLM)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS merchant_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_id INTEGER NOT NULL,
        rating REAL CHECK(rating >= 1.0 AND rating <= 5.0),
        comment TEXT NOT NULL,
        FOREIGN KEY (merchant_id) REFERENCES merchant(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    print("✓ Esquema de banco de dados SQLite criado com sucesso!")

    # Inserção de dados de teste (Seed Data)
    seed_data(conn)
    add_more_items(db_name)

    conn.close()

def connect_db(db_name="ifood_dataset.db"):
    # Conecta ao banco (cria o arquivo se não existir)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    return (conn, cursor)


def seed_data(conn):
    cursor = conn.cursor()

    # Limpar dados antigos para permitir reexecução limpa do script
    cursor.execute("DELETE FROM catalog;")
    cursor.execute("DELETE FROM item;")
    cursor.execute("DELETE FROM merchant;")
    cursor.execute("DELETE FROM merchant_review;")

    # Inserir Merchants
    merchants = [
        (1, "Burger King Size", "Hambúrgueres grelhados no fogo e porções.", "AVAILABLE", 2.3),
        (2, "Dogão do Zé", "Cachorros-quentes prensados e tradicionais.", "AVAILABLE", 1.8),
        (3, "Green Light Plant-Based", "Comida saudável, hambúrgueres veganos e sem lactose.", "AVAILABLE", 4.1),
    ]
    cursor.executemany("INSERT INTO merchant VALUES (?, ?, ?, ?, ?)", merchants)

    # Inserir Items
    # Estrutura: (id, nome, descricao, status, price_value, price_original_value, discount, veg, vegan, org, s_gluten, s_acucar, z_lactose)
    items = [
        ("ITM-01", "X-Tudo Artesanal", "Pão brioche, 180g carne, bacon, queijo, salada e maionese da casa.", "AVAILABLE", 32.90, 38.00, 13.4, 0, 0, 0, 0, 0, 0),
        ("ITM-02", "Cachorro-Quente Duplo Prensado", "Duas salsichas, vinagrete, milho, batata palha e maionese.", "AVAILABLE", 18.50, None, 0.0, 0, 0, 0, 0, 0, 0),
        ("ITM-03", "Smash Burger Vegano", "Hambúrguer de grão-de-bico, queijo vegano zero lactose e salada.", "AVAILABLE", 29.00, 34.00, 14.7, 1, 1, 0, 1, 1, 1),
        ("ITM-04", "Chicken Burger Crocante", "Hambúrguer de frango empanado, maionese sem lactose e alface.", "AVAILABLE", 26.00, None, 0.0, 0, 0, 0, 0, 0, 1),
    ]
    cursor.executemany("INSERT INTO item VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", items)

    # Inserir Catalogs (Associações)
    catalogs = [
        (1, "ITM-01"), # Burger King Size -> X-Tudo
        (1, "ITM-04"), # Burger King Size -> Chicken Burger
        (2, "ITM-02"), # Dogão do Zé -> Cachorro-Quente
        (3, "ITM-03"), # Green Light -> Smash Burger Vegano
    ]
    cursor.executemany("INSERT INTO catalog VALUES (?, ?)", catalogs)

    # Inserir Reviews de Exemplo (para o seu Agente testar se a comida veio fria, etc.)
    reviews = [
        (1, 4.5, "Lanche excelente, mas as batatas vieram um pouco murchas."),
        (1, 1.5, "Pedi um X-tudo e veio muito frio, demorou bastante."),
        (2, 4.8, "Cachorro quente muito bem servido e quentinho! Barato demais."),
        (3, 5.0, "Ótima opção zero lactose! Ingredientes bem frescos."),
    ]
    cursor.executemany("INSERT INTO merchant_review (merchant_id, rating, comment) VALUES (?, ?, ?)", reviews)

    conn.commit()
    print("✓ Banco populado com dados de teste!")

def add_more_items(db_name="ifood_dataset.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Habilita suporte a chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Estrutura do item:
    # (id, nome, descricao, status, price_value, price_original_value, discount, is_veg, is_vegan, is_org, is_s_gluten, is_s_acucar, is_z_lactose)
    new_items = [
        # ==========================================
        # ITENS PARA O MERCHANT 1: Burger King Size (ID: 1)
        # ==========================================
        ("ITM-101", "Smash Burger Duplo", "Dois hambúrgueres de 90g, queijo cheddar duplo e molho especial.", "AVAILABLE", 24.90, 29.90, 16.7, 0, 0, 0, 0, 0, 0),
        ("ITM-102", "Monster Bacon BBQ", "Três carnes de 150g, muito bacon crocante, cheddar e molho barbecue.", "AVAILABLE", 42.00, None, 0.0, 0, 0, 0, 0, 0, 0),
        ("ITM-103", "Chicken Crispy Deluxe", "Hambúrguer de frango empanado, maionese temperada e salada verde.", "AVAILABLE", 27.50, 31.00, 11.3, 0, 0, 0, 0, 0, 0),
        ("ITM-104", "Burger de Cogumelos Veggie", "Hambúrguer vegetal com cogumelos shimeji refogados e queijo.", "AVAILABLE", 31.00, None, 0.0, 1, 0, 0, 0, 0, 0),
        ("ITM-105", "Batata Frita Suprema", "Porção grande de batata frita crocante com molho de cheddar e bacon.", "AVAILABLE", 19.90, 23.00, 13.5, 0, 0, 0, 0, 0, 0),
        ("ITM-106", "Onion Rings Crocantes", "Anéis de cebola empanados e fritos acompanhados de molho barbecue.", "AVAILABLE", 16.00, None, 0.0, 1, 0, 0, 0, 0, 0),
        ("ITM-107", "Milkshake de Ovomaltine", "Milkshake cremoso de 500ml feito com sorvete artesanal.", "AVAILABLE", 18.00, None, 0.0, 1, 0, 0, 0, 0, 0),
        ("ITM-108", "Refrigerante Cola 350ml", "Lata de refrigerante gelada 350ml.", "AVAILABLE", 6.50, None, 0.0, 1, 1, 0, 1, 0, 1),
        ("ITM-109", "X-Salada Tradicional", "Pão macio, hambúrguer de 150g, queijo prato, alface e tomate.", "AVAILABLE", 22.00, 25.00, 12.0, 0, 0, 0, 0, 0, 0),
        ("ITM-110", "Brownie de Chocolate com Gelato", "Brownie quente acompanhado de uma bola de sorvete de baunilha.", "AVAILABLE", 15.00, None, 0.0, 1, 0, 0, 0, 0, 0),

        # ==========================================
        # ITENS PARA O MERCHANT 2: Dogão do Zé (ID: 2)
        # ==========================================
        ("ITM-201", "Cachorro-Quente Simples", "Pão macio, 1 salsicha, molho de tomate caseiro, milho e batata palha.", "AVAILABLE", 12.00, None, 0.0, 0, 0, 0, 0, 0, 0),
        ("ITM-202", "Dogão de Frango Desfiado", "Pão, 1 salsicha, frango desfiado temperado, catupiry e batata palha.", "AVAILABLE", 17.00, 20.00, 15.0, 0, 0, 0, 0, 0, 0),
        ("ITM-203", "Dogão com Calabresa Prensado", "Salsicha, calabresa fatiada, queijo derretido, vinagrete e maionese.", "AVAILABLE", 19.50, None, 0.0, 0, 0, 0, 0, 0, 0),
        ("ITM-204", "Dogão Vegano de Grão-de-Bico", "Pão vegano, salsicha vegetal de grão-de-bico, vinagrete e purê de batata.", "AVAILABLE", 21.00, 24.00, 12.5, 1, 1, 0, 0, 1, 1),
        ("ITM-205", "Cachorro-Quente de Linguiça Artesanal", "Pão australiano, linguiça suína grelhada, queijo provolone e vinagrete.", "AVAILABLE", 23.00, None, 0.0, 0, 0, 0, 0, 0, 0),
        ("ITM-206", "Porção de Mini Coxinhas (12 un)", "Mini coxinhas de frango bem crocantes e sequinhas.", "AVAILABLE", 16.90, 19.90, 15.0, 0, 0, 0, 0, 0, 0),
        ("ITM-207", "Suco Natural de Laranja 500ml", "Suco de laranja 100% natural espremido na hora.", "AVAILABLE", 8.50, None, 0.0, 1, 1, 1, 1, 1, 1),
        ("ITM-208", "Refrigerante Guaraná 350ml", "Lata de refrigerante gelada 350ml.", "AVAILABLE", 6.50, None, 0.0, 1, 1, 0, 1, 0, 1),
        ("ITM-209", "Dogão Doce de Prestígio", "Pão doce, creme de chocolate e coco ralado.", "AVAILABLE", 14.00, None, 0.0, 1, 0, 0, 0, 0, 0),
        ("ITM-210", "Dogão Mexicano Apimentado", "Salsicha, pimenta jalapeño, chilli de carne moída e queijo cheddar.", "AVAILABLE", 22.50, None, 0.0, 0, 0, 0, 0, 0, 0),

        # ==========================================
        # ITENS PARA O MERCHANT 3: Green Light Plant-Based (ID: 3)
        # ==========================================
        ("ITM-301", "Burger Vegano de Lentilha", "Hambúrguer de lentilha temperada, queijo vegetal, tomate e maionese verde.", "AVAILABLE", 28.00, 32.00, 12.5, 1, 1, 1, 1, 1, 1),
        ("ITM-302", "Wrap de Faláfel Zero Lactose", "Massa folhada leve, faláfel de grão-de-bico, homus e salada fresca.", "AVAILABLE", 26.50, None, 0.0, 1, 1, 1, 0, 1, 1),
        ("ITM-303", "Cachorro-Quente Vegano de NotDog", "Pão artesanal sem glúten, notdog vegetal, purê sem lactose e batata palha.", "AVAILABLE", 25.00, 28.50, 12.2, 1, 1, 0, 1, 1, 1),
        ("ITM-304", "Bowl Proteico Sem Glúten", "Quinoa, cogumelos grelhados, abacate, tofu temperado e sementes.", "AVAILABLE", 34.00, None, 0.0, 1, 1, 1, 1, 1, 1),
        ("ITM-305", "Batata Rústica Assada com Ervas", "Porção de batata rústica assada com alecrim e azeite extravirgem.", "AVAILABLE", 17.90, None, 0.0, 1, 1, 1, 1, 1, 1),
        ("ITM-306", "Coxinha Vegana de Jaca", "Coxinha frita recheada com carne de jaca desfiada super temperada.", "AVAILABLE", 9.50, None, 0.0, 1, 1, 0, 0, 1, 1),
        ("ITM-307", "Kombucha Orgânica de Gengibre 300ml", "Bebida fermentada probiótica natural e refrescante.", "AVAILABLE", 14.50, None, 0.0, 1, 1, 1, 1, 1, 1),
        ("ITM-308", "Smoothie Detox Verde 400ml", "Batido de couve, abacaxi, hortelã e água de coco.", "AVAILABLE", 13.00, 15.00, 13.3, 1, 1, 1, 1, 1, 1),
        ("ITM-309", "Cheesecake Vegano de Frutas Vermelhas", "Sobremesa à base de castanha-de-caju e geleia de frutas vermelhas sem açúcar.", "AVAILABLE", 19.00, None, 0.0, 1, 1, 1, 1, 1, 1),
        ("ITM-310", "Salada Caesar Vegana", "Mix de folhas, croutons sem glúten, molho de castanhas e 'bacon' de coco.", "AVAILABLE", 27.00, None, 0.0, 1, 1, 1, 1, 1, 1)
    ]

    # Inserir os novos itens na tabela ITEM
    cursor.executemany("""
    INSERT OR REPLACE INTO item VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, new_items)

    # Mapear os novos itens para os respectivos Merchants na tabela CATALOG
    catalogs = [
        # Merchant 1 (Burger King Size)
        (1, "ITM-101"), (1, "ITM-102"), (1, "ITM-103"), (1, "ITM-104"), (1, "ITM-105"),
        (1, "ITM-106"), (1, "ITM-107"), (1, "ITM-108"), (1, "ITM-109"), (1, "ITM-110"),

        # Merchant 2 (Dogão do Zé)
        (2, "ITM-201"), (2, "ITM-202"), (2, "ITM-203"), (2, "ITM-204"), (2, "ITM-205"),
        (2, "ITM-206"), (2, "ITM-207"), (2, "ITM-208"), (2, "ITM-209"), (2, "ITM-210"),

        # Merchant 3 (Green Light Plant-Based)
        (3, "ITM-301"), (3, "ITM-302"), (3, "ITM-303"), (3, "ITM-304"), (3, "ITM-305"),
        (3, "ITM-306"), (3, "ITM-307"), (3, "ITM-308"), (3, "ITM-309"), (3, "ITM-310"),
    ]

    cursor.executemany("""
    INSERT OR REPLACE INTO catalog VALUES (?, ?)
    """, catalogs)

    conn.commit()
    print(f"✓ Sucesso! Foram inseridos {len(new_items)} novos itens associados aos seus respectivos estabelecimentos.")
    conn.close()

if __name__ == "__main__":
    init_db()