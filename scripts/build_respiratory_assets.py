"""Build the respiratory atlas from author-exported, positioned Z-Anatomy data.

Read GLB files converted by Assimp from the pinned official FBX exports. No
Blender execution, procedural anatomy, fitted geometry or remote requests.
All structures share one original world space and one display transform.
"""
from pathlib import Path
import hashlib
import json
import re
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/respiratory'
DOC = ROOT / 'refinamento/respiratorio/geometria'
OUT.mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)
CENTER = np.array([0., 142., 0.])  # centimetres in the original FBX world
SCALE = .2
GROUPS = {
    'nariz': 'Nariz e cavidade nasal', 'seios': 'Seios paranasais',
    'faringe': 'Faringe e palato', 'laringe': 'Laringe · cartilagens e hioide',
    'musculos_laringe': 'Músculos da laringe', 'ligamentos_laringe': 'Membranas e ligamentos da laringe',
    'arvore': 'Traqueia e árvore brônquica', 'pulmoes': 'Lobos pulmonares',
    'pleuras': 'Pleura · conjunto', 'respiracao': 'Músculos da respiração',
    'musculos_faringe': 'Músculos da faringe', 'contexto_torax': 'Contexto torácico',
    'contexto_cabeca': 'Contexto ósseo da cabeça', 'musculos_pescoco': 'Músculos supra e infra-hióideos',
    'vascular_pulmonar': 'Vasos pulmonares proximais',
    'contexto_mediastino': 'Contexto mediastinal',
    'linfaticos_torax': 'Linfonodos traqueobronquiais e paratraqueais',
    'nervos_torax': 'Nervos vagos e troncos simpáticos',
}
COLORS = {
    'nariz': '#c8bba6', 'seios': '#a8c2bc', 'faringe': '#b87878', 'laringe': '#bcc6bd',
    'musculos_laringe': '#ac645f', 'ligamentos_laringe': '#e3d8b9', 'arvore': '#d9c4a0',
    'pulmoes': '#c997a0', 'pleuras': '#b5ced0', 'respiracao': '#a86766',
    'musculos_faringe': '#b66f6b', 'contexto_torax': '#d0c6b0',
    'contexto_cabeca': '#d9cdb8', 'musculos_pescoco': '#b87c73',
    'vascular_pulmonar': '#658ba9',
    'contexto_mediastino': '#b87878', 'linfaticos_torax': '#91ae7d',
    'nervos_torax': '#d6bd78',
}
PARTS = []


def add(name, label, group, source, note='', **kwargs):
    item = dict(sourceName=name, label=label, group=group, sourceFile=source + '.fbx',
                      note=note or 'Superfície anatômica original do atlas, selecionável individualmente.',
                      defaultVisible=not group.startswith('contexto'),
                      quizEligible=not group.startswith('contexto'))
    item.update(kwargs)
    PARTS.append(item)


def paired(name, label, group, source, note='', **kwargs):
    for side, pt in [('l', 'lado esquerdo'), ('r', 'lado direito')]:
        add(name + '.' + side, label + ' · ' + pt, group, source, note, **kwargs)


V, S, M, J = 'VisceralSystem100', 'SkeletalSystem100', 'MuscularSystem100', 'Joints100'
add('Mucosa of nasal cavity', 'Mucosa da cavidade nasal', 'nariz', V,
    'Superfície agregada da fonte; meatos, regiões olfatória e respiratória não estão separados.', representation='aggregate')
add('Nasal septal cartilage', 'Cartilagem do septo nasal', 'nariz', S)
paired('Lateral process of nasal septal cartilage', 'Processo lateral da cartilagem do septo nasal', 'nariz', S)
paired('Major alar cartilage', 'Cartilagem alar maior', 'nariz', S)
paired('Inferior nasal concha bone', 'Concha nasal inferior', 'nariz', S)
add('Ethmoid bone', 'Osso etmoide', 'nariz', S,
    'Conjunto ósseo: conchas média/superior e lâmina perpendicular não são peças separadas.', representation='aggregate')
add('Vomer', 'Vômer', 'nariz', S)
add('Sinus of frontal bone', 'Seio frontal · conjunto', 'seios', S,
    'Modelo da cavidade sinusal; não representa uma lâmina óssea isolada.', representation='cavity_surface')
