# Contexto mediastinal recuperado — atribuição

Geometria: **Z-Anatomy**, Gauthier Kervyn e colaboradores; aplicação de Lluis
Vinent. Base original BodyParts3D, Kousaku Okubo / The Database Center for Life
Science. Licença da derivação geométrica: **CC BY-SA 4.0**:
https://creativecommons.org/licenses/by-sa/4.0/

Fontes originais Z-Anatomy no commit
`6c7f9016bd5899ac8edafd31b9900c151df42ed6`:
https://github.com/LluisV/Z-Anatomy/tree/6c7f9016bd5899ac8edafd31b9900c151df42ed6/Resources/Models/FBX

Arquivos pertinentes: `VisceralSystem100.fbx`, `CardioVascular41.fbx`,
`LymphoidOrgans100.fbx` e `NervousSystem100.fbx`. URLs, hashes e tamanhos da
conversão recuperada constam de `parts.json`. Não foram copiados slides,
mídias pessoais ou arquivos Anki.

## Alterações desta entrega

Extração de 15 peças adicionais da cópia recuperada, sem duplicar suas 175
peças compartilhadas com o atlas público. O script
`scripts/extract_respiratory_context.py` comparou os bytes de todas as posições,
normais e índices das 175 peças compartilhadas antes de aceitar o registro.
Os 15 conjuntos de buffers extras foram copiados byte a byte e reempacotados
em GLB independente; nenhum vértice, normal, índice ou transformação anatômica
foi alterado. O GLB e catálogo originais permanecem intactos. Traduções,
seleção e notas de limites foram preservadas da recuperação. Não houve
remalhamento, ajuste de proporções por peça, inferência de nervos ou ligação
entre acervos de pessoas diferentes.

O visualizador só acrescenta material de exibição, vistas e ocultação. As
peças adicionais são inicialmente ocultas e não são elegíveis para quiz.
Quatro vistas mostram relações mediastinais, nervos e grupos de linfonodos.
São trajetos integrais da fonte: o enquadramento torácico não recorta nem
transforma o trajeto. Frênicos, plexos, vasos linfáticos, sulcos e impressões
pulmonares completos continuam ausentes ou não demonstrados; grupos de
linfonodos não equivalem a linfonodos individualizados. Revisão anatômica
integral pendente.

`provenance.json` registra hashes do GLB recuperado, do modelo base e de cada
buffer extraído. O novo GLB continua sob CC BY-SA 4.0. Manter créditos e licença
em eventual redistribuição; não há endosso dos autores ao atlas local.
