#!/usr/bin/env python3
"""
Script de teste para Instagram Login e Scraping
Execute este script para testar a funcionalidade do Instagram
"""

import sys
sys.path.insert(0, '/home/patreze/dev/sorteio/backend')

from instagram_service import instagram_service

def test_login():
    """Testa o login no Instagram"""
    print("=" * 60)
    print("🔐 TESTANDO LOGIN NO INSTAGRAM")
    print("=" * 60)
    
    username = "casadosomsobral"
    password = "eitaeitaeita"
    
    print(f"\n📝 Tentando login com usuário: {username}")
    
    try:
        success = instagram_service.login(username, password)
        if success:
            print("✅ LOGIN REALIZADO COM SUCESSO!")
            print(f"   Status: {instagram_service.logged_in}")
            return True
        else:
            print("❌ FALHA NO LOGIN")
            return False
    except Exception as e:
        print(f"❌ ERRO NO LOGIN: {str(e)}")
        return False


def test_scrape():
    """Testa o scraping de um post"""
    print("\n" + "=" * 60)
    print("🔍 TESTANDO SCRAPING DE POST")
    print("=" * 60)
    
    post_url = "https://www.instagram.com/p/DSAYQxiDfwR/"
    
    print(f"\n📝 URL do post: {post_url}")
    
    try:
        print("\n⏳ Coletando comentários...")
        post_data = instagram_service.scrape_post_comments(post_url)
        
        print("\n✅ SCRAPING CONCLUÍDO!")
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Shortcode: {post_data['shortcode']}")
        print(f"   Dono: @{post_data['owner_username']}")
        print(f"   Curtidas: {post_data['likes']}")
        print(f"   Total de comentários: {post_data['comments_count']}")
        print(f"   Participantes coletados: {len(post_data['participants'])}")
        
        print(f"\n👥 PRIMEIROS 5 PARTICIPANTES:")
        for i, participant in enumerate(post_data['participants'][:5], 1):
            print(f"\n   {i}. @{participant['username']}")
            print(f"      Comentário: {participant['text'][:60]}...")
            print(f"      Marcou: {', '.join(['@' + u for u in participant['tagged_users']])}")
        
        return post_data
        
    except Exception as e:
        print(f"\n❌ ERRO NO SCRAPING: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_validation():
    """Testa a validação de um participante"""
    print("\n" + "=" * 60)
    print("✓ TESTANDO VALIDAÇÃO DE PARTICIPANTE")
    print("=" * 60)
    
    # Exemplo de validação
    username = "exemplo_usuario"
    tagged_users = ["amigo1", "amigo2"]
    required_follows = ["soundhouse_producoes", "_ribeiramusic", "goticosnatal"]
    shortcode = "DSAYQxiDfwR"
    
    print(f"\n📝 Validando usuário: @{username}")
    print(f"   Marcou: {', '.join(['@' + u for u in tagged_users])}")
    print(f"   Deve seguir: {', '.join(['@' + a for a in required_follows])}")
    
    try:
        is_valid, errors = instagram_service.validate_participant(
            username=username,
            tagged_users=tagged_users,
            required_follows=required_follows,
            shortcode=shortcode,
            require_public=True,
            require_mutual=False
        )
        
        if is_valid:
            print("\n✅ PARTICIPANTE VÁLIDO!")
        else:
            print("\n❌ PARTICIPANTE INVÁLIDO")
            print("\n   Erros encontrados:")
            for error in errors:
                print(f"   - {error}")
        
        return is_valid, errors
        
    except Exception as e:
        print(f"\n❌ ERRO NA VALIDAÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, [str(e)]


def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print("🎯 TESTE COMPLETO DO SISTEMA INSTAGRAM")
    print("=" * 60)
    
    # Teste 1: Login
    login_success = test_login()
    
    if not login_success:
        print("\n⚠️  Login falhou, mas vamos tentar scraping sem login...")
    
    # Teste 2: Scraping
    post_data = test_scrape()
    
    if post_data and len(post_data['participants']) > 0:
        # Teste 3: Validação (apenas se tiver participantes)
        print("\n⏳ Aguarde, vamos validar o primeiro participante...")
        first_participant = post_data['participants'][0]
        
        is_valid, errors = instagram_service.validate_participant(
            username=first_participant['username'],
            tagged_users=first_participant['tagged_users'],
            required_follows=["soundhouse_producoes", "_ribeiramusic", "goticosnatal"],
            shortcode=post_data['shortcode'],
            require_public=True,
            require_mutual=False
        )
        
        print(f"\n📋 RESULTADO DA VALIDAÇÃO:")
        print(f"   Usuário: @{first_participant['username']}")
        if is_valid:
            print(f"   Status: ✅ VÁLIDO")
        else:
            print(f"   Status: ❌ INVÁLIDO")
            print(f"   Erros:")
            for error in errors:
                print(f"   - {error}")
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Inicie o backend: cd backend && uv run python main.py")
    print("2. Inicie o frontend: cd frontend && npm run dev")
    print("3. Acesse: http://localhost:5173")
    print("4. Vá na aba '📸 Instagram'")
    print("5. Faça login e teste o sorteio!")
    print()


if __name__ == "__main__":
    main()
