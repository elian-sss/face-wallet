# Documentação do Backend: Aplicação Carteira Digital Segura

## 1. Resumo

Este documento detalha a arquitetura e implementação do servidor backend para o projeto "Carteira Digital Segura". Construído em **Python** com o framework **Django** e **Django REST Framework (DRF)**, o sistema expõe uma API RESTful segura projetada para ser consumida por um cliente frontend (web ou mobile).

O projeto demonstra a aplicação de múltiplos conceitos de segurança da informação, como criptografia de dados em repouso, autenticação multifator, e validação de identidade por biometria facial, servindo como um protótipo robusto para um sistema de armazenamento de dados sensíveis.

## 2. Tecnologias Utilizadas

* **Linguagem:** Python 3.10
* **Framework Principal:** Django & Django REST Framework (DRF)
* **Banco de Dados:** SQLite 3 (para desenvolvimento)
* **Reconhecimento Facial:** `face-recognition` (utilizando `dlib`)
* **Criptografia:** `cryptography` (para criptografia simétrica AES)
* **Comunicação Externa:** `requests` (para integração com a Evolution API)
* **Gerenciamento de Segredos:** `python-decouple` (para variáveis de ambiente)

## 3. Detalhamento Técnico: O Fluxo de Verificação Facial

A autenticação biométrica é um dos pilares de segurança deste projeto. Ela é implementada em um processo de duas etapas (cadastro e verificação) e se baseia no conceito de *embeddings* faciais.

### 3.1. O que é um Embedding Facial?

Um embedding facial não é uma imagem, mas sim uma **representação matemática e vetorial de um rosto**. O modelo de machine learning da biblioteca `face-recognition` analisa uma foto, identifica as características faciais únicas (distância entre os olhos, formato do nariz, etc.) e as converte em um vetor de 128 números de ponto flutuante.

> `[-0.132, 0.052, ..., -0.098]` (um array com 128 dimensões)

Este vetor é como uma "impressão digital" numérica do rosto. A grande vantagem é que não precisamos armazenar as fotos dos usuários após o cadastro, apenas essa representação matemática, o que é mais seguro e privado.

### 3.2. Etapa de Cadastro (Enrollment)

1.  **Recebimento da Imagem:** A API recebe um arquivo de imagem (`face_image`) junto com os outros dados do usuário no endpoint de registro (`POST /api/auth/register/`).
2.  **Pré-processamento:** A imagem é carregada em memória com a biblioteca OpenCV e convertida para o formato de cores RGB, que é o padrão esperado pelo modelo.
3.  **Geração do Embedding:** A função `face_recognition.face_encodings()` processa a imagem e retorna o vetor de 128 dimensões. Se nenhum rosto for detectado, o cadastro falha.
4.  **Armazenamento:** O vetor (embedding) é convertido para uma string no formato JSON e salvo no campo `face_embedding` do modelo `Profile` do usuário no banco de dados.

### 3.3. Etapa de Verificação (Verification)

1.  **Login Prévio:** O usuário primeiro se autentica com suas credenciais (usuário/senha) e recebe um token.
2.  **Envio da Nova Foto:** O usuário envia uma nova foto para o endpoint protegido `POST /api/auth/verify-face/`. A requisição é autenticada com o token obtido no passo anterior.
3.  **Processamento:** O backend executa os mesmos passos de pré-processamento e geração de embedding na nova imagem, criando um `new_embedding`.
4.  **Recuperação:** O `stored_embedding` é recuperado do banco de dados do usuário autenticado.
5.  **A Comparação:** A função `face_recognition.compare_faces([stored_embedding], new_embedding)` é chamada.

    * **Como funciona?** Internamente, a função calcula a **distância Euclidiana** entre os dois vetores de 128 dimensões. A distância é um único número que representa o quão "diferentes" os dois rostos são (distância 0.0 significa rostos idênticos).
    * **Tolerância:** A função compara essa distância com um limiar de tolerância (o padrão é `0.6`). Se a distância calculada for **menor ou igual** à tolerância, a função retorna `True` (os rostos correspondem). Caso contrário, retorna `False`. Ajustamos essa tolerância para `0.5` em nosso código para um reconhecimento um pouco mais estrito.
    * Com base no resultado `True` ou `False`, a API retorna uma resposta de sucesso ou falha.

## 4. Documentação da API (Endpoints)

| Método | Endpoint                                    | Autenticação | Descrição da Funcionalidade                                               |
| :----- | :------------------------------------------ | :----------- | :------------------------------------------------------------------------ |
| `POST` | `/api/auth/register/`                       | Nenhuma      | Realiza o cadastro de um novo usuário com dados, foto facial e telefone.   |
| `POST` | `/api/auth/verify-phone/`                   | Nenhuma      | Ativa a conta do usuário com o código enviado via WhatsApp.               |
| `POST` | `/api/auth/login/`                          | Nenhuma      | Autentica o usuário com `username` e `password` e retorna um token.         |
| `POST` | `/api/auth/verify-face/`                    | **Token** | Segundo fator de autenticação, onde o usuário verifica sua identidade facial.|
| `POST` | `/api/auth/password-reset/request/`         | Nenhuma      | Solicita um código de redefinição de senha, enviado para o WhatsApp.       |
| `POST` | `/api/auth/password-reset/confirm/`         | Nenhuma      | Confirma a redefinição de senha com o código e novos dados.               |
| `GET`  | `/api/cards/`                               | **Token** | Lista todos os cartões de crédito associados ao usuário autenticado.      |
| `POST` | `/api/cards/`                               | **Token** | Adiciona um novo cartão de crédito para o usuário autenticado.            |
| `GET`  | `/api/cards/{id}/`                          | **Token** | Obtém os detalhes de um cartão de crédito específico pelo seu ID.         |
| `PUT`  | `/api/cards/{id}/`                          | **Token** | Atualiza os dados de um cartão de crédito específico.                     |
| `DELETE`| `/api/cards/{id}/`                          | **Token** | Remove um cartão de crédito específico.                                   |

## 5. Configuração do Ambiente de Desenvolvimento

1.  **Clone o repositório** do projeto.
2.  Navegue até a pasta do projeto e crie um ambiente virtual: `python -m venv venv`.
3.  Ative o ambiente virtual: `source venv/Scripts/activate` (no Windows/Git Bash).
4.  **(Apenas para Windows)** Instale o [CMake](https://cmake.org/download/) e as [Build Tools for Visual Studio](https://visualstudio.microsoft.com/pt-br/downloads/) com a carga de trabalho "Desenvolvimento para desktop com C++" para compilar a dependência `dlib`.
5.  Crie um arquivo `requirements.txt` se ainda não existir: `pip freeze > requirements.txt`.
6.  Instale todas as dependências: `pip install -r requirements.txt`.
7.  Crie um arquivo `.env` na raiz do projeto e configure as variáveis de ambiente (`ENCRYPTION_KEY`, `EVOLUTION_API_URL`, etc.).
8.  Aplique as migrações para criar o banco de dados: `python manage.py migrate`.
9.  Inicie o servidor: `python manage.py runserver`.