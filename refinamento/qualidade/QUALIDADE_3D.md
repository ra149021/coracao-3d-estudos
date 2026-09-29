# Qualidade 3D — etapa de 28–29/09/2026

Objetivo: melhorar a utilidade anatômica com geometrias prontas, procedência
rastreável e limites explícitos. Quantidade de triângulos, acabamento visual e
cobertura do roteiro são medidas diferentes.

## Entregas e ganho demonstrável

| Frente | Estado nesta etapa | Ganho e limite |
|---|---|---|
| Respiratório Z-Anatomy | **175 peças; 959.255 triângulos.** Oito vasos proximais acrescentados no registro original. | Tronco/bifurcação, duas artérias e quatro veias permitem estudar relações broncovasculares no preset `hilo`. Não incluem rede vascular segmentar nem todos os componentes da raiz pulmonar. |
| Coração: superfícies do autor | **72 peças; 482.116 triângulos**, promovido à cena principal após comparação. | Quatro câmaras avaliadas com o modificador Subsurf/Catmull-Clark e nível de render 2 existentes no arquivo original. Recupera a superfície de exibição prevista pelo autor; não cria novas estruturas ou detalhe histológico. |
| Coração HRA independente | **14 peças; 164.119 triângulos; 9 elegíveis para treino.** | Acrescenta uma representação com septo interventricular selecionável, quatro câmaras e quatro conjuntos valvares. As cinco peças papilares ficam fora do quiz por identidade conflitante, representação parcial ou conferência pendente. |
| Peças institucionais UMN online | Referências 612, 188 e 064, por páginas/players oficiais. | Superfície de peça fixada por perfusão, janela do VD e relação entre valvas. A preparação modifica aparência; não há segmentação de cada alvo do roteiro. Arquivos dessas três referências não foram obtidos localmente. |

No respiratório, R173–R176 são associações nominais dos seis vasos laterais;
R151/R152 indicam apenas contexto regional. Tronco e bifurcação não entram no quiz.
A correção R010 foi preservada. Os **85 IDs diretamente associados** continuam
sujeitos a conferência anatômica individual.

## Método e apresentação

- **Anatomia acrescentada:** oito vasos prontos no mesmo sistema espacial do
  respiratório; septo selecionável no acervo HRA separado. As cenas de origens
  diferentes não foram deformadas para se encaixarem.
- **Superfície autoral recuperada:** o coração principal aplica configurações
  já presentes no `Startup.blend`, preservando IDs e a montagem. A diferença máxima
  das caixas das quatro câmaras ficou abaixo de 0,73 mm na escala nominal; isso
  não certifica erro anatômico, espessura de parede ou inserções.
- **Renderização:** iluminação lateral e oclusão ambiente facilitam a leitura
  do relevo existente. Cores são didáticas. Nenhuma textura fotográfica foi
  atribuída às malhas Z-Anatomy, BP3D ou HRA.
- **Anotações:** os marcos autorais foram investigados, mas nenhuma extremidade
  de linha ou origem de objeto foi promovida automaticamente a ponto anatômico
  validado. A auditoria consta de `MARCOS_AUTORAIS.json`.

A verificação geométrica respiratória registra coordenadas finitas, índices,
contagens, bounds, normais e hashes; superfícies abertas da fonte foram preservadas.
O HRA preserva topologia e relações originais, incluindo 820 faces de área zero
já existentes no átrio direito. O relatório `heart_author_validation.json` confirma que apenas as quatro câmaras mudaram e que as 68 outras malhas preservam exatamente posições, normais e índices. Inspeções estáticas estão nos relatórios de cada
acervo. Os testes de navegador são registrados separadamente em `VERIFICACAO_QUALIDADE_3D.md`, na raiz do projeto.

## Referências independentes e lacunas

A referência broncovascular de CT de Meershoek et al. foi obtida e convertida em
GLB independente, com **312.856 triângulos** preservados. O STL é um conjunto
fundido, sem rótulos de tecidos; os autores fizeram suavização, cortes e entalhes
para impressão. Serve à inspeção geral, sem somar cobertura ou permitir inferir
automaticamente segmentos. Sua licença específica é **CC BY-NC-SA 4.0**.

Os quatro cortes UMN anteriormente instalados continuam sendo uma referência
local distinta das três peças online; sua redistribuição permanece sem confirmação.

Permanecem pendentes: pericárdio/reflexões/seios, esqueleto fibroso e condução;
validação fina de cordas, papilares, óstios e relevos; folhetos/recessos pleurais,
mucosa/pregas vestibulares laríngeas e parênquima segmentar individualizado.
Mais polígonos ou novos acervos não estabelecem 100% de correspondência validada
com os roteiros de estudo.

## Fontes e rastreabilidade

- [Z-Anatomy: modelos Blender](https://github.com/Z-Anatomy/Models-of-human-anatomy)
  e [exportações da aplicação](https://github.com/LluisV/Z-Anatomy/tree/6c7f9016bd5899ac8edafd31b9900c151df42ed6/Resources/Models/FBX):
  CC BY-SA 4.0. Ver `heart_author_candidate.json` e `respiratorio/README.md`.
- [BodyParts3D: acervo oficial](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html):
  CC BY 4.0 conforme a licença atual do acervo; proveniência mantida nas peças.
- [HRA Heart Male / NIH 3DPX-021000](https://3d.nih.gov/entries/3DPX-021000):
  CC BY 4.0; créditos e adaptações em `site/assets/heart-hra/ATTRIBUTION.md`.
- UMN/Visible Heart Labs: [612](https://sketchfab.com/3d-models/perfusion-fixed-human-heart-anatomy-612-f6d63aea48a14d27969067f2754c2d3b),
  [188](https://sketchfab.com/3d-models/plastinated-whole-human-heart-188-d4cc3d373db24d3ca9d08907d620d078)
  e [064](https://sketchfab.com/3d-models/plastinated-human-hear-valve-view-heart0064-62abe2315c5648a8abc3d48bcced28bb):
  páginas indicam CC Attribution–NonCommercial; uso online depende de rede e da
  plataforma. Metadados e limites em `coracao/pecas_reais_recomendadas.json`.
- [Meershoek et al., 2023](https://doi.org/10.1007/s40670-023-01807-x):
  suplemento oficial e atribuição em `respiratorio/rijnstate_reference/NOTICE.md`.
