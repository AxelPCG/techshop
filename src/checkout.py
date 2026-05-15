# Este arquivo contém código propositalmente ruim para fins educacionais em uma aula de refatoração.
# MÁS PRÁTICAS APLICADAS:
# 1. Função única com múltiplas responsabilidades (validação, cálculo, pagamento).
# 2. Nomes de variáveis ruins e não descritivos (x1, val, p, temp, res).
# 3. Falta de tipagem de dados (sem type hints).
# 4. Manipulação de dicionários brutos em vez de modelos de dados (sem Pydantic).
# 5. Aninhamento profundo de condicionais (código espaguete).
# 6. "Números mágicos" espalhados pelo código (valores fixos sem explicação).
# 7. Mock de chamadas externas e validações com prints.
# 8. Falta de tratamento de erros robusto.

# Simulação de uma biblioteca de requisições HTTP para não adicionar dependências reais.
class FakeResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
    def json(self):
        return self._json_data

def fake_post(url, json):
    """Simula uma chamada POST para uma API de pagamento."""
    print(f"--- Simulando POST para API de pagamento: {url} ---")
    if json['valor_total'] > 0 and json['valor_total'] < 9999:
        print("--- Pagamento APROVADO (simulado) ---")
        return FakeResponse(200, {"status": "pagamento_aprovado", "transacao_id": "xyz123abc"})
    else:
        print("--- Pagamento RECUSADO (simulado) ---")
        return FakeResponse(400, {"status": "pagamento_recusado", "motivo": "valor_invalido"})


def processar_tudo(cart_data, u_data):
    """
    Função gigante e mal escrita para processar um checkout completo.
    Recebe dados do carrinho e do usuário em formato de dicionário.
    """
    print("Iniciando processamento de checkout...")
    val = 0
    
    if cart_data and 'items' in cart_data:
        # Validação de estoque e cálculo de valor
        for p in cart_data['items']:
            print(f"Verificando estoque para o produto ID: {p['id']}...")
            # Estoque mockado
            estoque_disponivel = 10
            if p['qtd'] <= estoque_disponivel:
                print(f"Estoque OK para {p['qtd']} unidades do produto {p['id']}.")
                x1 = p['preco'] * p['qtd']
                val = val + x1
            else:
                print(f"ERRO: Estoque insuficiente para o produto {p['id']}.")
                return "Erro de estoque"

        # Cálculo de frete e descontos
        if val > 0:
            print(f"Valor parcial: {val}")
            # Frete fixo
            frete = 15.50
            val = val + frete
            print(f"Valor com frete: {val}")

            # Lógica de desconto aninhada
            if val > 200:
                if u_data['vip']:
                    print("Aplicando desconto VIP de 15%")
                    val = val * 0.85
                else:
                    print("Aplicando desconto padrão de 5%")
                    val = val * 0.95
            
            # Simulação de chamada para API de pagamento
            print("Preparando para processar pagamento...")
            dados_pagamento = {
                "id_usuario": u_data['id'],
                "valor_total": round(val, 2),
                "info_cartao": "XXXX-XXXX-XXXX-1234" # Dados sensíveis hardcoded
            }
            
            res = fake_post("https://api.pagamento.exemplo/processar", json=dados_pagamento)
            
            if res.status_code == 200:
                temp = res.json()
                if temp['status'] == 'pagamento_aprovado':
                    print(f"Checkout finalizado com sucesso! ID da transação: {temp['transacao_id']}")
                    return {"sucesso": True, "transacao": temp['transacao_id']}
                else:
                    print("Ocorreu um problema com o pagamento.")
                    return {"sucesso": False, "erro": "problema_na_api_de_pagamento"}
            else:
                print("API de pagamento retornou um erro.")
                return {"sucesso": False, "erro": "api_pagamento_offline"}
        else:
            print("Carrinho vazio, nenhum valor a processar.")
            return "Carrinho vazio"
    else:
        print("Dados do carrinho estão vazios ou em formato inválido.")
        return "Dados inválidos"