add('Sinus of sphenoid bone', 'Seio esfenoidal · conjunto', 'seios', S,
    'Modelo da cavidade sinusal; não representa uma lâmina óssea isolada.', representation='cavity_surface')
for word, pt in [('Anterior', 'anteriores'), ('Middle', 'médias'), ('Posterior', 'posteriores')]:
    paired(word + ' cells of ethmoid bone', 'Células etmoidais ' + pt, 'seios', S,
           'Conjunto de células etmoidais da fonte; não individualiza cada célula.', representation='aggregate')
for name, label in [('Nasopharynx', 'Nasofaringe'), ('Oropharynx', 'Orofaringe'),
                    ('Laryngopharynx', 'Laringofaringe'), ('Soft palate', 'Palato mole'),
                    ('Uvula of palate', 'Úvula palatina')]:
    add(name, label, 'faringe', V,
        'Superfície original do atlas; parede, mucosa e luz não estão segmentadas em camadas independentes.')
add('Tongue', 'Língua · contexto da via oral', 'faringe', V,
    'Superfície externa para situar a passagem oral; musculatura intrínseca não individualizada.')
for name, label in [('Hyoid bone', 'Osso hioide'), ('Thyroid cartilage', 'Cartilagem tireóidea'),
                    ('Cricoid cartilage', 'Cartilagem cricóidea')]:
    add(name, label, 'laringe', S)
paired('Arytenoid cartilage', 'Cartilagem aritenóidea', 'laringe', S)
paired('Corniculate cartilage', 'Cartilagem corniculada', 'laringe', S)
add('Epiglottis', 'Epiglote', 'laringe', V,
    'Peça denominada epiglote na fonte; cartilagem e mucosa não estão separadas.')
for name, label in [
    ('Lateral crico-arytenoid muscle', 'Músculo cricoaritenóideo lateral'),
    ('Posterior crico-arytenoid muscle', 'Músculo cricoaritenóideo posterior'),
    ('External part of thyro-arytenoid muscle', 'Músculo tireoaritenóideo · parte externa'),
    ('Ary-epiglottic part of oblique arytenoid muscle', 'Músculo aritenóideo oblíquo · parte ariepiglótica'),
    ('Thyro-epiglottic part of thyro-arytenoid muscle', 'Músculo tireoaritenóideo · parte tireoepiglótica'),
    ('Straight part of cricothyroid muscle', 'Músculo cricotireóideo · parte reta'),
    ('Oblique part of cricothyroid muscle', 'Músculo cricotireóideo · parte oblíqua'),
]:
    paired(name, label, 'musculos_laringe', M)
add('Transverse arytenoid muscle', 'Músculo aritenóideo transverso', 'musculos_laringe', M)
for name, label in [('Quadrangular membrane', 'Membrana quadrangular'),
                    ('Lateral thyrohyoid ligament', 'Ligamento tireo-hióideo lateral'),
                    ('Cricopharyngeal ligament', 'Ligamento cricofaríngeo')]:
    paired(name, label, 'ligamentos_laringe', J)
add('Median thyrohyoid ligament', 'Ligamento tireo-hióideo mediano', 'ligamentos_laringe', J,
    'Peça mediana da fonte; não equivale à membrana tireo-hióidea inteira.')
add('Median cricothyroid ligament', 'Ligamento cricotireóideo mediano', 'ligamentos_laringe', J,
    'Parte mediana individualizada; não representa todo o cone elástico.')
add('Trachea', 'Traqueia', 'arvore', V,
    'Peça original com relevo dos anéis; cartilagens, parede e músculo traqueal não estão individualizados.')
