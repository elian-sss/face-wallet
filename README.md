# Carteira Digital Segura com Biometria Facial

Este projeto é uma aplicação de carteira digital desenvolvida em Python com o framework Django. O objetivo principal é fornecer um ambiente seguro para o armazenamento de dados de cartões de crédito, utilizando criptografia forte e múltiplos fatores de autenticação, incluindo biometria facial.

## ✨ Funcionalidades Implementadas

* **✅ Cadastro e Login de Usuários:** Sistema completo de criação e autenticação de contas de usuário.
* **✅ Criptografia AES de Dados de Cartões:** Todos os dados sensíveis dos cartões (número, data de validade, CVV) são criptografados com o algoritmo Fernet (AES-128-CBC) antes de serem salvos no banco de dados.
* **✅ Autenticação Biométrica Facial:**
    * **Cadastro:** No momento do registro, o usuário deve enviar uma foto de seu rosto. O sistema extrai uma "assinatura" facial (embedding) e a armazena de forma segura.
    * **Verificação:** Após o login com senha, um endpoint dedicado permite que o usuário envie uma nova foto para verificar sua identidade, comparando-a com a assinatura armazenada.
* **✅ Gerenciamento de Cartões (CRUD):** Endpoints seguros para criar, listar, atualizar e deletar os cartões de um usuário. Um usuário só pode acessar seus próprios cartões.
* **✅ API RESTful Segura:** A interação com o sistema é feita através de uma API RESTful construída com Django REST Framework, com endpoints protegidos por autenticação baseada em token.
* **✅ Gerenciamento de Segredos:** A chave de criptografia é gerenciada de forma segura através de um arquivo `.env`, que não é enviado para o controle de versão.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.10, Django, Django REST Framework
* **Banco de Dados:** SQLite 3 (padrão do Django para desenvolvimento)
* **Reconhecimento Facial:** `face-recognition` (com `dlib`)
* **Criptografia:** `cryptography`
* **Gerenciamento de Ambiente:** `venv`
* **Gerenciamento de Segredos:** `python-decouple`