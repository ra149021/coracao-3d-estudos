# Revisão de apresentação — 29/09/2026

Escopo: apresentação do site e do repositório para demonstração docente. Navegação, leitura, fontes, acesso às aulas e funcionamento das páginas principais. Não foi realizada revisão anatômica integral nem análise do conteúdo das gravações.

## Resultado

Cinco pontos corrigidos: um funcional e quatro de apresentação/navegação. Nenhum erro JavaScript nos fluxos testados. Nenhum transbordamento horizontal nas páginas verificadas a 390 px.

| Ponto | Gravidade | Categoria | Correção |
| --- | --- | --- | --- |
| Figura da teoria buscava `/local/page/` e sumia no site estático | Média | Funcional | Figura servida pela mesma coleção de slides estáticos da sala de aulas. |
| Página inicial anunciava aulas exclusivamente locais | Média | Conteúdo | Textos atualizados para as sete aulas e seis documentos online. |
| Navegação móvel escondia destinos fora da área visível | Média | Navegação | Menu expansível com estado acessível e fechamento pela tecla Escape. |
| Textos pequenos e pouco contrastantes para demonstração | Baixa | Visual | Ajustes de tamanho e contraste no início, teoria e sala de aulas. |
| README centrado em histórico e ausência de apresentação do projeto | Baixa | Apresentação | README reorganizado, captura da aplicação e página Sobre o projeto; histórico preservado. |

## Reprodução e evidências

1. **Figura da teoria:** abrir `theory.html` em servidor estático. Antes, a figura solicitava uma rota exclusiva do servidor local e retornava 404. Depois, a imagem do slide carrega e abre o documento correspondente.
2. **Textos de acesso:** abrir a página inicial e conferir o cartão de aulas e o rodapé. As descrições antigas foram substituídas por informações da biblioteca integrada.
3. **Menu:** usar viewport de 390 px. Os destinos agora aparecem em duas colunas ao acionar Menu; Escape fecha e devolve o foco ao botão.
4. **Leitura:** comparar a página inicial e a teoria a 1440 px e 390 px. Fontes ampliadas e cores de texto mais escuras preservam o estilo do site.
5. **Apresentação:** abrir o README e `about.html`. Ambos apresentam objetivos, autoria, recursos, fontes e escopo antes dos registros de implementação.

Evidências: `output/playwright/refinamento/home-desktop.png`, `home-mobile-menu.png`, `about-desktop.png`, `heart-desktop.png`, `respiratory-desktop.png` e `theory-desktop.png`. Imagens com material docente continuam apenas na pasta de evidências local. A captura pública do início está em `docs/atlas-preview.png`.

## Testes realizados

- Modelos de coração e respiratório carregados no navegador.
- Página inicial com duas prévias 3D e navegação para Sobre o projeto.
- Menu móvel: abrir, conferir `aria-expanded`, fechar por Escape.
- Abertura de slide cardíaco por link com número de página.
- Figura da teoria carregada pelo servidor estático.
- Abertura e fechamento da revisão por perguntas.
- Páginas Sobre, teoria respiratória, atlas respiratório e peças reais a 390 px, sem transbordamento horizontal.
- Links HTML locais conferidos no filesystem, sem arquivo ausente.
- Sintaxe JavaScript e `git diff --check`.

As páginas de peças reais foram abertas sem carregar novas incorporações externas. O teste de navegador não constitui validação de precisão anatômica. Publicação e disponibilidade dos arquivos na release são conferidas separadamente, após o envio.