BRONCHI = [
    ('Left main bronchus', 'Brônquio principal esquerdo'),
    ('Right main bronchus', 'Brônquio principal direito'),
    ('Left superior lobar bronchus', 'Brônquio lobar superior esquerdo'),
    ('Left inferior lobar bronchus', 'Brônquio lobar inferior esquerdo'),
    ('Right superior lobar bronchus', 'Brônquio lobar superior direito'),
    ('Intermediate bronchus.r', 'Brônquio intermédio direito'),
    ('Middle lobar bronchus.r', 'Brônquio lobar médio direito'),
    ('Right inferior lobar bronchus', 'Brônquio lobar inferior direito'),
    ('Apical segmental bronchus of right lung (BI)', 'Brônquio segmentar apical direito · B1'),
    ('Posterior segmental bronchus of right lung (BII)', 'Brônquio segmentar posterior direito · B2'),
    ('Anterior segmental bronchus of right lung (BIII)', 'Brônquio segmentar anterior direito · B3'),
    ('Lateral segmental bronchus of right lung (BIV)', 'Brônquio segmentar lateral direito · B4'),
    ('Medial segmental bronchus of right lung (BV)', 'Brônquio segmentar medial direito · B5'),
    ('Superior segmental bronchus of right lung (BVI)', 'Brônquio segmentar superior direito · B6'),
    ('Medial basal segmental bronchus of right lung (BVII)', 'Brônquio segmentar basal medial direito · B7'),
    ('Anterior basal segmental bronchus of right lung (BVIII)', 'Brônquio segmentar basal anterior direito · B8'),
    ('Lateral basal segmental bronchus of right lung (BIX)', 'Brônquio segmentar basal lateral direito · B9'),
    ('Posterior basal segmental bronchus of right lung (BX)', 'Brônquio segmentar basal posterior direito · B10'),
    ('Apicoposterior segmental bronchus of left lung (BI+BII)', 'Brônquio segmentar apicoposterior esquerdo · B1+2'),
    ('Anterior segmental bronchus of left lung (BIII)', 'Brônquio segmentar anterior esquerdo · B3'),
    ('Superior lingular segmental bronchus of left lung (BIV)', 'Brônquio segmentar lingular superior · B4'),
    ('Inferior lingular segmental bronchus of left lung (BV)', 'Brônquio segmentar lingular inferior · B5'),
    ('Superior segmental bronchus of left lung (BVI)', 'Brônquio segmentar superior esquerdo · B6'),
    ('Medial basal segmental bronchus of left lung (BVII)', 'Brônquio segmentar basal medial esquerdo · B7'),
    ('Anterior basal segmental bronchus of left lung (BVIII)', 'Brônquio segmentar basal anterior esquerdo · B8'),
    ('Lateral basal segmental bronchus of left lung (BIX)', 'Brônquio segmentar basal lateral esquerdo · B9'),
    ('Posterior basal segmental bronchus of left lung (BX)', 'Brônquio segmentar basal posterior esquerdo · B10'),
    ('(Anteromedial basal segmental bronchus of left lung)', 'Brônquio basal anteromedial esquerdo · representação da fonte'),
]
for name, label in BRONCHI:
    add(name, label, 'arvore', V,
        'Malha pronta exportada de curvas do autor, com trajeto e calibre preservados. Os ramos finos integram a mesma peça; não representam alvéolos.',
        representation='authored_curve_surface')
PARTS[-1]['quizEligible'] = False
PARTS[-1]['note'] += ' A fonte mantém também peças B7/B8; tratar este agregado com cautela, sem contar uma estrutura extra.'
PARTS[-1]['defaultVisible'] = False
for name, label, color in [
    ('Superior lobe of right lung', 'Pulmão direito · lobo superior', '#c8969b'),
    ('Middle lobe of right lung', 'Pulmão direito · lobo médio', '#d4a7a1'),
    ('Inferior lobe of right lung', 'Pulmão direito · lobo inferior', '#b9818c'),
    ('Superior lobe of left lung', 'Pulmão esquerdo · lobo superior', '#c997a2'),
    ('Inferior lobe of left lung', 'Pulmão esquerdo · lobo inferior', '#b47e91'),
]:
    add(name, label, 'pulmoes', V,
        'Lobo original individualizado. Fissuras aparecem nas relações entre as superfícies; segmentos broncopulmonares não estão separados.',
        color=color, representation='whole_lobe')
add('Pleura', 'Pleura · superfície agregada', 'pleuras', V,
    'Malha única da fonte. Não separa pleura parietal/visceral, suas regiões ou recessos; transparência ajuda a examinar as relações.',
    representation='aggregate', quizEligible=False)
