# Atlas cardiorrespiratório

Um ambiente de estudo de anatomia circulatória e respiratória que conecta modelos 3D, revisão ativa e material de aula. Desenvolvido por **Victor Hugo**, estudante de Medicina.

**[Abrir o atlas](https://ra149021.github.io/coracao-3d-estudos/)** · [Aulas e slides](https://ra149021.github.io/coracao-3d-estudos/classroom.html) · [Sobre o projeto e fontes](https://ra149021.github.io/coracao-3d-estudos/about.html)

![Página inicial do atlas, com modelos do coração e do sistema respiratório.](docs/atlas-preview.png)

## O que explorar

| Recurso | Uso no estudo |
| --- | --- |
| **Atlas 3D e peças reais** | Coração HRA e pulmões Z-Anatomy com nomes visíveis, seleção, descrição e isolamento; duas reconstruções de CT e dez referências institucionais para comparação. Modelos e fotos no mesmo ambiente. |
| **Exploração didática** | Modelos por estrutura, com seleção, isolamento, transparência e cortes, disponíveis como complemento no acervo integrado. |
| **Vistas do roteiro** | 15 vistas orientadas com transparência, seleção de peças e acesso ao slide correspondente. [Inspeção e limites](refinamento/qualidade/inspecao_roteiros/README.md). |
| **Teoria e revisão** | 26 unidades, 94 perguntas textuais e 10 tarefas visuais, com figuras por seção, comparação de slides e progresso separado por tipo. |
| **Aulas da professora Carmem** | 7 aulas gravadas, busca nas transcrições e retomada do ponto de reprodução. |
| **Slides e roteiro** | 6 documentos e 354 páginas navegáveis, com acesso aos PDFs originais. |
| **Imagens por sistema** | Duas seções recolhíveis: circulatório e respiratório. O site público oferece quatro fotos CC BY-SA; a instalação pessoal preserva 213 entradas dos Ankis e do esquema, com busca, filtros, ampliação e acesso às pranchas. |
| **Tutor de anatomia** | Chat no canto inferior: consulta de 109 seções com links às unidades e IA gratuita experimental pela LLM7, sem chave na rota anônima testada. A biblioteca permanece acessível quando a API falha. |

## Uma sequência para conhecer o projeto

1. Abra **Atlas 3D e peças reais**, carregue um modelo com nomes e escolha uma estrutura para identificá-la.
2. Compare com **Imagens do circulatório** ou **Imagens do respiratório**. Use a seleção para revelar estruturas internas e o isolamento para examinar sua forma.
3. Consulte uma unidade em **Teoria e revisão** e suas questões.
4. Abra **Aulas e materiais** para relacionar o estudo aos slides e às gravações.
5. Consulte **Sobre o projeto** para conhecer a proposta, as fontes e o escopo atual.

O site público funciona no navegador, sem instalação e sem depender dos arquivos do computador do autor. Modelos e bibliotecas estão no repositório; vídeos e PDFs estão no GitHub Releases. Os modelos 3D requerem WebGL 2; aulas e referências externas requerem conexão com a internet.

## Escopo e rigor

O material docente orienta o estudo. Os modelos têm simplificações e **não cobrem integralmente o roteiro**. A associação de um item a uma peça não certifica todos os detalhes anatômicos. O roteiro distingue peças associadas, contexto parcial e itens pendentes.

As transcrições são automáticas e servem para localizar trechos; os termos devem ser conferidos no áudio e nos slides. O progresso é pessoal, salvo apenas no navegador, e não mede domínio do conteúdo.

## Fontes e autoria

- **Geometria:** Z-Anatomy e BodyParts3D. Créditos, licenças e transformações em [NOTICE](site/LICENSES/NOTICE.txt).
- **Referência cardíaca independente:** Human Reference Atlas / HuBMAP, disponibilizada pelo NIH 3D, com [atribuição própria](site/assets/heart-hra/ATTRIBUTION.md).
- **Coração de tomografia:** Matthew Bramlet / NIH 3DPX-002636, domínio público / CC0. GLB oficial preservado; [origem e adaptações de exibição](site/assets/heart-ct/ATTRIBUTION.md).
- **Reconstrução broncovascular de tomografia:** Meershoek et al. (2023), **CC BY-NC-SA 4.0**. A condição não comercial do modelo difere da licença do artigo; [atribuição e conversão](site/assets/lung-ct/NOTICE.md).
- **Peças humanas em 3D:** Visible Heart Laboratories / Universidade de Minnesota e UBC / HIVE, incorporadas dos visualizadores oficiais; arquivos externos não redistribuídos.
- **Fotografias públicas:** quatro peças humanas por Anatomist90 / Wikimedia Commons, CC BY-SA 3.0; [créditos e originais](site/assets/public-specimens/ATTRIBUTION.md).
- **Fotografias pessoais:** dois pacotes Anki locais do colega e o esquema enviado por Victor. O acervo e seu manifesto `site/assets/cadaver-gallery.json` ficam fora do Git; sua autorização de divulgação pública não foi documentada.
- **Material docente:** aulas, slides e roteiro da professora Carmem / UEM. Autoria preservada; esses materiais não integram as licenças das malhas. Os vídeos e PDFs ficam na [release de aulas](https://github.com/ra149021/coracao-3d-estudos/releases/tag/aulas-v1).
- **Teoria:** referências indicadas junto a cada unidade de estudo.

## Executar localmente

Requer Python 3 e navegador com WebGL 2. O site já inclui as dependências de execução.

```bash
python3 scripts/serve_heart.py --open
```

Acesse `http://127.0.0.1:8765` e mantenha o terminal aberto. Os arquivos docentes locais são opcionais: a biblioteca usa as cópias online quando não há acervo instalado.

Para abrir diretamente o acervo integrado, execute `./Abrir_Pecas_Reais.sh`.

## Chat e opção gratuita

Abra **Dúvidas?** no canto inferior. **Biblioteca do atlas** consulta o material e exibe trechos com links, sem geração por IA nem envio a um provedor. Em **IA gratuita · experimental**, a pergunta, até seis mensagens anteriores de IA e até três trechos de teoria **já publicados no GitHub** são enviados à [LLM7](https://llm7.io/) e aos seus provedores. A rota `default` respondeu sem conta ou chave nos testes reais e permite requisições do GitHub Pages. O modelo efetivo aparece na resposta; o roteamento pode mudar. O tutor recebe texto, sem fotos, Ankis, credenciais ou arquivos locais, e mostra as unidades consultadas.

O índice usado pela IA é derivado exclusivamente de dois JSONs públicos, com seus hashes conferidos no GitHub. O gerador recusa fontes alteradas que não tenham sido verificadas para publicação. Dados sem essa confirmação não são enviados pelo chat. A biblioteca é a alternativa para limites, falhas e tempo esgotado; não há tentativa automática de criar conta, obter chave ou usar rota paga. A IA é geral e voltada a dúvidas de estudo, sem validação clínica; confira cada resposta com as fontes. Detalhes e evidências em [Atlas integrado](refinamento/qualidade/atlas_integrado/README.md).

Há também integração opcional com a [faixa gratuita da Groq](https://console.groq.com/docs/rate-limits), que requer conta e chave próprias. Para usá-la no servidor local, copie `chat.env.example` para `.env.chat` na raiz do projeto, preencha `GROQ_API_KEY` localmente e reinicie `scripts/serve_heart.py`. A chave permanece fora de `site/` e do Git; nunca deve ser inserida no JavaScript. Essa opção requer um servidor com a rota `/api/chat`; GitHub Pages sozinho atende a biblioteca e a opção pública sem chave.

## Código e verificações

| Local | Conteúdo |
| --- | --- |
| `site/` | Aplicação estática, modelos, índices e páginas de slides. |
| `site/auditoria/` | Relatório, matriz de cobertura e evidências da auditoria. |
| `scripts/` | Servidor local e preparação dos materiais. |
| `refinamento/` | Registros de geometria, fontes e cobertura. |
| [Revisão funcional final](VERIFICACAO_FINAL_SITE.md) | Correções de bugs, progresso, aulas e disponibilidade pública. |
| [Revisão de apresentação](VERIFICACAO_APRESENTACAO.md) | Conferências de navegação, leitura, modelos e layout móvel. |
| [Verificação das aulas](VERIFICACAO_AULAS.md) | Conferências de documentos, reprodução e navegação. |
| [Ampliação mediastinal](refinamento/qualidade/mediastino/README.md) | 15 peças adicionais, quatro vistas e preservação das malhas anteriores. |
| [Teoria, figuras e prática](refinamento/qualidade/teoria_visual/README.md) | Figuras por seção, tarefas visuais e conexões com roteiro, vistas e peças humanas; resultados da verificação. |
| [Atlas integrado, imagens e tutor](refinamento/qualidade/atlas_integrado/README.md) | Modelos com nomes, fontes de CT, imagens por sistema, chat e verificação da atualização. |
| [Melhorias fundamentadas no conteúdo](refinamento/qualidade/REVISAO_CONTEUDO_SITE.md) | Prioridades para figuras, reconhecimento visual e integração do site. |
| [Histórico técnico](docs/HISTORICO_TECNICO.md) | Evolução dos modelos, métodos e verificações anteriores. |

Alterações em `main` são publicadas pelo workflow **Publicar atlas**. Os vídeos e PDFs ficam fora do histórico Git, na release de aulas.

Correções de conteúdo, fontes ou navegação podem ser registradas nas [issues do projeto](https://github.com/ra149021/coracao-3d-estudos/issues), indicando a página, a estrutura e a referência pertinente.

Os registros de extração dos Ankis ficam apenas na instalação pessoal, em `refinamento/qualidade/pecas_apkg/`, junto ao acervo não publicado.
