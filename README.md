# TrySober

Investigação de compatibilidade do Monarca com Arch Linux + Sober.

## Estado verificado

- Sober 1.8.0 identificado em execução no Arch Linux de teste.
- 30 arquivos Lua/Luau do Monarca baixados localmente.
- Diagnóstico da instância do Flatpak funciona.
- Analisador estático identifica uso de APIs de executores.
- **TrySober NÃO executa scripts dentro do Roblox. A interface Luau do cliente Sober não está disponível publicamente.**

## Como testar

    python triesober.py status
    python diagnose.py
    python triesober.py fetch-monarca
    python compatibility.py --format summary
    python -m unittest discover -s tests -v

## Bloqueios de compatibilidade

O arquivo de entrada Monarca.lua baixa hub_core.lua usando game:HttpGet e depois usa loadstring para compilá-lo. Vários módulos usam o mesmo mecanismo. O núcleo também utiliza getgenv, gethui, getcustomasset, readfile e writefile. Essas não são APIs gerais de LocalScript.

Algumas funções do Monarca dependem de scripts instalados no servidor de uma experiência própria, como server/MonarcaInvisibility.server.lua e server/MonarcaTouchBounce.server.lua. Elas não podem ser ativadas em qualquer jogo apenas por um aplicativo Linux.

O relatório é **estático**: ignora comentários/textos, mas não interpreta todas as construções Luau. Não comprova execução, nem compatibilidade em tempo real.

## Caminho técnico

1. Validar a auditoria com o código real do Monarca.
2. Investigar apenas interfaces realmente disponíveis de integração Luau com Sober, sem presumir acesso ao interpretador.
3. Caso não exista interface compatível, adaptar as funções permitidas para experiências Roblox próprias com LocalScripts e ModuleScripts.
4. Uma GUI externa seria apenas editor/gerenciador, não um executor.

Referências:
- https://sober.vinegarhq.org/
- https://create.roblox.com/docs/reference/engine/globals/LuaGlobals
- https://create.roblox.com/docs/reference/engine/classes/ServerScriptService

A ferramenta não modifica memória do Roblox, não injeta bibliotecas e não altera arquivos do Sober.