PARTS[-1]['defaultVisible'] = False
add('Diaphragm_node', 'Diafragma', 'respiracao', M,
    'Superfície muscular original; pilares, hiatos e centro tendíneo não são peças selecionáveis separadas.', sourceAlias='Diaphragm')
for name, label in [('External intercostal muscles', 'Músculos intercostais externos'),
                    ('Internal intercostal muscles', 'Músculos intercostais internos'),
                    ('Innermost intercostal muscles', 'Músculos intercostais íntimos')]:
    paired(name, label, 'respiracao', M,
           'Conjunto muscular de um lado do tórax; cada espaço intercostal não é uma peça independente.')
    for item in PARTS[-2:]: item['defaultVisible'] = False
for name, label in [('Superior pharyngeal constrictor', 'Músculo constritor superior da faringe'),
                    ('Middle pharyngeal constrictor', 'Músculo constritor médio da faringe'),
                    ('Inferior pharyngeal constrictor', 'Músculo constritor inferior da faringe'),
                    ('Stylopharyngeus muscle', 'Músculo estilofaríngeo'),
                    ('Palatopharyngeus muscle', 'Músculo palatofaríngeo')]:
    paired(name, label, 'musculos_faringe', M)
    for item in PARTS[-2:]: item['defaultVisible'] = False
paired('Nasal bone', 'Osso nasal', 'contexto_cabeca', S)
paired('Palatine bone', 'Osso palatino', 'contexto_cabeca', S)
paired('Maxilla', 'Maxila', 'contexto_cabeca', S)
paired('Lacrimal bone', 'Osso lacrimal', 'contexto_cabeca', S)
add('Sphenoid bone', 'Osso esfenoide', 'contexto_cabeca', S)
for name, label in [('Sternohyoid muscle', 'Músculo esterno-hióideo'),
                    ('Sternothyroid muscle', 'Músculo esternotireóideo'),
                    ('Thyrohyoid muscle', 'Músculo tireo-hióideo'),
                    ('Omohyoid muscle', 'Músculo omo-hióideo'),
                    ('Mylohyoid muscle', 'Músculo milo-hióideo'),
                    ('Geniohyoid muscle', 'Músculo gênio-hióideo'),
                    ('Stylohyoid muscle', 'Músculo estilo-hióideo'),
                    ('Anterior belly of digastric muscle', 'Músculo digástrico · ventre anterior'),
                    ('Posterior belly of digastric muscle', 'Músculo digástrico · ventre posterior'),
                    ('Intermediate tendon of digastric muscle', 'Músculo digástrico · tendão intermédio')]:
    paired(name, label, 'musculos_pescoco', M, defaultVisible=False)
for name, label in [('Manubrium of sternum', 'Manúbrio do esterno'),
                    ('Body of sternum', 'Corpo do esterno'), ('Xiphoid process', 'Processo xifoide')]:
    add(name, label, 'contexto_torax', S)
numbers = ['First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Ninth','Tenth','Eleventh','Twelfth']
for number, name in enumerate(numbers, 1):
    paired(name + ' rib', str(number) + 'ª costela', 'contexto_torax', S)
for name, label in [('Right atrium', 'Átrio direito'), ('Right ventricle', 'Ventrículo direito'),
                    ('Left atrium', 'Átrio esquerdo'), ('Left ventricle', 'Ventrículo esquerdo')]:
    add(name, label + ' · contexto cardíaco', 'contexto_torax', 'CardioVascular41',
        'Câmara cardíaca da mesma fonte e no mesmo registro; incluída para estudar relações torácicas.',
        color='#a96569')

