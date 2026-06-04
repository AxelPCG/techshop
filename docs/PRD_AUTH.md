### Product Requirements Document: Autenticação e Perfis de Usuário

#### 1. Objetivo
Implementar um sistema de autenticação seguro que permita aos usuários criar contas, fazer login/logout e gerenciar um perfil básico. Isso é fundamental para personalizar a experiência de compra e permitir o rastreamento de pedidos.

#### 2. Requisitos Funcionais
*   **US8:** Como um novo usuário, quero poder me cadastrar na plataforma usando e-mail and senha para ter uma conta pessoal.
*   **US9:** Como um usuário cadastrado, quero poder fazer login no sistema para acessar minha conta e histórico.
*   **US10:** Como um usuário logado, quero poder fazer logout para proteger minha conta em dispositivos compartilhados.
*   **US11:** Como um usuário logado, quero ter uma página de perfil onde posso ver e editar minhas informações básicas (como nome e endereço de entrega).

#### 3. Requisitos Não-Funcionais
*   **Segurança:** Senhas devem ser armazenadas de forma segura (hashed). O sistema deve ter proteção contra ataques comuns (ex: brute-force).
*   **Usabilidade:** O processo de login e cadastro deve ser simples e intuitivo.
