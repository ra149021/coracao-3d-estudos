# Auditoria de prontidão para publicação

Data: 29/09/2026. Revisão do histórico alcançável até `b392061` e dos arquivos atuais preparados para o próximo commit. Publicação HTTPS/GitHub autorizada pelo usuário; commit, push e implantação a cargo do agente principal.

## Resultado

**Nenhum impedimento concreto por credenciais, materiais docentes brutos ou modelos sem licença confirmada foi identificado no conjunto versionável revisado.** Os caminhos pessoais atuais encontrados foram tornados portáveis. A revisão não alterou o histórico Git.

## Escopo conferido

- Três commits alcançáveis, 175 nomes de arquivos e 190 blobs distintos; também arquivos modificados e 58 candidatos novos existentes no início da revisão.
- Ausência de PDFs/Office docentes, vídeos, áudio, transcrições brutas, bancos, arquivos de chave e pastas `fontes/`, `materiais/` e `site/assets/local-references/` no histórico alcançável.
- Nenhuma ocorrência dos padrões pesquisados para tokens GitHub/OpenAI, identificadores AWS, chaves Google, blocos de chave privada ou credenciais em URLs. Nenhum valor de credencial foi exibido.
- Identidades dos commits revisados usam endereço `noreply`.
- Os JSONs de evidência pública contêm sínteses curtas e referências; não são cópias integrais das transcrições. O catálogo de aulas contém títulos/IDs/durações, sem caminhos para os arquivos privados.
- Os quatro GLBs públicos atuais não contêm URIs externas de imagens ou buffers.
- O workflow Pages faz checkout dos arquivos versionados e publica somente `site/`. Os materiais docentes e a referência UMN local não acompanham esse artefato.

## Fontes e condições dos modelos

| Conjunto público | Licença indicada e atribuição |
|---|---|
| Coração principal: 46 peças Z-Anatomy + 26 BodyParts3D | Origens por peça preservadas; montagem CC BY-SA 4.0; BodyParts3D independente CC BY 4.0. Aviso histórico BodyParts3D CC BY-SA 2.1 Japan preservado em `site/LICENSES/Z-Anatomy-original.txt`. |
| Respiratório: 175 peças Z-Anatomy | CC BY-SA 4.0; créditos e adaptações no NOTICE. |
| Laringe independente: 40 peças BodyParts3D | CC BY 4.0; créditos e origem próprios no catálogo/NOTICE. |
| HRA independente: 14 peças | CC BY 4.0 confirmada na entrada NIH 3DPX-021000; atribuição e transformação documentadas em `site/assets/heart-hra/ATTRIBUTION.md`. |
| UMN 612/188/064 | Incorporação oficial externa sob clique; arquivos não copiados. Atribuição, licença CC Attribution-NonCommercial exibida pela origem e limites da preparação acompanham os modelos. |
| Three.js e passes de renderização | MIT; arquivos de licença preservados. |

A referência local UMN MC_VALVES continua excluída porque sua redistribuição não foi confirmada. O GLB candidato Rijnstate, com condição própria CC BY-NC-SA 4.0, também continua excluído; seu NOTICE diferencia a licença do modelo da licença do artigo. A cena temporária `heart-author/` está excluída; as quatro câmaras promovidas no coração principal derivam dos modificadores já existentes do Z-Anatomy, com adaptação declarada no NOTICE.

## Sanitização efetuada

- `refinamento/aulas_escopo.json`: nove caminhos absolutos substituídos por referências internas relativas ou nomes de arquivos. Dez hashes de origem preservados.
- `verificacao.json`: três caminhos de PDFs substituídos por nomes dos arquivos; três hashes preservados.
- `refinamento/geometria/README.md` e `refinamento/respiratorio/geometria/README.md`: nove comandos usam `$HOME` com aspas.
- `refinamento/respiratorio/conteudo/build_content.py`: constantes `SRC` e `VAULT` usam `Path.home()`; os caminhos resolvidos nesta instalação permanecem iguais. Sintaxe Python conferida sem executar a geração de conteúdo.

O histórico anterior mantém referências de caminho em seis arquivos. Elas revelam nome de usuário local e organização das pastas acadêmicas, do projeto e do ambiente Python; não foram encontrados dados clínicos pessoais ou segredos nesses caminhos. Essas versões não foram apagadas nem reescritas, conforme instrução de preservar o Git existente.

## Limites

A varredura por padrões não garante a detecção de todo segredo possível. Não houve auditoria forense de objetos Git inalcançáveis, reconhecimento textual de todas as capturas de tela, parecer jurídico de licenças ou teste de navegador nesta revisão. As verificações de interação, download do artefato e publicação pública devem ser concluídas pelo agente principal. Esta conclusão se aplica aos arquivos revisados; inclusão forçada de arquivos ignorados mudaria o resultado.
