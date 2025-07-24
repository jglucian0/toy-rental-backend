# Toy Rental ERP – Backend

**Toy Rental ERP** é um sistema completo de gestão desenvolvido para empresas de locação de brinquedos infláveis e serviços para festas infantis. Este repositório contém o backend da aplicação, desenvolvido com **Django**, responsável por toda a lógica de negócio, persistência de dados e funcionalidades administrativas.

## 🚀 Tecnologias Utilizadas

- **Python 3.12+**
- **Django 5+**
- **SQLite (ambiente de desenvolvimento)**
- **Bootstrap (via templates do Django Admin)**
- **Django Admin personalizado**
- **Possível integração com Django REST Framework e serviços externos (WhatsApp, e-mail, etc.)**

---

## 🔧 Funcionalidades

O sistema oferece recursos robustos e automatizados para facilitar a gestão do negócio:

### 💰 Controle Financeiro
Gerencie entradas, saídas e relatórios financeiros de forma intuitiva e automatizada.

### 📦 Gestão de Estoque
Controle completo dos brinquedos infláveis, com status de disponibilidade, manutenção e histórico de uso.

### 📆 Agendamento de Festas
Organize todos os eventos com praticidade. O sistema envia confirmações automáticas e evita conflitos de horário.

### 👥 Gestão de Clientes
Mantenha o cadastro completo de clientes e responsáveis, com dados organizados para facilitar o atendimento.

### 📊 Relatórios Detalhados
Geração de relatórios personalizados para análise de desempenho financeiro, histórico de locações e visão geral do negócio.

### 🗺️ Cronograma de Montagem
Tenha um roteiro claro e organizado com todas as festas agendadas para o dia, facilitando a logística da equipe.

---

## 📁 Estrutura do Projeto

```bash
toy_rental_erp/
├── core/              # Aplicações principais do sistema (clientes, locações, brinquedos, etc.)
├── templates/         # Templates HTML (Django Admin ou interface pública, se houver)
├── static/            # Arquivos estáticos (CSS, JS, imagens, logo, etc.)
├── media/             # Uploads (contratos, imagens dos brinquedos, etc.)
├── db.sqlite3         # Banco de dados local (dev)
├── manage.py
└── README.md
