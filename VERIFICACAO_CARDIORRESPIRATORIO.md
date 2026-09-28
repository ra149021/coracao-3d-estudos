# Verificação do atlas cardiorrespiratório — v0.3

Conferência em Chromium local, em 28/09/2026. Esta verificação examina funcionamento e integridade; não certifica precisão anatômica integral.

## Modelos e conteúdo

| Conjunto | Peças carregadas | Elegíveis ao treino | Alvos no roteiro |
| --- | ---: | ---: | ---: |
| Coração e contexto vascular | 72 | 53 | 178 |
| Respiratório Z-Anatomy | 167 | 125 | 222 |
| Laringe BodyParts3D independente | 40 | 39 | mesmos 222 respiratórios |

O roteiro cardíaco apresentou 65 alvos com peça associada, 54 com contexto parcial e 59 pendentes. O respiratório apresentou 80, 71 e 71, respectivamente. No modelo laríngeo independente, 20 associados, 26 parciais e 176 sem associação nessa cena. Não somar os modelos como prova de cobertura completa.

Teoria: 14 unidades circulatórias/36 questões e 12 respiratórias/58 questões. Questões autorais, com referências, sem promessa de reproduzir a prova. Transcrições automáticas são localizadores e não foram integralmente conferidas contra o áudio.

## Fluxos executados no navegador

- Página inicial com duas prévias WebGL reais; 3 modelos carregados com contagem compatível com os catálogos.
- Preset de árvore brônquica, corte sagital em 40% e zoom por teclado. A tecla `+` reduziu a distância à câmera.
- Rodada de cinco lobos pulmonares: resposta revelada, avaliação registrada e pausa com restauração do corte/vista anterior.
- Troca respiratório → laringe → respiratório preservou a rodada: uma peça revisada, quatro restantes. A laringe usou armazenamento próprio.
- Leitura marcada e questão respondida em ambos os sistemas; 36 e 58 questões disponíveis, respostas e explicações exibidas, avaliação persistida.
- Ligações da teoria para a peça 3D conferidas: 11 links na primeira unidade respiratória; seleção direta da nasofaringe. Busca por pleura retornou 13 alvos e referências clicáveis. Ausência do servidor de aulas simulada com resposta 404: página apresentou a mensagem de instalação local.
- Página respiratória 104 aberta, imagem carregada e avanço até 105; PDF original ligado à página física correspondente.
- Aula R1: metadados carregados, busca por “nariz” encontrou 8 de 28 segmentos; mudança para 1,5×, avanço de 10 segundos, reprodução e pausa sem erro de mídia.
- Requisição de vídeo com `Range: bytes=0-99` retornou 206, 100 bytes e Content-Range correto. ID desconhecido retornou 404.
- Início, atlas respiratório, teoria e sala de aula em 390 × 844: largura total de 390 px, sem transbordamento horizontal.
- Nenhuma exceção JavaScript capturada nos fluxos concluídos. Avisos de desempenho WebGL do Chromium apareceram ao capturar imagens; não são validação de desempenho em outras máquinas.

## Integridade e materiais

- Sintaxe JavaScript dos módulos e compilação dos scripts Python conferidas; `git diff --check` sem erro.
- Catálogos geométricos têm auditoria própria em `refinamento/respiratorio/geometria/asset_validation.json`.
- Seis documentos, 354 páginas renderizadas, sete vídeos e sete transcrições locais disponíveis. Originais e manifesto com caminhos ficam em `materiais/`, excluídos do Git.
- Servidor em 127.0.0.1; rotas de material baseadas em IDs permitidos; sem listagem de diretórios.
- Capturas com figuras docentes ficam locais e ignoradas no Git. Capturas dos modelos abertos acompanham `output/playwright/`.

## Limites

Não houve validação anatômica individual de todas as malhas, revisão integral das gravações, teste em Safari/Firefox ou em aparelho móvel físico. A largura de celular foi emulada. Há detalhes ausentes e malhas simplificadas. O estudo deve combinar modelo, critérios do roteiro, figuras e explicação docente.
