from flask import Flask , render_template , redirect, request, flash, get_flashed_messages
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = 'algumacoisa'

logado = False

@app.route('/')
def home():
    global logado
    logado = False
    return render_template("index.html")

@app.route('/adm')
def adm():
    if logado:
        with open('usuarios.json') as usuariosTemp:
            usuarios = json.load(usuariosTemp)

        return render_template('adm.html', usuarios=usuarios)
    else:
        return redirect('/')


@app.route ('/login' , methods =['POST'])
def login():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
        cont = 0
        for usuario in usuarios:
            cont += 1

            if nome == 'adm' and senha == '000':
                logado = True
                return redirect ('/adm')

            if usuario["nome"] == nome and usuario["senha"] == senha:
                return render_template("usuarios.html")

            if cont >= len(usuarios):
                flash("USUARIO INVALIDO")
                return redirect('/')
            

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    novo_usuario = {
        "nome": nome,
        "senha": senha
    }

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
       


    # Verifica se o usuário já existe
    for usuario in usuarios:
        if usuario["nome"] == nome:
            flash("Este Usuario ja esta cadastrado")
            return redirect('/adm')

    usuarios.insert(0, novo_usuario)

    with open('usuarios.json', 'w') as gravarTemp:
        json.dump(usuarios, gravarTemp, indent=4)
    
    flash("Usuario cadastrado com sucesso")
    return redirect('/adm')

if __name__ in '__main__':
    app.run(debug= True)
