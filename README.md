# Coração 3D local

Protótipo em português para explorar o coração em 3D e acompanhar a relação
com um roteiro de anatomia. A prioridade é fidelidade anatômica, com controles
didáticos. **O modelo ainda não cobre integralmente o roteiro.**

## Abrir

Requer Python 3 e um navegador com WebGL 2. Bibliotecas e peças já estão no
repositório; não é necessário instalar npm nem acessar a internet para usar.

```bash
python3 scripts/serve_heart.py --open
```

No Linux, também é possível executar `./Abrir_Coracao_3D.sh`. Deixe o terminal
aberto. Endereço padrão: <http://127.0.0.1:8765>. `Ctrl+C` encerra o servidor.
O serviço atende apenas o computador local. O HTML aberto diretamente como
arquivo não consegue carregar o modelo; use o iniciador.

## Primeira etapa — v0.1

- 39 peças prontas, 129.008 triângulos; GLB de aproximadamente 3,2 MB.
- Girar, aproximar, mover, selecionar, destacar, ocultar e isolar estruturas.
- Vistas anatômicas, transparência, corte em três planos e inversão do corte.
- Conjuntos de câmaras, valvas/papilares e vasos coronários.
- Paletas ilustrativas, nomes em português e identidade preservada da fonte.
- Fontes, licenças, matriz de cobertura e download do GLB na própria página.

As quatro câmaras e peças internas usam superfícies extraídas de `Startup.blend`.
Os vasos vêm de `CardioVascular41.fbx`, da aplicação Z-Anatomy. A conversão
comum `(x,y,z) → (x,z,-y)` e uma escala uniforme preservam a disposição original.
Os limites das 17 peças compartilhadas foram comparados entre os dois arquivos.
Isso verifica registro técnico; não substitui a conferência anatômica.

### Limitações conhecidas

Faltam, nesta montagem, as cúspides anteriores da mitral e da tricúspide,
parte do conjunto papilar esquerdo, pericárdio, esqueleto fibroso, condução
e vários relevos internos. As cordas integram as malhas dos folhetos.
As malhas da base apresentam simplificações. Não há textura fotográfica nem
validação especializada de cada alvo. Cortes não recebem tampas artificiais.

O levantamento principal tem 156 alvos: 70 com geometria associada nos acervos,
47 parciais e 39 não localizados. Esses números **não são a cobertura da cena**.
Mesmo o potencial de 75% depende de conferir todos os parciais. Os 22 alvos
complementares dos slides são contados separadamente.

## Segunda etapa

Meta solicitada: correspondência de 100% com o roteiro, com realismo prioritário.
A conclusão exige demonstrar e conferir cada item, sem contar rótulo, descrição
ou forma genérica como representação anatômica completa.

Prioridades:

1. Integrar peças prontas faltantes, verificando escala, posição e inserções.
2. Relacionar cada alvo à geometria, fonte, estado e evidência de validação.
3. Criar percurso de estudo e treino de identificação, incluindo lacunas.
4. Melhorar materiais, iluminação, navegação e legibilidade sem inventar anatomia.
5. Procurar fontes mais detalhadas para relevos internos e envoltórios.

## Organização

- `site/`: aplicação estática, dependências locais, modelo, créditos e auditoria.
- `scripts/serve_heart.py`: servidor local com biblioteca padrão.
- `scripts/build_heart_site_assets.py`: geração do GLB a partir dos dados de origem.
- `matriz_coracao.json` / `.csv`: todos os alvos e suas evidências.
- `RELATORIO.md`: método da auditoria.
- `output/playwright/`: evidências de verificação de interface, quando disponíveis.

Arquivos de aula originais, credenciais, ambientes Python, dependências npm e
downloads brutos não fazem parte do repositório. A aplicação pronta não depende
deles. Os scripts de extração requerem os acervos locais indicados na auditoria;
`site/assets/` contém o resultado já preparado.

## Créditos e licenças

Geometria: [Z-Anatomy](https://github.com/Z-Anatomy/Models-of-human-anatomy),
Gauthier Kervyn e colaboradores; aplicação por Lluis Vinent; base de
BodyParts3D / Kousaku Okubo / The Database Center for Life Science.
A derivação geométrica distribuída aqui permanece **CC BY-SA 4.0**.
Avisos históricos da origem são preservados em `site/LICENSES/`.
Three.js 0.186.1 usa licença MIT. Consulte os avisos completos em
[NOTICE](site/LICENSES/NOTICE.txt). Não há arquivos de ouvido ou rim de outras licenças.

As notas breves usam o roteiro local e
[OpenStax, Heart Anatomy](https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy).
