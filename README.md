# TrySober

Protótipo experimental de integração do projeto Monarca com Arch Linux e Sober.

## Objetivo

Construir ferramentas de diagnóstico do Sober, um editor local de Luau e um carregador de arquivos do repositório Monarca, sem presumir que scripts externos possam ser executados no cliente Roblox.

**Limitação:** o Sober não oferece uma API pública conhecida para executar Luau arbitrário no Roblox. Carregar um arquivo no editor não executa código dentro do jogo. A integração direta permanece não comprovada.

## Testar no Arch Linux

```bash
python triesober.py status
python triesober.py fetch-monarca
python triesober.py open-monarca
```

O protótipo utiliza apenas a biblioteca padrão do Python 3. O comando `fetch-monarca` baixa arquivos `.lua` e `.luau` públicos do GitHub para uma pasta local, sem executá-los.

## Próximos passos

1. Validar a detecção do Flatpak Sober em uma máquina Arch real.
2. Revisar a estrutura de `DiscNet/Monarca` e definir o ponto de entrada.
3. Implementar uma interface desktop e editor Luau.
4. Testar integração somente por interfaces documentadas ou em experiências Roblox sob controle do desenvolvedor.

Não injeta bibliotecas em processos, altera memória do Roblox nem contorna controles de segurança.