for name, label, color in [
    ('Pulmonary trunk', 'Tronco pulmonar', '#648cae'),
    ('Bifurcation of pulmonary trunk', 'Bifurcação do tronco pulmonar', '#648cae'),
    ('Right pulmonary artery', 'Artéria pulmonar direita', '#648cae'),
    ('Left pulmonary artery', 'Artéria pulmonar esquerda', '#648cae'),
    ('Right superior pulmonary vein', 'Veia pulmonar superior direita', '#b87177'),
    ('Right inferior pulmonary vein', 'Veia pulmonar inferior direita', '#b87177'),
    ('Left superior pulmonary vein', 'Veia pulmonar superior esquerda', '#b87177'),
    ('Left inferior pulmonary vein', 'Veia pulmonar inferior esquerda', '#b87177'),
]:
    add(name, label, 'vascular_pulmonar', 'CardioVascular41',
        'Trecho proximal do vaso no registro original do atlas; sem ramos intrapulmonares segmentares separados. '
        'Azul nas artérias e vermelho nas veias pulmonares são cores didáticas de oxigenação, não texturas do tecido.',
        color=color, defaultVisible=False, representation='proximal_vessel',
        quizEligible=name not in ('Pulmonary trunk', 'Bifurcation of pulmonary trunk'))

# Append new context after the existing atlas pieces so their order and geometry
# remain stable. Each addition uses its complete authored surface and the same
# world transform; no thoracic cropping, fitting or procedural anatomy.
add('Oesophagus', 'Esôfago · contexto mediastinal', 'contexto_mediastino', V,
    'Superfície integral do esôfago da fonte, no mesmo registro da traqueia e dos pulmões. '
    'Não individualiza regiões, camadas da parede ou impressões pulmonares; inspeção visual pendente.',
    defaultVisible=False, quizEligible=False, representation='mediastinal_context')
for name, label, color in [
    ('Ascending aorta', 'Aorta ascendente', '#ba7275'),
    ('Aortic arch', 'Arco da aorta', '#ba7275'),
    ('Thoracic aorta', 'Aorta torácica', '#ba7275'),
    ('Left subclavian artery', 'Artéria subclávia esquerda', '#ba7275'),
    ('Superior vena cava', 'Veia cava superior', '#658ba9'),
    ('Azygos vein', 'Veia ázigos', '#658ba9'),
]:
    add(name, label + ' · contexto mediastinal', 'contexto_mediastino', 'CardioVascular41',
        'Superfície integral do vaso da fonte, sem recorte ou ajuste de trajeto. '
        'Ajuda a examinar relações mediastinais; não individualiza sulcos pulmonares. '
        'Cores didáticas; inspeção visual pendente.',
        color=color, defaultVisible=False, quizEligible=False, representation='mediastinal_context')
for name, label in [
    ('Inferior tracheobronchial nodes', 'Linfonodos traqueobronquiais inferiores · conjunto'),
    ('Superior tracheobronchial nodes', 'Linfonodos traqueobronquiais superiores · conjunto'),
    ('Paratracheal cervical nodes', 'Linfonodos paratraqueais cervicais · conjunto'),
    ('Paratracheal thoracic nodes', 'Linfonodos paratraqueais torácicos · conjunto'),
]:
    add(name, label, 'linfaticos_torax', 'LymphoidOrgans100',
        'Conjunto original de linfonodos no mesmo registro anatômico. Cada linfonodo '
        'e suas conexões linfáticas não são peças independentes; inspeção visual pendente.',
        defaultVisible=False, quizEligible=False, representation='aggregate')
for name, label in [('Vagus nerve (X)', 'Nervo vago (X)'),
                    ('Sympathetic trunk', 'Tronco simpático')]:
    paired(name, label, 'nervos_torax', 'NervousSystem100',
           'Trajeto integral da peça original, incluindo extensões fora do tórax; sem recorte '
           'ou ajuste por região. Ramos, plexos e gânglios não estão individualizados nesta peça; '
           'inspeção visual pendente.',
           defaultVisible=False, quizEligible=False, representation='authored_nerve_surface')


