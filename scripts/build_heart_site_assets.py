"""Extract existing, positioned cardiac anatomy; do not synthesize anatomy.

The high resolution Blender surfaces and the app's vessel meshes share the
same source coordinate system: Blender (x,y,z) metres -> FBX (x,z,-y)*100.
All geometry receives the same final translation and uniform display scale.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ASSETS = SITE / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)

# English source names are kept in the exported metadata for traceability.
PARTS = [
 ('Right atrium', 'Átrio direito', 'camaras', '#9f615d', 'Recebe o retorno venoso sistêmico. A aurícula está incorporada à mesma peça.', '16'),
 ('Right ventricle', 'Ventrículo direito', 'camaras', '#ae7267', 'Ejeta sangue no tronco pulmonar. Use o corte ou a transparência para explorar o interior.', '20'),
 ('Left atrium', 'Átrio esquerdo', 'camaras', '#ac5159', 'Recebe as veias pulmonares. A aurícula está incorporada à mesma peça.', '18'),
 ('Left ventricle', 'Ventrículo esquerdo', 'camaras', '#943c49', 'Ejeta sangue na aorta. Suas camadas musculares não estão individualizadas nesta malha.', '21'),
 ('Ascending aorta', 'Aorta ascendente', 'grandes', '#bc5257', 'Segmento inicial da aorta disponível no modelo de origem.', '76'),
 ('Aortic arch', 'Arco da aorta', 'grandes', '#bc5257', 'O arco está presente; seus ramos para pescoço e membros não foram incluídos nesta cena cardíaca.', '84'),
 ('Pulmonary trunk', 'Tronco pulmonar', 'grandes', '#668797', 'Via de saída do ventrículo direito. As cores servem para distinguir as peças.', '30c'),
 ('Bifurcation of pulmonary trunk', 'Bifurcação do tronco pulmonar', 'grandes', '#668797', 'Peça de junção presente no arquivo de origem.', ''),
 ('Right pulmonary artery', 'Artéria pulmonar direita', 'grandes', '#688ba0', 'Segmento proximal disponível. Ramos dentro dos pulmões não fazem parte desta cena.', '30d'),
 ('Left pulmonary artery', 'Artéria pulmonar esquerda', 'grandes', '#688ba0', 'Segmento proximal disponível. Ramos dentro dos pulmões não fazem parte desta cena.', '30e'),
 ('Superior vena cava', 'Veia cava superior', 'grandes', '#637b9b', 'Retorno venoso para o átrio direito; a parede do óstio não é uma peça separada.', '30a'),
 ('Inferior vena cava (thoracic part)', 'Veia cava inferior · parte torácica', 'grandes', '#637b9b', 'Trecho torácico original, preservado até sua extremidade no arquivo de origem.', '30b'),
 ('Right superior pulmonary vein', 'Veia pulmonar superior direita', 'grandes', '#ce7876', 'Peça venosa original; a conexão e o óstio no átrio esquerdo ainda exigem revisão detalhada.', '30h'),
 ('Right inferior pulmonary vein', 'Veia pulmonar inferior direita', 'grandes', '#ce7876', 'Peça venosa original; a conexão e o óstio no átrio esquerdo ainda exigem revisão detalhada.', 'C15'),
 ('Left superior pulmonary vein', 'Veia pulmonar superior esquerda', 'grandes', '#ce7876', 'Peça venosa original; a conexão e o óstio no átrio esquerdo ainda exigem revisão detalhada.', '30f'),
 ('Left inferior pulmonary vein', 'Veia pulmonar inferior esquerda', 'grandes', '#ce7876', 'Peça venosa original; a conexão e o óstio no átrio esquerdo ainda exigem revisão detalhada.', '30g'),
 ('Right coronary artery', 'Artéria coronária direita', 'coronarias', '#dc8870', 'Malha arterial com ramificações. Cada ramo do roteiro precisa de identificação própria.', '81'),
 ('Right inferolateral branch of right coronary artery', 'Ramo inferolateral direito da coronária direita', 'coronarias', '#dc8870', 'Nome traduzido do arquivo original. A equivalência de cada ramo com o roteiro requer conferência.', '102'),
 ('Left coronary artery', 'Artéria coronária esquerda', 'coronarias', '#dc8870', 'Trecho inicial da coronária esquerda disponível no arquivo de origem.', '83'),
 ('Anterior interventricular artery', 'Ramo interventricular anterior', 'coronarias', '#dc8870', 'Peça arterial original. Explore sua relação com a face anterior dos ventrículos.', '103'),
 ('Circumflex artery of heart', 'Ramo circunflexo', 'coronarias', '#dc8870', 'Conjunto arterial original; alguns ramos permanecem unidos nesta mesma peça.', '104'),
 ('Septal branches of anterior interventricular artery', 'Ramos septais do interventricular anterior', 'coronarias', '#dc8870', 'Conjunto de ramos em uma única malha. Pode ficar encoberto pelas paredes ventriculares.', '103b'),
 ('Coronary sinus', 'Seio coronário', 'veias', '#7597b1', 'Explore pela vista posterior. A abertura no átrio direito não está individualizada.', '30k'),
 ('Great cardiac vein', 'Veia cardíaca magna', 'veias', '#7597b1', 'Peça venosa original, selecionável independentemente das artérias.', '106'),
 ('Middle cardiac vein', 'Veia cardíaca média', 'veias', '#7597b1', 'Explore sua relação com a face posterior do coração.', '111'),
 ("Inferior vein of left ventricle (//Posterior '')", 'Veia inferior do ventrículo esquerdo', 'veias', '#7597b1', 'Nome do modelo de origem: veia inferior, também indicada nele como posterior.', '110'),
 ('Inferior leaflet of right atrioventricular valve', 'Tricúspide · cúspide inferior/posterior', 'valvas', '#ead4af', 'Folheto com cordas incorporadas. O conjunto tricúspide desta cena está incompleto: falta a cúspide anterior.', '46b'),
 ('Septal leaflet of right atrioventricular valve', 'Tricúspide · cúspide septal', 'valvas', '#ead4af', 'Folheto com cordas incorporadas. O conjunto tricúspide desta cena está incompleto: falta a cúspide anterior.', '46c'),
 ('Posterior leaflet of left atrioventricular valve', 'Mitral · cúspide posterior', 'valvas', '#ead4af', 'Folheto com cordas incorporadas. A cúspide anterior ainda não está integrada a esta cena.', '58b'),
 ('Right coronary leaflet', 'Aórtica · válvula semilunar direita', 'valvas', '#efd5a7', 'Um dos três folhetos semilunares aórticos disponíveis. Não representa o anel fibroso.', '63a'),
 ('Left coronary leaflet', 'Aórtica · válvula semilunar esquerda', 'valvas', '#efd5a7', 'Um dos três folhetos semilunares aórticos disponíveis. Não representa o anel fibroso.', '63b'),
 ('Non-coronary leaflet', 'Aórtica · válvula semilunar posterior', 'valvas', '#efd5a7', 'Folheto não coronário. O nome original é preservado abaixo.', '63c'),
 ('Anterior semilunar leaflet of pulmonary valve', 'Pulmonar · válvula semilunar anterior', 'valvas', '#d9d7b6', 'Um dos três folhetos pulmonares disponíveis. Não representa o anel fibroso.', '53a'),
 ('Right semilunar leaflet of pulmonary valve', 'Pulmonar · válvula semilunar direita', 'valvas', '#d9d7b6', 'Um dos três folhetos pulmonares disponíveis. Não representa o anel fibroso.', '53b'),
 ('Left semilunar leaflet of pulmonary valve', 'Pulmonar · válvula semilunar esquerda', 'valvas', '#d9d7b6', 'Um dos três folhetos pulmonares disponíveis. Não representa o anel fibroso.', '53c'),
 ('Anterior papillary muscle of right ventricle', 'VD · músculo papilar anterior', 'papilares', '#cf9982', 'Músculo papilar original. As cordas que o alcançam pertencem às malhas dos folhetos.', '47'),
 ('Inferior papillary muscle of right ventricle', 'VD · músculo papilar inferior/posterior', 'papilares', '#cf9982', 'Terminologia inferior no arquivo de origem; conferir equivalência posterior no roteiro.', '48'),
 ('Septal papillary muscle of right ventricle', 'VD · músculo papilar septal', 'papilares', '#cf9982', 'Músculo papilar original, selecionável de modo independente.', '49'),
 ('Inferior papillary muscle of left ventricle', 'VE · músculo papilar inferior/posterior', 'papilares', '#cf9982', 'O outro grupo papilar esquerdo não está integrado nesta cena.', '60'),
]

raw = (ROOT / 'malhas/CardioVascular41.glb').read_bytes()
assert raw[:4] == b'glTF'
json_len, chunk_type = struct.unpack_from('<II', raw, 12)
assert chunk_type == 0x4e4f534a
gltf = json.loads(raw[20:20 + json_len])
bin_len, chunk_type = struct.unpack_from('<II', raw, 20 + json_len)
assert chunk_type == 0x004e4942
binary = raw[28 + json_len:28 + json_len + bin_len]
world = {}

def visit(index, parent):
    node = gltf['nodes'][index]
    # Assimp emitted matrix transforms; reject any unexpected TRS for safety.
    assert not any(k in node for k in ('translation', 'rotation', 'scale'))
    matrix = np.array(node.get('matrix', np.eye(4).flatten())).reshape(4, 4).T
    world[index] = parent @ matrix
    for child in node.get('children', []):
        visit(child, world[index])

for top in gltf['scenes'][gltf.get('scene', 0)]['nodes']:
    visit(top, np.eye(4))

def accessor(index):
    acc = gltf['accessors'][index]
    assert not acc.get('sparse')
    view = gltf['bufferViews'][acc['bufferView']]
    assert view['buffer'] == 0
    dim = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[acc['type']]
    dtype = np.dtype({5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[acc['componentType']])
    return np.ndarray((acc['count'], dim), dtype=dtype, buffer=binary,
                      offset=view.get('byteOffset', 0) + acc.get('byteOffset', 0),
                      strides=(view.get('byteStride', dim * dtype.itemsize), dtype.itemsize)).copy()

nodes_by_name = {n['name']: i for i, n in enumerate(gltf['nodes']) if 'mesh' in n}
high_res = {p['name']: p for p in json.loads((ROOT / 'malhas/heart_source/manifest.json').read_text())}
coverage = json.loads((ROOT / 'matriz_coracao.json').read_text())
requirements = {row['id']: row for row in coverage['alvos']}
geometry = []
alignment = []
center = np.array([2.0, 130.5, 2.0])
display_scale = 0.25

for num, (name, label, group, color, note, requirement_id) in enumerate(PARTS):
    node_id = nodes_by_name[name]
    node = gltf['nodes'][node_id]
    vertex_chunks, face_chunks, offset = [], [], 0
    for primitive in gltf['meshes'][node['mesh']]['primitives']:
        assert primitive.get('mode', 4) == 4
        vertices = accessor(primitive['attributes']['POSITION'])
        vertices = vertices @ world[node_id][:3, :3].T + world[node_id][:3, 3]
        faces = accessor(primitive['indices']).reshape(-1, 3).astype(np.uint32)
        if np.linalg.det(world[node_id][:3, :3]) < 0:
            faces = faces[:, [0, 2, 1]]
        vertex_chunks.append(vertices)
        face_chunks.append(faces + offset)
        offset += len(vertices)
    vertices, faces = np.concatenate(vertex_chunks), np.concatenate(face_chunks)
    origin = 'CardioVascular41.fbx'
    if name in high_res:
        higher = np.load(ROOT / 'malhas/heart_source' / high_res[name]['file'], allow_pickle=False)
        points = higher['vertices'][:, [0, 2, 1]] * [100, 100, -100]
        delta = float(np.max(np.abs(np.array([vertices.min(0), vertices.max(0)]) - np.array([points.min(0), points.max(0)]))))
        alignment.append({'name': name, 'bounding_box_difference_source_units': delta})
        # Compare source placement before substituting higher resolution geometry.
        assert delta < 0.18, (name, delta)
        vertices, faces = points, higher['faces'].astype(np.uint32)
        origin = 'Startup.blend'
    vertices = ((vertices - center) * display_scale).astype('<f4')
    assert np.isfinite(vertices).all() and np.max(np.abs(vertices)) < 10
    assert len(vertices) > 2 and len(faces) > 0 and faces.max() < len(vertices)
    face_normals = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]], vertices[faces[:, 2]] - vertices[faces[:, 0]])
    normals = np.zeros_like(vertices)
    for column in range(3):
        np.add.at(normals, faces[:, column], face_normals)
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths[:, None], 1e-12)
    source_requirement = requirements.get(requirement_id)
    meta = dict(id=f'heart_{num:02}', label=label, sourceName=name, group=group,
                color=color, note=note, sourceFile=origin, source='Z-Anatomy',
                license='CC BY-SA 4.0', sourceNode=node_id,
                requirement={'id': requirement_id, 'label': source_requirement['estrutura'], 'page': source_requirement['pagina'], 'source': source_requirement['fonte']} if source_requirement else None,
                vertices=len(vertices), triangles=len(faces),
                bounds=[vertices.min(0).tolist(), vertices.max(0).tolist()])
    geometry.append((meta, vertices, normals.astype('<f4'), faces.astype('<u4')))

# Write a small standards-compliant GLB with one selectable mesh per source object.
out = {'asset': {'version': '2.0', 'generator': 'Local cardiac extraction; existing Z-Anatomy geometry',
                  'copyright': 'Z-Anatomy; BodyParts3D / The Database Center for Life Science. CC BY-SA 4.0. See LICENSES.'},
       'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [],
       'accessors': [], 'bufferViews': [], 'buffers': [],
       'materials': [{'name': 'Recolorable anatomy', 'doubleSided': True,
                      'pbrMetallicRoughness': {'baseColorFactor': [1, 1, 1, 1], 'metallicFactor': 0, 'roughnessFactor': 0.6}}]}
chunks = bytearray()

def append_array(array, kind, component, target):
    while len(chunks) % 4:
        chunks.append(0)
    start = len(chunks)
    chunks.extend(array.tobytes())
    vi = len(out['bufferViews'])
    out['bufferViews'].append({'buffer': 0, 'byteOffset': start, 'byteLength': array.nbytes, 'target': target})
    ai = len(out['accessors'])
    a = {'bufferView': vi, 'componentType': component, 'count': len(array), 'type': kind}
    if kind == 'VEC3':
        a.update(min=array.min(0).tolist(), max=array.max(0).tolist())
    out['accessors'].append(a)
    return ai

for meta, vertices, normals, faces in geometry:
    pos = append_array(vertices, 'VEC3', 5126, 34962)
    nor = append_array(normals, 'VEC3', 5126, 34962)
    idx = append_array(faces.flatten(), 'SCALAR', 5125, 34963)
    n = len(out['nodes'])
    out['scenes'][0]['nodes'].append(n)
    out['nodes'].append({'name': meta['id'], 'mesh': n, 'extras': {'partId': meta['id'], 'sourceName': meta['sourceName']}})
    out['meshes'].append({'name': meta['label'], 'primitives': [{'attributes': {'POSITION': pos, 'NORMAL': nor}, 'indices': idx, 'material': 0, 'mode': 4}]})
out['buffers'] = [{'byteLength': len(chunks)}]
encoded = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode()
encoded += b' ' * (-len(encoded) % 4)
blob = (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(chunks)) +
        struct.pack('<II', len(encoded), 0x4e4f534a) + encoded +
        struct.pack('<II', len(chunks), 0x004e4942) + chunks)
(ASSETS / 'heart.glb').write_bytes(blob)
catalog = {
    'version': 1, 'parts': [p[0] for p in geometry],
    'model': {'parts': len(geometry), 'triangles': sum(len(p[3]) for p in geometry),
              'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest(),
              'synthetic_anatomical_parts': 0, 'individually_anatomically_validated': False},
    'orientation': {'xPositive': 'esquerda do corpo', 'yPositive': 'superior', 'zPositive': 'anterior'},
    'coverage': coverage['resumo'],
    'limitations': [
        'Faltam as cúspides anteriores da mitral e da tricúspide nesta montagem.',
        'Cordas tendíneas integram os folhetos; não são peças individualmente selecionáveis.',
        'Pericárdio, esqueleto fibroso e sistema de condução ainda não estão representados.',
        'Relevos finos, óstios e conexões entre peças precisam de revisão anatômica.',
        'O modelo isolado não demonstra toda a sintopia do coração.',
    ],
    'sources': [
        {'label': 'Z-Anatomy · modelo Blender', 'url': 'https://github.com/Z-Anatomy/Models-of-human-anatomy', 'revision': '7cc49aa8749632adcd564c0e75f096dc43f6a4b8'},
        {'label': 'Z-Anatomy · vasos da aplicação', 'url': 'https://github.com/LluisV/Z-Anatomy/tree/PC-Version/Resources/Models', 'revision': '6c7f9016bd5899ac8edafd31b9900c151df42ed6'},
        {'label': 'OpenStax · anatomia do coração', 'url': 'https://openstax.org/books/anatomy-and-physiology-2e/pages/19-1-heart-anatomy'},
    ],
}
(ASSETS / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
(ASSETS / 'alignment.json').write_text(json.dumps({'method': 'Shared source coordinates; common rigid axis change and uniform scale. No per-part warping or hand placement.', 'checks': alignment}, indent=2))

# Vendor the browser files, so the running app never needs a CDN or npm access.
vendor = SITE / 'vendor/three'
for rel in ['build/three.core.js', 'build/three.module.js', 'examples/jsm/controls/OrbitControls.js', 'examples/jsm/loaders/GLTFLoader.js', 'examples/jsm/utils/BufferGeometryUtils.js', 'examples/jsm/utils/SkeletonUtils.js', 'LICENSE']:
    dst = vendor / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SITE / 'node_modules/three' / rel, dst)

licenses = SITE / 'LICENSES'
licenses.mkdir(exist_ok=True)
shutil.copy2(ROOT / 'fontes/z_app/License.txt', licenses / 'Z-Anatomy-original.txt')
shutil.copy2(SITE / 'node_modules/three/LICENSE', licenses / 'Three-MIT.txt')
(licenses / 'NOTICE.txt').write_text('''Coração 3D local — protótipo de viabilidade

Geometria derivada de Z-Anatomy, the open source atlas of anatomy — CC BY-SA 4.0.
https://creativecommons.org/licenses/by-sa/4.0/
Créditos: Gauthier Kervyn (design, 3D, anatomia), Lluis Vinent (aplicação),
Kousaku Okubo / BodyParts3D, The Database Center for Life Science (modelo original).
A licença histórica pedida pelos arquivos Z-Anatomy atribui BodyParts3D sob
CC BY-SA 2.1 Japan; esse aviso é preservado em Z-Anatomy-original.txt.
O download atual e independente de BodyParts3D está sob CC BY 4.0, mas não
foi integrado a esta cena. A geometria derivada aqui permanece CC BY-SA 4.0.

Alterações: seleção de 39 peças cardíacas já existentes; conversão para GLB;
conversão comum de eixos e escala; normais calculadas; cores didáticas e
rótulos em português. Nenhuma nova estrutura anatômica foi gerada. Modelos
de ouvido e rim de outros autores não foram incluídos.
Os recortes e a transparência são efeitos de visualização, não novas malhas.

Three.js 0.186.1 — MIT. Cópia da licença em Three-MIT.txt.
Notas anatômicas: roteiro local e resumo de OpenStax, Anatomy and Physiology 2e,
19.1 Heart Anatomy. A cena ainda não é uma validação integral do roteiro.
''')
audit = SITE / 'auditoria'
audit.mkdir(exist_ok=True)
for name in ['auditoria.html', 'matriz_coracao.csv', 'matriz_coracao.json', 'RELATORIO.md', 'verificacao.json']:
    shutil.copy2(ROOT / name, audit / name)
(audit / 'evidencias').mkdir(exist_ok=True)
shutil.copy2(ROOT / 'evidencias/z_coracao_inspecao.png', audit / 'evidencias/z_coracao_inspecao.png')
print(json.dumps({'parts': len(geometry), 'triangles': catalog['model']['triangles'], 'glb_bytes': len(blob), 'max_alignment_bbox_delta': max(c['bounding_box_difference_source_units'] for c in alignment)}, indent=2))
