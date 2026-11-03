# CineLista — Catálogo de Filmes | UC32

Projeto completo de estudo com Python, Flask, SQLite e templates Jinja2.
Cadastro, listagem, edição e exclusão com confirmação; notas de 1 a 10 (aceita decimais), validação no servidor, layout responsivo em tons roxos.

## Executar no Linux / Chromebook

Extraia o ZIP e abra o terminal dentro da pasta `catalogo-filmes` (onde está app.py):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 no navegador. Para parar: Ctrl+C.
Se `venv` não estiver disponível no Linux Debian/Chromebook, instale `python3-venv` pelo gerenciador de pacotes do sistema.

## Windows

Dentro da pasta extraída, use o terminal:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Não é necessário ativar o ambiente virtual com PowerShell.

## Banco automático

`filmes.db` é criado ao iniciar/importar app.py, inclusive com Gunicorn. O ZIP não inclui um banco preenchido: cadastre seus próprios filmes.
A conexão é fechada ao terminar a requisição. INSERT, UPDATE e DELETE usam commit; os parâmetros SQL usam `?`.
O ano aceito vai de 1888 a 2100 e a nota de 1 a 10.

## Rotas e CRUD

| Rota | Método | Operação |
| --- | --- | --- |
| `/` | GET | Listar (SELECT) |
| `/cadastrar` | GET / POST | Formulário / cadastrar (INSERT) |
| `/editar/<id>` | GET / POST | Formulário / editar (UPDATE) |
| `/excluir/<id>` | GET / POST | Confirmar / excluir (DELETE) |

O código app.py contém comentários para facilitar a apresentação.
As ações POST verificam um token contra envios de formulários de outros sites. O sistema é um catálogo compartilhado, sem login: qualquer visitante pode modificar os registros.

## Enviar ao GitHub

1. Crie um repositório chamado `catalogo-filmes` no GitHub.
2. Em **Add file → Upload files**, envie os arquivos extraídos e as pastas templates e static. Não envie apenas o ZIP.
3. Deixe app.py, requirements.txt e Procfile diretamente na raiz do repositório.
4. Não envie .venv, __pycache__, arquivos .db ou segredos.
5. Confirme o envio (Commit changes) e copie o link do repositório.

## Publicar no Render

1. Entre em https://render.com e escolha **New → Web Service**.
2. Conecte o repositório do GitHub.
3. Escolha Python 3 como linguagem/runtime.
4. Se app.py estiver na raiz, deixe Root Directory vazio. Se enviou a pasta inteira, configure Root Directory como `catalogo-filmes`.
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app`
7. Em Environment, crie `SECRET_KEY` com uma chave aleatória. Gere uma localmente com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Não publique essa chave no GitHub. Localmente, sem essa variável, a aplicação gera uma chave temporária; reiniciar encerra as sessões anteriores.

8. Escolha o plano adequado e clique em Deploy Web Service.
9. Quando o deploy terminar, abra a URL fornecida pelo Render e teste cadastrar, editar e excluir.
10. Entregue o link do site e o link do repositório.

**SQLite no Render:** sem disco persistente, os dados locais são perdidos em reinícios e novos deploys. No serviço gratuito, também podem desaparecer quando ele entra em suspensão. O banco é recriado automaticamente, vazio. Isso atende ao cenário didático do enunciado.

Referências oficiais:
- https://render.com/docs/deploy-flask
- https://render.com/docs/free

## Conferência antes da entrega

- [ ] Executar na sua máquina.
- [ ] Cadastrar um filme e verificar a listagem.
- [ ] Editar título, gênero, ano e nota.
- [ ] Excluir e confirmar que o filme desapareceu.
- [ ] Publicar no GitHub e no Render.
- [ ] Abrir o link público e repetir o CRUD.

O ZIP contém o código pronto. A publicação depende da criação do repositório e do serviço nas suas contas.