class SourceGLB:
    def __init__(self, name, path=None):
        self.name = name
        self.path = path or ROOT / 'malhas' / (name + '.glb')
        self.raw = self.path.read_bytes()
        assert self.raw[:4] == b'glTF'
        size, kind = struct.unpack_from('<II', self.raw, 12)
        assert kind == 0x4e4f534a
        self.g = json.loads(self.raw[20:20 + size])
        self.binary_start = 28 + size
        self.world = {}
        self.nodes = {node['name']: i for i, node in enumerate(self.g['nodes']) if 'mesh' in node}

        def visit(index, parent):
            node = self.g['nodes'][index]
            assert not any(key in node for key in ('translation', 'rotation', 'scale'))
            matrix = np.array(node.get('matrix', np.eye(4).flatten())).reshape(4, 4).T
            self.world[index] = parent @ matrix
            for child in node.get('children', []): visit(child, self.world[index])
        for top in self.g['scenes'][self.g.get('scene', 0)]['nodes']: visit(top, np.eye(4))

    def accessor(self, index):
        acc = self.g['accessors'][index]
        view = self.g['bufferViews'][acc['bufferView']]
        assert not acc.get('sparse') and view['buffer'] == 0
        width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[acc['type']]
        dtype = np.dtype({5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[acc['componentType']])
        return np.ndarray((acc['count'], width), dtype=dtype, buffer=self.raw,
                          offset=self.binary_start + view.get('byteOffset', 0) + acc.get('byteOffset', 0),
                          strides=(view.get('byteStride', width * dtype.itemsize), dtype.itemsize)).copy()

    def geometry(self, name):
        node_index = self.nodes[name]
        node = self.g['nodes'][node_index]
        matrix = self.world[node_index]
        points, faces, offset = [], [], 0
        for primitive in self.g['meshes'][node['mesh']]['primitives']:
            assert primitive.get('mode', 4) == 4
            vertices = self.accessor(primitive['attributes']['POSITION'])
            vertices = vertices @ matrix[:3, :3].T + matrix[:3, 3]
            indices = self.accessor(primitive['indices']).reshape(-1, 3).astype('<u4')
            if np.linalg.det(matrix[:3, :3]) < 0: indices = indices[:, [0, 2, 1]]
            points.append(vertices); faces.append(indices + offset); offset += len(vertices)
        return np.concatenate(points), np.concatenate(faces), node_index


def normal_array(vertices, faces):
    face_normals = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]], vertices[faces[:, 2]] - vertices[faces[:, 0]])
    normals = np.zeros_like(vertices)
    for column in range(3): np.add.at(normals, faces[:, column], face_normals)
    cancelled = np.flatnonzero(np.linalg.norm(normals, axis=1) < 1e-12)
    for index in cancelled:
        incident = np.flatnonzero(np.any(faces == index, axis=1))
        if len(incident): normals[index] = face_normals[incident[np.argmax(np.linalg.norm(face_normals[incident], axis=1))]]
        else: normals[index] = [0., 1., 0.]
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-12)
    return normals.astype('<f4'), int(len(cancelled))


