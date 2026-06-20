# Product Requirements Document: TechShop

## 1. Objetivo

O objetivo do projeto TechShop é desenvolver uma plataforma de e-commerce robusta e escalável. O foco inicial (MVP) é a implementação de um carrinho de compras funcional e um processo de checkout seguro, proporcionando uma experiência de usuário fluida e confiável.

## 2. Requisitos Funcionais

- **Gerenciamento de Carrinho:** Usuários devem ser capazes de adicionar, remover e visualizar produtos em seu carrinho de compras.
- **Checkout:** O processo de checkout deve ser simples, seguro e coletar as informações necessárias para o envio e pagamento.
- **Visualização de Produtos:** Usuários devem poder navegar e ver detalhes dos produtos.

## 3. Requisitos Não-Funcionais

- **Segurança:** Todas as transações e dados do usuário devem ser criptografados.
- **Desempenho:** A aplicação deve ter um tempo de resposta rápido, mesmo com um grande número de usuários simultâneos.
- **Escalabilidade:** A arquitetura deve permitir o crescimento futuro da plataforma.

## 4. Melhorias de Qualidade — Shift Left

As práticas abaixo devem ser aplicadas **antes** da integração de qualquer código na branch principal, reduzindo o custo de correção de defeitos ao detectá-los o mais cedo possível no ciclo de desenvolvimento.

### SL-001 — Verificação Estática de Tipos no CI
Todo código Python submetido via Pull Request deve passar pela verificação `mypy --strict` como etapa obrigatória do pipeline de CI/CD. Erros de tipo bloqueiam o merge. Isso elimina uma classe inteira de bugs de runtime antes da execução, sem custo de teste adicional.

### SL-002 — Cobertura de Testes Unitários Obrigatória (padrão AAA)
Cada método público de domínio (ex.: `add_item`, `remove_item`, `calculate_total`, `calculate_total_with_discount`) deve ter ao menos um teste unitário seguindo o padrão Arrange-Act-Assert. O pipeline rejeita PRs com cobertura abaixo de 80% nos módulos de domínio (`src/cart.py`, `src/models.py`). Bugs de regra de negócio — como aceitar preço negativo ou quantidade zero — são identificados na fase de desenvolvimento, não em produção.

### SL-003 — Validação de Contrato de Dados na Borda do Sistema
Todos os modelos de entrada e saída da API devem ser definidos com schemas Pydantic com validadores explícitos (`field_validator`) antes de qualquer integração com serviços externos (banco de dados, gateway de pagamento). Dados inválidos são rejeitados na camada de entrada com mensagem estruturada, impedindo que dados corrompidos propaguem para o domínio ou persistência.
