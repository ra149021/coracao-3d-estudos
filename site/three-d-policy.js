/** UI study policy, not an edit or anatomical validation of source catalogs. */
const documentedSets = new Set([
  'bp_FMA3895', // Catalog: circunflexo, conjunto da fonte; branches not individualized.
  'hra_mitral', 'hra_tricuspid', 'hra_aortic', 'hra_pulmonary', // Entire valves, not individual leaflets/cusps.
]);
export function identificationExclusion(part) {
  if (['resp_medial_basal_segmental_bronchus_of_left_lung_bvii',
       'resp_anterior_basal_segmental_bronchus_of_left_lung_bviii'].includes(part.id))
    return 'Variante basal esquerda não resolvida: B7/B8 coexistem com a representação anteromedial. Fora da identificação individual e de encontrar sem contexto da variante; exploração e nomes originais preservados, sem contar território adicional.';
  if (part.representation === 'aggregate' || documentedSets.has(part.id))
    return 'Representação em conjunto: disponível para explorar, fora da identificação individual e de encontrar.';
  if (part.representation === 'ambiguous' || part.identificationAmbiguous === true)
    return 'Identificação explicitamente ambígua: disponível para explorar, fora do treino.';
  if (part.quizEligible === false)
    return 'Peça mantida apenas para exploração/contexto; identificação individual não aprovada para o treino.';
  return null;
}
export function practiceParts(parts) {
  return parts.map(part => ({...part, quizEligible: !identificationExclusion(part)}));
}