def main():
    readers = {name: SourceGLB(name) for name in {part['sourceFile'][:-4] for part in PARTS}}
    requirement_file = OUT / 'requirements.json'
    requirements = json.loads(requirement_file.read_text()).get('alvos', []) if requirement_file.exists() else []
    geometry, audit = [], []
    for part in PARTS:
        meta = dict(part)
        name = meta['sourceName']; reader = readers[meta['sourceFile'][:-4]]
        vertices, faces, node_index = reader.geometry(name)
        source_bounds = [vertices.min(0).tolist(), vertices.max(0).tolist()]
        vertices = ((vertices - CENTER) * SCALE).astype('<f4')
        assert np.isfinite(vertices).all() and len(vertices) > 2 and len(faces) > 0
        assert faces.min() >= 0 and faces.max() < len(vertices)
        assert np.abs(vertices).max() < 30
        normals, normal_fallbacks = normal_array(vertices, faces)
        areas = np.linalg.norm(np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]], vertices[faces[:, 2]] - vertices[faces[:, 0]]), axis=1)
        meta.update(id='resp_' + re.sub('[^a-z0-9]+', '_', name.lower()).strip('_'),
                    source='Z-Anatomy', license='CC BY-SA 4.0', sourceNode=node_index,
                    color=meta.get('color', COLORS[meta['group']]),
                    tissueColor=meta.get('color', COLORS[meta['group']]),
                    vertices=len(vertices), triangles=len(faces),
                    bounds=[vertices.min(0).tolist(), vertices.max(0).tolist()],
                    requirement=None, requirementIds=[])
        aliases = {name, meta.get('sourceAlias', name)}
        matches = [r for r in requirements if aliases.intersection(r.get('z_evidencia', []))]
        exact = [r for r in matches if r.get('tipo') == 'estrutura' and r.get('status') == 'geometria_disponivel']
        related = [r for r in matches if r not in exact]
        meta['requirementIds'] = [r['id'] for r in exact]
        meta['relatedRequirementIds'] = [r['id'] for r in related]
        meta['requirementMatches'] = [{'id': r['id'], 'label': r['estrutura'], 'type': r.get('tipo'),
                                       'match': 'source_name_candidate', 'visualValidation': 'pending_individual',
                                       'separateStructure': r in exact} for r in matches]
        if meta['group'] == 'vascular_pulmonar' and meta['quizEligible']:
            for region in requirements:
                if region['id'] in ('R151', 'R152'):
                    meta['relatedRequirementIds'].append(region['id'])
                    meta['requirementMatches'].append({'id': region['id'], 'label': region['estrutura'],
                        'type': region.get('tipo'), 'match': 'regional_context_only',
                        'visualValidation': 'pending_individual', 'separateStructure': False})
        if exact:
            primary = exact[0]
            meta['requirement'] = {'id': primary['id'], 'label': primary['estrutura'],
                                   'page': primary['pagina'], 'source': primary['fonte']}
        audit.append({'id': meta['id'], 'sourceFile': meta['sourceFile'], 'sourceNode': node_index,
                      'sourceWorldBounds': source_bounds, 'finite': True, 'indices_in_bounds': True,
                      'source_triangles_preserved': True, 'degenerate_triangles': int((areas == 0).sum()),
                      'normal_fallbacks': normal_fallbacks})
        geometry.append((meta, vertices, normals, faces.astype('<u4')))
    assert len({item[0]['id'] for item in geometry}) == len(geometry)
    gltf = {'asset': {'version': '2.0', 'generator': 'Local respiratory atlas extraction; source shapes preserved',
                     'copyright': 'Z-Anatomy / BodyParts3D contributors; CC BY-SA 4.0'},
            'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [], 'materials': [],
            'accessors': [], 'bufferViews': [], 'buffers': []}
    binary = bytearray()

    def put(array, kind, component, target):
        while len(binary) % 4: binary.append(0)
        start = len(binary); binary.extend(array.tobytes())
        view = len(gltf['bufferViews'])
        gltf['bufferViews'].append({'buffer': 0, 'byteOffset': start, 'byteLength': array.nbytes, 'target': target})
        index = len(gltf['accessors'])
        entry = {'bufferView': view, 'componentType': component, 'count': len(array), 'type': kind}
        if kind == 'VEC3': entry.update(min=array.min(0).tolist(), max=array.max(0).tolist())
        gltf['accessors'].append(entry)
        return index

    for index, (meta, vertices, normals, faces) in enumerate(geometry):
        positions = put(vertices, 'VEC3', 5126, 34962)
        normal_index = put(normals, 'VEC3', 5126, 34962)
        indices = put(faces.flatten(), 'SCALAR', 5125, 34963)
        color = [int(meta['color'][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        gltf['materials'].append({'name': meta['label'], 'doubleSided': True,
                                 'pbrMetallicRoughness': {'baseColorFactor': color + [1], 'metallicFactor': 0, 'roughnessFactor': .75}})
        gltf['nodes'].append({'name': meta['id'], 'mesh': index, 'extras': {'partId': meta['id']}})
        gltf['meshes'].append({'name': meta['sourceName'], 'primitives': [{'attributes': {'POSITION': positions, 'NORMAL': normal_index},
                                                                       'indices': indices, 'material': index, 'mode': 4}]})
        gltf['scenes'][0]['nodes'].append(index)
    gltf['buffers'].append({'byteLength': len(binary)})
    encoded = json.dumps(gltf, ensure_ascii=False, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    blob = struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary)) + struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary
    (OUT / 'model.glb').write_bytes(blob)
    limitations = [
        'Atlas anatômico idealizado: as cores são didáticas, não texturas de tecido.',
        'Pleura é uma superfície agregada: não individualiza folhetos, regiões ou recessos.',
        'Segmentos broncopulmonares, bronquíolos e alvéolos não são volumes independentes.',
        'Algumas peças do acervo original são marcadores/coleções; essas não foram exportadas como anatomia.',
        'Variações de ramificação brônquica pertencem ao espécime/atlas representado; não estabelecem padrão universal.',
        'Não há simulação de ventilação, fluxo aéreo, fonação ou movimentos musculares.',
        'Os vasos pulmonares representam trechos proximais; não individualizam a rede vascular segmentar nem completam todos os componentes das raízes pulmonares.',
    ]
    presets = [
        dict(id='exterior', label='Visão geral', groups=['pulmoes','arvore','laringe','respiracao'], direction=[0,.05,1], transparency=0,
             note='Comece pelos lobos, traqueia e diafragma. Use transparência para enxergar a árvore brônquica.'),
        dict(id='arvore', label='Árvore brônquica', groups=['pulmoes','arvore'], direction=[0,0,1], transparency=82,
             note='Cada ramo nomeado pode ser selecionado; ramos finos do mesmo território integram a peça.'),
        dict(id='laringe', label='Laringe', groups=['laringe','musculos_laringe','ligamentos_laringe'], direction=[.7,.1,1], transparency=0,
             note='Oculte a cartilagem tireóidea para examinar músculos e membranas internos.'),
        dict(id='vias_superiores', label='Vias superiores', groups=['nariz','seios','faringe','laringe'], direction=[1,0,.3], transparency=0,
             note='Vista lateral da cavidade nasal, regiões da faringe e laringe.'),
        dict(id='hioideos', label='Músculos hióideos', groups=['musculos_pescoco','laringe'], direction=[.7,.1,1], transparency=0,
             note='Músculos supra e infra-hióideos no registro original; o osso hioide ajuda na orientação.'),
        dict(id='pleuras', label='Pleura e pulmões', groups=['pleuras','pulmoes','respiracao'], direction=[.7,.1,1], transparency=70,
             note='A pleura é uma superfície única do acervo. Seus folhetos e recessos não são peças distintas.'),
        dict(id='torax', label='Relações torácicas', groups=['pulmoes','arvore','respiracao','contexto_torax'], direction=[.4,.1,1], transparency=72,
             note='Coração, costelas, esterno, pulmões e diafragma preservam o mesmo registro da fonte.'),
        dict(id='hilo', label='Hilos e vasos pulmonares', groups=['pulmoes','arvore','vascular_pulmonar'], direction=[0,.1,-1], transparency=85,
             note='Examine brônquios e vasos proximais com os lobos translúcidos. As raízes também contêm estruturas que esta cena não individualiza.'),
    ]
    sources = []
    for name in sorted(readers):
        provenance = ROOT / 'fontes/z_app' / (name + '.fbx.provenance.json')
        entry = json.loads(provenance.read_text()) if provenance.exists() else {'file': name + '.fbx'}
        sources.append(dict(name='Z-Anatomy · ' + name, license='CC BY-SA 4.0', **entry))
    catalog = dict(version=1, system='respiratory', title='Atlas respiratório', parts=[item[0] for item in geometry],
                   groups=GROUPS, presets=presets, translucencyGroups=['pulmoes','pleuras'], labelGroups=['pulmoes'],
                   mainGroups=['nariz','faringe','laringe','arvore','pulmoes','respiracao'],
                   model={'file':'model.glb','bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),
                          'parts':len(geometry),'triangles':sum(len(item[3]) for item in geometry)},
                   orientation={'x':'esquerda anatômica','y':'superior','z':'anterior',
                                'transform':{'source':'FBX world centimetres','center':CENTER.tolist(),'scale':SCALE},
                                'preserved':'Uma única transformação comum, sem ajuste por peça.'},
                   limitations=limitations, sources=sources)
    (OUT / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    (DOC / 'mesh_audit.json').write_text(json.dumps({'parts':audit,'source_triangle_count':catalog['model']['triangles'],
                                                   'display_transform':catalog['orientation']}, ensure_ascii=False, indent=2))
    (DOC / 'parts_manifest.json').write_text(json.dumps(catalog['parts'], ensure_ascii=False, indent=2))
    print(json.dumps(catalog['model'], indent=2))


if __name__ == '__main__': main()
