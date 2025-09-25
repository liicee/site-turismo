from flask import Flask, render_template, redirect, request, flash, get_flashed_messages, session, url_for, jsonify
import sqlite3
import os
import hashlib
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from database import init_database, get_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'turismo_sudeste_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar banco de dados
init_database()

def hash_password(password):
    """Criptografa a senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_logged_in():
    """Verifica se o usuário está logado"""
    return 'user_id' in session

def get_current_user():
    """Retorna dados do usuário atual"""
    if not is_logged_in():
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'nome': user[1],
            'email': user[2],
            'endereco': user[4],
            'telefone': user[5],
            'cpf': user[6],
            'passaporte': user[7],
            'foto_perfil': user[8],
            'is_admin': session.get('is_admin', False)
        }
    return None

@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar pontos turísticos por estado (5 por estado)
    estados = ['RJ', 'SP', 'MG', 'ES']
    pontos_por_estado = {}
    
    for estado in estados:
        cursor.execute('''
            SELECT pt.id, pt.nome, pt.descricao, pt.endereco, pt.latitude, pt.longitude, 
                   pt.imagem, pt.categoria, pt.horario_funcionamento, pt.preco_entrada, 
                   pt.telefone_contato, pt.site_oficial, pt.data_cadastro,
                   COALESCE(ROUND(AVG(a.nota), 1), 0) as media_avaliacoes,
                   COUNT(a.id) as total_avaliacoes
            FROM pontos_turisticos pt
            LEFT JOIN avaliacoes a ON pt.id = a.ponto_turistico_id
            WHERE pt.endereco LIKE ?
            GROUP BY pt.id, pt.nome, pt.descricao, pt.endereco, pt.latitude, pt.longitude, 
                     pt.imagem, pt.categoria, pt.horario_funcionamento, pt.preco_entrada, 
                     pt.telefone_contato, pt.site_oficial, pt.data_cadastro
            ORDER BY media_avaliacoes DESC, total_avaliacoes DESC, pt.nome
            LIMIT 5
        ''', (f'%{estado}%',))
        
        pontos_estado = cursor.fetchall()
        
        # Mapear os dados para facilitar o acesso no template
        pontos_mapeados = []
        for ponto in pontos_estado:
            ponto_dict = {
                'id': ponto[0],
                'nome': ponto[1],
                'descricao': ponto[2],
                'endereco': ponto[3],
                'latitude': ponto[4],
                'longitude': ponto[5],
                'imagem': ponto[6],
                'categoria': ponto[7],
                'horario_funcionamento': ponto[8],
                'preco_entrada': ponto[9],
                'telefone_contato': ponto[10],
                'site_oficial': ponto[11],
                'data_cadastro': ponto[12],
                'media_avaliacoes': ponto[13],
                'total_avaliacoes': ponto[14]
            }
            pontos_mapeados.append(ponto_dict)
        
        pontos_por_estado[estado] = pontos_mapeados
    
    conn.close()
    
    return render_template('dashboard.html', pontos_por_estado=pontos_por_estado, user=get_current_user())

@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    termo_pesquisa = request.form.get('pesquisa', '').strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if termo_pesquisa:
        cursor.execute('''
            SELECT pt.id, pt.nome, pt.descricao, pt.endereco, pt.latitude, pt.longitude, 
                   pt.imagem, pt.categoria, pt.horario_funcionamento, pt.preco_entrada, 
                   pt.telefone_contato, pt.site_oficial, pt.data_cadastro,
                   COALESCE(ROUND(AVG(a.nota), 1), 0) as media_avaliacoes,
                   COUNT(a.id) as total_avaliacoes
            FROM pontos_turisticos pt
            LEFT JOIN avaliacoes a ON pt.id = a.ponto_turistico_id
            WHERE pt.nome LIKE ? OR pt.descricao LIKE ? OR pt.categoria LIKE ?
            GROUP BY pt.id, pt.nome, pt.descricao, pt.endereco, pt.latitude, pt.longitude, 
                     pt.imagem, pt.categoria, pt.horario_funcionamento, pt.preco_entrada, 
                     pt.telefone_contato, pt.site_oficial, pt.data_cadastro
            ORDER BY media_avaliacoes DESC, total_avaliacoes DESC, pt.nome
        ''', (f'%{termo_pesquisa}%', f'%{termo_pesquisa}%', f'%{termo_pesquisa}%'))
    else:
        cursor.execute('''
            SELECT pt.id, pt.nome, pt.descricao, pt.endereco, pt.latitude, pt.longitude, 
                   pt.imagem, pt.categoria, pt.horario_funcionamento, pt.preco_entrada, 
                   pt.telefone_contato, pt.site_oficial, pt.data_cadastro,
                   COALESCE(ROUND(AVG(a.nota), 1), 0) as media_avaliacoes,
                   COUNT(a.id) as total_avaliacoes
            FROM pontos_turisticos pt
            LEFT JOIN avaliacoes a ON pt.id = a.ponto_turistico_id
            GROUP BY pt.id, pt.nome, pt.descricao, pt.endereco, pt.latitude, pt.longitude, 
                     pt.imagem, pt.categoria, pt.horario_funcionamento, pt.preco_entrada, 
                     pt.telefone_contato, pt.site_oficial, pt.data_cadastro
            ORDER BY media_avaliacoes DESC, total_avaliacoes DESC, pt.nome
        ''')
    
    pontos_turisticos = cursor.fetchall()
    
    # Mapear os dados para facilitar o acesso no template
    pontos_mapeados = []
    for ponto in pontos_turisticos:
        ponto_dict = {
            'id': ponto[0],
            'nome': ponto[1],
            'descricao': ponto[2],
            'endereco': ponto[3],
            'latitude': ponto[4],
            'longitude': ponto[5],
            'imagem': ponto[6],
            'categoria': ponto[7],
            'horario_funcionamento': ponto[8],
            'preco_entrada': ponto[9],
            'telefone_contato': ponto[10],
            'site_oficial': ponto[11],
            'data_cadastro': ponto[12],
            'media_avaliacoes': ponto[13],
            'total_avaliacoes': ponto[14]
        }
        pontos_mapeados.append(ponto_dict)
    
    conn.close()
    
    return render_template('dashboard.html', pontos_turisticos=pontos_mapeados, user=get_current_user(), termo_pesquisa=termo_pesquisa)

@app.route('/avaliar', methods=['POST'])
def avaliar():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    ponto_id = request.form.get('ponto_id')
    nota = int(request.form.get('nota'))
    comentario = request.form.get('comentario', '').strip()
    
    if not ponto_id or not (1 <= nota <= 5):
        flash("Dados de avaliação inválidos!")
        return redirect(url_for('dashboard'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se o usuário já avaliou este ponto
    cursor.execute('SELECT id FROM avaliacoes WHERE usuario_id = ? AND ponto_turistico_id = ?', 
                   (session['user_id'], ponto_id))
    
    if cursor.fetchone():
        # Atualizar avaliação existente
        cursor.execute('''
            UPDATE avaliacoes 
            SET nota = ?, comentario = ?, data_avaliacao = CURRENT_TIMESTAMP
            WHERE usuario_id = ? AND ponto_turistico_id = ?
        ''', (nota, comentario, session['user_id'], ponto_id))
    else:
        # Inserir nova avaliação
        cursor.execute('''
            INSERT INTO avaliacoes (usuario_id, ponto_turistico_id, nota, comentario)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], ponto_id, nota, comentario))
    
    conn.commit()
    conn.close()
    
    flash("Avaliação salva com sucesso!")
    return redirect(url_for('dashboard'))

@app.route('/minhas_avaliacoes')
def minhas_avaliacoes():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, pt.nome as ponto_nome
        FROM avaliacoes a
        JOIN pontos_turisticos pt ON a.ponto_turistico_id = pt.id
        WHERE a.usuario_id = ?
        ORDER BY a.data_avaliacao DESC
    ''', (session['user_id'],))
    
    avaliacoes = cursor.fetchall()
    conn.close()
    
    return render_template('minhas_avaliacoes.html', avaliacoes=avaliacoes, user=get_current_user())

@app.route('/remover_avaliacao', methods=['POST'])
def remover_avaliacao():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    avaliacao_id = request.form.get('avaliacao_id')
    
    if not avaliacao_id:
        flash("ID da avaliação não fornecido!")
        return redirect(url_for('minhas_avaliacoes'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se a avaliação pertence ao usuário atual
    cursor.execute('SELECT id FROM avaliacoes WHERE id = ? AND usuario_id = ?', 
                   (avaliacao_id, session['user_id']))
    
    if not cursor.fetchone():
        flash("Avaliação não encontrada ou você não tem permissão para removê-la!")
        conn.close()
        return redirect(url_for('minhas_avaliacoes'))
    
    # Remover a avaliação
    cursor.execute('DELETE FROM avaliacoes WHERE id = ?', (avaliacao_id,))
    conn.commit()
    conn.close()
    
    flash("Avaliação removida com sucesso!")
    return redirect(url_for('minhas_avaliacoes'))

@app.route('/ponto/<int:ponto_id>')
def ponto_detalhes(ponto_id):
    if not is_logged_in():
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pontos_turisticos WHERE id = ?', (ponto_id,))
    ponto = cursor.fetchone()
    conn.close()
    
    if not ponto:
        flash("Ponto turístico não encontrado!")
        return redirect(url_for('dashboard'))
    
    ponto_data = {
        'id': ponto[0],
        'nome': ponto[1],
        'descricao': ponto[2],
        'endereco': ponto[3],
        'latitude': ponto[4],
        'longitude': ponto[5],
        'imagem': ponto[6],
        'categoria': ponto[7],
        'horario_funcionamento': ponto[8],
        'preco_entrada': ponto[9],
        'telefone_contato': ponto[10],
        'site_oficial': ponto[11]
    }
    
    return render_template('ponto_detalhes.html', ponto=ponto_data, user=get_current_user())

@app.route('/perfil')
def perfil():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    return render_template('perfil.html', user=get_current_user())

@app.route('/atualizar_perfil', methods=['POST'])
def atualizar_perfil():
    if not is_logged_in():
        return redirect(url_for('home'))
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')
    cpf = request.form.get('cpf')
    passaporte = request.form.get('passaporte')
    
    # Upload da foto de perfil
    foto_perfil = None
    if 'foto_perfil' in request.files:
        file = request.files['foto_perfil']
        if file and file.filename:
            filename = secure_filename(file.filename)
            if filename:
                foto_perfil = f"uploads/{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se email já existe em outro usuário
    cursor.execute('SELECT id FROM usuarios WHERE email = ? AND id != ?', (email, session['user_id']))
    if cursor.fetchone():
        flash("Este email já está sendo usado por outro usuário!")
        conn.close()
        return redirect(url_for('perfil'))
    
    # Verificar se CPF já existe em outro usuário
    if cpf:
        cursor.execute('SELECT id FROM usuarios WHERE cpf = ? AND id != ?', (cpf, session['user_id']))
        if cursor.fetchone():
            flash("Este CPF já está sendo usado por outro usuário!")
            conn.close()
            return redirect(url_for('perfil'))
    
    # Atualizar dados
    update_fields = []
    values = []
    
    if nome:
        update_fields.append('nome = ?')
        values.append(nome)
    
    if email:
        update_fields.append('email = ?')
        values.append(email)
    
    if endereco:
        update_fields.append('endereco = ?')
        values.append(endereco)
    
    if telefone:
        update_fields.append('telefone = ?')
        values.append(telefone)
    
    if cpf:
        update_fields.append('cpf = ?')
        values.append(cpf)
    
    if passaporte:
        update_fields.append('passaporte = ?')
        values.append(passaporte)
    
    if foto_perfil:
        update_fields.append('foto_perfil = ?')
        values.append(foto_perfil)
    
    if update_fields:
        values.append(session['user_id'])
        query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        flash("Perfil atualizado com sucesso!")
    else:
        flash("Nenhuma alteração foi feita.")
    
    conn.close()
    return redirect(url_for('perfil'))

@app.route('/login', methods=['POST'])
def login():
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    if not nome or not senha:
        flash("Nome e senha são obrigatórios!")
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se é administrador
    if nome == 'adm' and senha == '000':
        cursor.execute('SELECT id FROM usuarios WHERE nome = ?', ('adm',))
        admin = cursor.fetchone()
        if admin:
            session['user_id'] = admin[0]
            session['is_admin'] = True
            conn.close()
            return redirect(url_for('adm'))
    
    # Verificar usuário normal
    cursor.execute('SELECT id, senha FROM usuarios WHERE nome = ?', (nome,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[1] == hash_password(senha):
        session['user_id'] = user[0]
        session['is_admin'] = False
        return redirect(url_for('dashboard'))
    else:
        flash("Usuário ou senha inválidos!")
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/recriar_pontos_sudeste')
def recriar_pontos_sudeste():
    """Rota para recriar pontos turísticos do Sudeste (apenas para desenvolvimento)"""
    if not is_logged_in() or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Limpar pontos turísticos existentes
    cursor.execute('DELETE FROM pontos_turisticos')
    
    # Inserir pontos turísticos do Sudeste
    pontos_sudeste = [
        # Rio de Janeiro
        ('Cristo Redentor', 'Monumento religioso mais famoso do Brasil', 'Parque Nacional da Tijuca, Rio de Janeiro - RJ', -22.9519, -43.2105, 'cristo-redentor.jpg', 'Monumento', 'Diariamente das 8h às 19h', 'R$ 65,00', '(21) 2558-1329', 'https://www.cristoredentoroficial.com.br', '2024-01-01'),
        
        # São Paulo
        ('MASP - Museu de Arte de São Paulo', 'Museu de arte mais importante do Brasil', 'Av. Paulista, 1578 - Bela Vista, São Paulo - SP', -23.5614, -46.6565, 'masp.jpg', 'Museu', 'Terça a domingo das 10h às 18h', 'R$ 50,00', '(11) 3149-5959', 'https://masp.org.br', '2024-01-01'),
        
        # Minas Gerais
        ('Inhotim', 'Museu de arte contemporânea e jardim botânico', 'Rua B, 20 - Inhotim, Brumadinho - MG', -20.1204, -44.2200, 'inhotim.jpg', 'Museu', 'Terça a domingo das 9h30 às 17h30', 'R$ 44,00', '(31) 3571-9700', 'https://www.inhotim.org.br', '2024-01-01'),
        
        # Espírito Santo
        ('Convento da Penha', 'Santuário católico com vista panorâmica', 'Rua Vasco Coutinho, s/n - Penha, Vila Velha - ES', -20.3156, -40.3128, 'convento-penha.jpg', 'Religioso', 'Diariamente das 5h às 18h', 'Gratuito', '(27) 3329-7220', 'https://www.conventodapenha.org.br', '2024-01-01'),
        
        # Rio de Janeiro (segundo ponto)
        ('Pão de Açúcar', 'Morro com bondinho e vista panorâmica', 'Av. Pasteur, 520 - Urca, Rio de Janeiro - RJ', -22.9494, -43.1551, 'pao-acucar.jpg', 'Paisagem', 'Diariamente das 8h às 21h', 'R$ 120,00', '(21) 2546-8400', 'https://www.bondinho.com.br', '2024-01-01')
    ]
    
    cursor.executemany('''
        INSERT INTO pontos_turisticos (nome, descricao, endereco, latitude, longitude, imagem, categoria, horario_funcionamento, preco_entrada, telefone_contato, site_oficial, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', pontos_sudeste)
    
    conn.commit()
    conn.close()
    
    flash("Pontos turísticos do Sudeste recriados com sucesso!")
    return redirect(url_for('dashboard'))


@app.route('/admin/adicionar_ponto', methods=['GET', 'POST'])
def adicionar_ponto():
    """Rota para admin adicionar novo ponto turístico"""
    if not is_logged_in() or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        endereco = request.form.get('endereco')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        categoria = request.form.get('categoria')
        horario_funcionamento = request.form.get('horario_funcionamento')
        preco_entrada = request.form.get('preco_entrada')
        telefone_contato = request.form.get('telefone_contato')
        site_oficial = request.form.get('site_oficial')
        
        # Verificar se todos os campos obrigatórios foram preenchidos
        if not all([nome, descricao, endereco, latitude, longitude, categoria]):
            flash("Todos os campos obrigatórios devem ser preenchidos!")
            return redirect(url_for('adicionar_ponto'))
        
        # Processar upload da imagem
        if 'imagem' in request.files:
            arquivo = request.files['imagem']
            if arquivo and arquivo.filename:
                filename = secure_filename(arquivo.filename)
                # Adicionar timestamp para evitar conflitos
                timestamp = str(int(time.time()))
                filename = f"{timestamp}_{filename}"
                arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagem = filename
            else:
                imagem = 'default.jpg'
        else:
            imagem = 'default.jpg'
        
        # Inserir no banco de dados
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pontos_turisticos (nome, descricao, endereco, latitude, longitude, imagem, categoria, horario_funcionamento, preco_entrada, telefone_contato, site_oficial, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, descricao, endereco, float(latitude), float(longitude), imagem, categoria, horario_funcionamento, preco_entrada, telefone_contato, site_oficial, datetime.now().strftime('%Y-%m-%d')))
            
            conn.commit()
            conn.close()
            
            flash("Ponto turístico adicionado com sucesso!")
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            conn.close()
            flash(f"Erro ao adicionar ponto turístico: {str(e)}")
            return redirect(url_for('adicionar_ponto'))
    
    return render_template('adicionar_ponto.html')


@app.route('/admin/editar_ponto/<int:ponto_id>', methods=['GET', 'POST'])
def editar_ponto(ponto_id):
    """Rota para admin editar ponto turístico existente"""
    if not is_logged_in() or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        endereco = request.form.get('endereco')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        categoria = request.form.get('categoria')
        horario_funcionamento = request.form.get('horario_funcionamento')
        preco_entrada = request.form.get('preco_entrada')
        telefone_contato = request.form.get('telefone_contato')
        site_oficial = request.form.get('site_oficial')
        
        # Verificar se todos os campos obrigatórios foram preenchidos
        if not all([nome, descricao, endereco, latitude, longitude, categoria]):
            flash("Todos os campos obrigatórios devem ser preenchidos!")
            return redirect(url_for('editar_ponto', ponto_id=ponto_id))
        
        # Processar upload da nova imagem (se fornecida)
        imagem_atual = None
        cursor.execute('SELECT imagem FROM pontos_turisticos WHERE id = ?', (ponto_id,))
        resultado = cursor.fetchone()
        if resultado:
            imagem_atual = resultado[0]
        
        nova_imagem = imagem_atual  # Manter imagem atual por padrão
        
        if 'imagem' in request.files:
            arquivo = request.files['imagem']
            if arquivo and arquivo.filename:
                filename = secure_filename(arquivo.filename)
                # Adicionar timestamp para evitar conflitos
                timestamp = str(int(time.time()))
                filename = f"{timestamp}_{filename}"
                arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                nova_imagem = filename
        
        # Atualizar no banco de dados
        try:
            cursor.execute('''
                UPDATE pontos_turisticos 
                SET nome = ?, descricao = ?, endereco = ?, latitude = ?, longitude = ?, 
                    imagem = ?, categoria = ?, horario_funcionamento = ?, preco_entrada = ?, 
                    telefone_contato = ?, site_oficial = ?
                WHERE id = ?
            ''', (nome, descricao, endereco, float(latitude), float(longitude), nova_imagem, 
                  categoria, horario_funcionamento, preco_entrada, telefone_contato, site_oficial, ponto_id))
            
            conn.commit()
            conn.close()
            
            flash("Ponto turístico atualizado com sucesso!")
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            conn.close()
            flash(f"Erro ao atualizar ponto turístico: {str(e)}")
            return redirect(url_for('editar_ponto', ponto_id=ponto_id))
    
    # Buscar dados do ponto turístico para edição
    cursor.execute('SELECT * FROM pontos_turisticos WHERE id = ?', (ponto_id,))
    ponto = cursor.fetchone()
    conn.close()
    
    if not ponto:
        flash("Ponto turístico não encontrado!")
        return redirect(url_for('dashboard'))
    
    # Mapear dados do ponto para o template
    ponto_data = {
        'id': ponto[0],
        'nome': ponto[1],
        'descricao': ponto[2],
        'endereco': ponto[3],
        'latitude': ponto[4],
        'longitude': ponto[5],
        'imagem': ponto[6],
        'categoria': ponto[7],
        'horario_funcionamento': ponto[8],
        'preco_entrada': ponto[9],
        'telefone_contato': ponto[10],
        'site_oficial': ponto[11]
    }
    
    return render_template('editar_ponto.html', ponto=ponto_data)


@app.route('/admin/excluir_ponto/<int:ponto_id>', methods=['POST'])
def excluir_ponto(ponto_id):
    """Rota para admin excluir ponto turístico"""
    if not is_logged_in() or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar dados do ponto antes de excluir
        cursor.execute('SELECT nome, imagem FROM pontos_turisticos WHERE id = ?', (ponto_id,))
        ponto = cursor.fetchone()
        
        if not ponto:
            flash("Ponto turístico não encontrado!")
            return redirect(url_for('dashboard'))
        
        # Excluir avaliações relacionadas primeiro (devido à foreign key)
        cursor.execute('DELETE FROM avaliacoes WHERE ponto_turistico_id = ?', (ponto_id,))
        
        # Excluir o ponto turístico
        cursor.execute('DELETE FROM pontos_turisticos WHERE id = ?', (ponto_id,))
        
        conn.commit()
        conn.close()
        
        # Tentar excluir a imagem do sistema de arquivos (opcional)
        if ponto[1] and ponto[1] != 'default.jpg':
            try:
                import os
                imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], ponto[1])
                if os.path.exists(imagem_path):
                    os.remove(imagem_path)
            except:
                pass  # Ignorar erros de exclusão de arquivo
        
        flash(f"Ponto turístico '{ponto[0]}' excluído com sucesso!")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        conn.close()
        flash(f"Erro ao excluir ponto turístico: {str(e)}")
        return redirect(url_for('editar_ponto', ponto_id=ponto_id))



@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if not all([nome, email, senha, confirmar_senha]):
        flash("Todos os campos são obrigatórios!")
        return redirect(url_for('home'))
    
    if senha != confirmar_senha:
        flash("As senhas não coincidem!")
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se usuário já existe
    cursor.execute('SELECT id FROM usuarios WHERE nome = ? OR email = ?', (nome, email))
    if cursor.fetchone():
        flash("Nome de usuário ou email já cadastrado!")
        conn.close()
        return redirect(url_for('home'))
    
    # Cadastrar novo usuário
    cursor.execute('''
        INSERT INTO usuarios (nome, email, senha) 
        VALUES (?, ?, ?)
    ''', (nome, email, hash_password(senha)))
    
    conn.commit()
    conn.close()
    
    flash("Usuário cadastrado com sucesso! Faça login para continuar.")
    return redirect(url_for('home'))

@app.route('/adm')
def adm():
    if not is_logged_in() or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios ORDER BY data_cadastro DESC')
    usuarios = cursor.fetchall()
    conn.close()
    
    return render_template('adm.html', usuarios=usuarios)

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    if not is_logged_in() or not session.get('is_admin'):
        return redirect(url_for('home'))
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    if not all([nome, email, senha]):
        flash("Todos os campos são obrigatórios!")
        return redirect(url_for('adm'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se usuário já existe
    cursor.execute('SELECT id FROM usuarios WHERE nome = ? OR email = ?', (nome, email))
    if cursor.fetchone():
        flash("Nome de usuário ou email já cadastrado!")
        conn.close()
        return redirect(url_for('adm'))
    
    # Cadastrar novo usuário
    cursor.execute('''
        INSERT INTO usuarios (nome, email, senha) 
        VALUES (?, ?, ?)
    ''', (nome, email, hash_password(senha)))
    
    conn.commit()
    conn.close()
    
    flash("Usuário cadastrado com sucesso!")
    return redirect(url_for('adm'))

if __name__ == '__main__':
    app.run(debug=True)
