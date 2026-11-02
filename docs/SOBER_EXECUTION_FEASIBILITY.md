# TrySober — análise de execução Luau no Sober

Data da análise: 2026-11-02
Ambiente testado pelo usuário: Arch Linux, Sober Flatpak 1.8.0, x86_64.

## Objetivo e critério de sucesso

Objetivo original: carregar o painel Monarca dentro de uma sessão de Roblox executada pelo Sober, incluindo experiências de terceiros.

Critério mínimo de sucesso para um **executor**:
1. Estabelecer um canal de execução de código Luau **dentro do cliente Roblox**.
2. Executar um teste mínimo verificável na sessão.
3. Demonstrar compatibilidade com as APIs requeridas pelo Monarca.
4. Somente então disponibilizar carregamento do `Monarca.lua`.

**Nenhuma das etapas 1 a 4 foi demonstrada.** O TrySober atual não deve se apresentar como executor.

## Constatações observadas

| Item | Estado | Evidência |
| --- | --- | --- |
| Sober 1.8.0 instalado | Confirmado | `diagnose.py` executado no Arch Linux |
| Sober em execução | Confirmado | Instância Flatpak e PID obtidos |
| Download de scripts Monarca | Confirmado | 30 arquivos Lua/Luau obtidos localmente |
| Análise estática | Confirmado | `compatibility.py` e testes unitários |
| Canal de execução Luau no Sober | **Não demonstrado** | Nenhum mecanismo encontrado no escopo analisado |
| Monarca executado no Roblox | **Não** | Não houve teste de execução |

A permissão `shared=ipc` do Flatpak não equivale a uma API de Luau no Roblox.
O Sober é proprietário; os repositórios públicos oficiais hospedam documentação e relatórios de problemas, não o motor de execução.

## Interface pública documentada pelo Sober

A documentação oficial lista configurações para desempenho, gráficos, interface, FFlags e outros ajustes. Nenhuma entrada documentada fornece acesso ao interpretador Luau ou executa scripts arbitrários.

O `asset_overlay` permite substituir *recursos de mídia* presentes nos assets do APK, como cursores e sons. Substituir recursos **não injeta ou executa scripts** e não é um caminho validado para carregar Monarca.

Referências:
- https://sober.vinegarhq.org/
- https://vinegarhq.org/Sober/FAQ/
- https://vinegarhq.org/Sober/Configuration/index.html
- https://vinegarhq.org/Sober/Configuration/TipsAndTricks.html

## Dependências reais do Monarca

A auditoria de 30 arquivos encontrou:
- 6 referências a carregamento de código dinâmico (`loadstring`).
- 6 referências a mecanismos HTTP específicos do executor (`game:HttpGet`).
- 18 referências a helpers de ambiente (`getgenv`, `gethui`, assets personalizados etc.).
- 35 referências de filesystem (armazenamento local).
- 0 referências do grupo de hooks pesquisado (não prova ausência de todas as técnicas).

A contagem é estática e pode mudar com o código ou com o analisador.
Exemplos de arquivos: `Monarca.lua`, `hub_core.lua`, `modules/waypoints.lua`.

Alguns módulos (invisibilidade de servidor e bounce) requerem scripts instalados no servidor de uma experiência administrada pelo desenvolvedor. Um executor **não concede** controle sobre a lógica de servidor em jogos de terceiros.

## Alternativas avaliadas

### 1. Aplicativo Linux externo comunicando-se com Sober

Viável para gerenciar scripts, atualizações, editor, logs e detectar a sessão. **Não** permite, por si só, executar Luau dentro do Roblox.

### 2. Asset overlay / FFlags / alterações de configuração

São recursos documentados do Sober, mas **não** fornecem execução arbitrária de código Luau. Não tentar renomear código Lua como textura ou FFlag.

### 3. Executor experimental não oficial

Existem páginas de projetos que anunciam injeção/execução para Sober, mas anúncios, vídeos ou telas de produto não equivalem a binários públicos auditáveis e testados. Não incorporar código ou dependências não verificados à ferramenta.
Referência de anúncio (não verificação): https://www.zafirhub.it/executor

### 4. Experiência Roblox própria (via Studio)

É possível adaptar o painel para `LocalScript`/`ModuleScript` e instalar os scripts de servidor necessários em uma experiência sob controle do desenvolvedor. Isso permite execução real durante o jogo pelo Sober, mas **não** é um executor para jogos de terceiros.
Referência: https://create.roblox.com/docs/reference/engine/classes/StarterPlayerScripts

## Decisão técnica

**Estado: investigação de executor bloqueada por ausência de mecanismo de execução reproduzível.**
Não afirmar que o cliente possui canal de execução apenas porque o processo é acessível no Linux. Não prometer suporte a jogos arbitrários.

Próximos trabalhos úteis:
1. Manter o analisador de compatibilidade e seus testes.
2. Desenvolver, se desejado, editor/gerenciador Linux com indicação explícita de `não executa no Sober`.
3. Para obter uma demonstração real dentro do Roblox sem um executor, portar um subconjunto de módulos para uma experiência própria.
4. Reavaliar a viabilidade de executor apenas se aparecer uma API pública de Luau no Sober ou uma prova independente, reproduzível e autorizada de execução no cliente.

Não foram executados procedimentos de modificação de memória, injeção de bibliotecas ou contorno de proteção do Roblox.
