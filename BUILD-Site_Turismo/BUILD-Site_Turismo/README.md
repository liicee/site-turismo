# Sistema de Turismo - Sudeste do Brasil

Um sistema completo de turismo focado nos pontos turísticos do Rio de Janeiro, desenvolvido em Flask com banco de dados SQLite3.

## 🚀 Funcionalidades

### Para Usuários
- **Login e Cadastro**: Sistema completo de autenticação
- **Dashboard**: Visualização dos pontos turísticos do Rio de Janeiro
- **Detalhes dos Pontos**: Informações completas com integração do Google Maps
- **Gerenciamento de Perfil**: 
  - Upload de foto de perfil
  - Edição de informações pessoais (Nome, Email, Endereço, Telefone, CPF, Passaporte)
  - Logout seguro

### Para Administradores
- **Painel Administrativo**: Gerenciamento de usuários
- **Cadastro de Usuários**: Criação de novas contas
- **Visualização de Dados**: Lista completa de usuários cadastrados

### Pontos Turísticos Incluídos
- Cristo Redentor
- Pão de Açúcar
- Praia de Copacabana
- Jardim Botânico
- Lapa

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapas**: Google Maps API
- **Ícones**: Font Awesome

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)

## 🔧 Instalação

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd site-turismo-main
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o sistema**:
   ```bash
   python main.py
   ```

4. **Acesse no navegador**:
   ```
   http://localhost:5000
   ```

## 🔑 Credenciais de Acesso

### Administrador
- **Usuário**: adm
- **Senha**: 000

### Usuário Normal
- Cadastre-se através do formulário na página inicial

## 📁 Estrutura do Projeto

```
site-turismo-main/
├── main.py                 # Aplicação principal Flask
├── database.py            # Configuração do banco de dados
├── requirements.txt       # Dependências do projeto
├── README.md             # Documentação
├── turismo.db            # Banco de dados SQLite (criado automaticamente)
├── static/
│   ├── css/
│   │   ├── home.css      # Estilos da página inicial
│   │   ├── dashboard.css # Estilos do dashboard
│   │   ├── ponto_detalhes.css # Estilos da página de detalhes
│   │   ├── perfil.css    # Estilos da página de perfil
│   │   ├── adm.css       # Estilos do painel administrativo
│   │   └── imagens/      # Imagens dos pontos turísticos
│   └── uploads/          # Pasta para uploads de fotos de perfil
└── templates/
    ├── index.html        # Página de login/cadastro
    ├── dashboard.html    # Página principal com pontos turísticos
    ├── ponto_detalhes.html # Página de detalhes do ponto turístico
    ├── perfil.html       # Página de gerenciamento de perfil
    └── adm.html          # Painel administrativo
```

## 🗺️ Google Maps API

Para usar a funcionalidade de mapas, você precisa:

1. Obter uma chave da API do Google Maps
2. Substituir `YOUR_API_KEY` no arquivo `templates/ponto_detalhes.html` pela sua chave

## 🎨 Características do Design

- **Design Responsivo**: Funciona em desktop, tablet e mobile
- **Interface Moderna**: Gradientes, sombras e animações
- **UX Intuitiva**: Navegação clara e fácil de usar
- **Tema Consistente**: Cores e estilos padronizados

## 🔒 Segurança

- Senhas criptografadas com SHA-256
- Validação de dados de entrada
- Proteção contra SQL Injection
- Sessões seguras

## 📱 Responsividade

O sistema é totalmente responsivo e funciona perfeitamente em:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (até 767px)

## 🚀 Funcionalidades Futuras

- Sistema de avaliações dos pontos turísticos
- Favoritos do usuário
- Sistema de comentários
- Integração com redes sociais
- Notificações push

## 📞 Suporte

Para dúvidas ou problemas, entre em contato através dos canais oficiais do projeto.

---

**Desenvolvido com ❤️ para promover o turismo no Sudeste do Brasil**
