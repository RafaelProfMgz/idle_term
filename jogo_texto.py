import os
import sys
import time

# --- Cross-platform tempo/limpa ---
def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausa(msg="Pressione ENTER..."):
    input(msg)

def digitar(texto, delay=0.03):
    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        # No Windows cmd, delay pode ser ignorado se lento; ok.
        time.sleep(delay)
    print()

# --- Jogo ---
def jogar():
    limpar()
    digitar("=== AVENTURA DO DRAGÃO ===")
    digitar("Você acorda numa sala escura. Há 3 portas.")
    digitar("Porta 1: Esquerda (cheira a mofo)\nPorta 2: Centro (som de gotejar)\nPorta 3: Direita (brilho dourado)")
    
    vida = 30
    ouro = 0
    
    # Primeiro nível
    escolha = input("Qual porta escolhe? (1/2/3): ").strip()
    
    if escolha == "1":
        digitar("\nVocê entra pela esquerda...")
        digitar("Um goblin aparece! Lute (A) ou fuja (B)?")
        acao = input("A/B: ").strip().upper()
        if acao == "A":
            vida -= 10
            digitar("Você vence! Mas fica machucado. Vida: " + str(vida))
            ouro += 5
        else:
            vida -= 5
            digitar("Você foge, mas se machuca na corrida. Vida: " + str(vida))
    elif escolha == "2":
        digitar("\nVocê entra pelo centro...")
        digitar("Uma armadilha de espinhos! Cuidado.")
        vida -= 8
        digitar("Você passa raspado. Vida: " + str(vida))
    elif escolha == "3":
        digitar("\nVocê entra pela direita...")
        digitar("Um baú dourado! Você ganha 20 ouro.")
        ouro += 20
    else:
        digitar("Escolha inválida... falta de comida. Perde 5 vida.")
        vida -= 5
    
    # Final
    digitar("\n--- FIM DA AVENTURA ---")
    digitar(f"Vida final: {vida}  |  Ouro: {ouro}")
    if vida <= 0:
        digitar("Você caiu exausto... GAME OVER.")
    elif ouro >= 20:
        digitar("Você é rico! VITÓRIA!")
    else:
        digitar("Sobreviveu, mas não encontrou tesouro.")
    
    pausa()

if __name__ == "__main__":
    try:
        jogar()
    except KeyboardInterrupt:
        print("\nJogo encerrado.")
