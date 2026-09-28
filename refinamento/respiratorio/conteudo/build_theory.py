"""Conteúdo autoral de revisão, ancorado nos materiais locais; não é gabarito de prova."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'site/assets/respiratory'
requirements=json.loads((OUT/'requirements.json').read_text())
catalog=json.loads((OUT/'catalog.json').read_text())
sources=json.loads((OUT/'practice-evidence.json').read_text())['sources']
sources.extend([
 {'id':'openstax_resp','label':'OpenStax — Organs and Structures of the Respiratory System','type':'reference','url':'https://openstax.org/books/anatomy-and-physiology-2e/pages/22-1-organs-and-structures-of-the-respiratory-system'},
 {'id':'openstax_mechanics','label':'OpenStax — The Process of Breathing','type':'reference','url':'https://openstax.org/books/anatomy-and-physiology-2e/pages/22-3-the-process-of-breathing'},
 {'id':'uams_nerves','label':'UAMS — Nerves of the Thorax','type':'reference','url':'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/nerve-tables/nerves-of-the-thorax/'}])
def refs(*pages,lecture=None,time=None,extra=None):
 r=[{'source':'respiratorio','page':p} for p in pages]
 if lecture:r.append({'source':lecture,'time':time})
 if extra:r.extend([{'source':x} if isinstance(x,str) else x for x in extra])
 return r
def ids(a,b=None):return [f'R{n:03d}' for n in range(a,(b or a)+1)]
def section(heading,paragraphs=None,bullets=None,table=None,references=None):
 s={'heading':heading,'paragraphs':paragraphs or [],'bullets':bullets or [],'references':references or []}
 if table:s['table']={'headers':table[0],'rows':table[1]}
 return s
def question(q,a,e,references):return {'question':q,'answer':a,'explanation':e,'references':references}
chapters=[]
def chapter(id,title,summary,objectives,sections,recall,targets):
 for n,q in enumerate(recall,1):q['id']=f'{id}_q{n:02d}'
 parts=[p['id'] for p in catalog['parts'] if set(targets)&set(p.get('requirementIds',[]))]
 chapters.append(dict(id=id,title=title,summary=summary,objectives=objectives,sections=sections,recall=recall,partIds=parts,requirementIds=targets))

chapter('resp_01','1. Caminho do ar e organização funcional',
 'Construa um mapa contínuo do nariz ao alvéolo e separe condução, ventilação, difusão e transporte de gases.',
 ['Descrever o trajeto do ar sem saltar regiões.','Localizar a transição entre zona condutora e respiratória.','Relacionar o sistema respiratório à circulação pulmonar.'],[
 section('Quatro processos que trabalham em sequência',[
  'Ventilação é o movimento de ar entre ambiente e pulmões. Difusão é a passagem de O₂ e CO₂ pela barreira alveolocapilar. O sangue transporta os gases entre pulmões e tecidos; as células utilizam O₂ no metabolismo. Portanto, movimentar ar e efetuar troca gasosa são etapas diferentes.',
  'Nos pulmões, o O₂ passa do ar alveolar para o sangue e o CO₂ faz o percurso inverso. Nos tecidos sistêmicos, a direção global se inverte. O fluxo sanguíneo precisa alcançar os alvéolos ventilados para que a troca contribua para a oxigenação.'],references=refs(3,4,5,125,lecture='R1',time='01:27–03:52')),
 section('O trajeto contínuo',bullets=[
  'Narinas → vestíbulo e cavidade nasal → cóanos → nasofaringe.',
  'Nasofaringe → orofaringe → laringofaringe → ádito e cavidade da laringe.',
  'Traqueia → brônquios principais → lobares → segmentares → ramificações menores → bronquíolos terminais.',
  'Bronquíolos respiratórios → ductos alveolares → sacos alveolares e alvéolos.'],references=refs(6,7,8,42,72,88,lecture='R3',time='02:44–06:29')),
 section('Duas classificações, duas perguntas',table=(['Classificação','O que separa','Referência para estudar'],[
  ['Topográfica','Vias superiores e inferiores','Na convenção da aula, nariz, cavidades e faringe/laringe compõem as vias superiores; a traqueia inicia as inferiores. Outras referências podem posicionar a laringe de modo diferente.'],
  ['Funcional','Zona condutora e zona respiratória','A condutora termina no bronquíolo terminal. A respiratória começa quando surgem alvéolos nas paredes dos bronquíolos respiratórios.'],
  ['Escala','Anatomia macroscópica e microanatomia','Um pulmão ou brônquio é reconhecível na peça; pneumócitos e barreira de difusão exigem imagem de outra escala.']]),references=refs(7,8,9,131,lecture='R1',time='08:10–09:06')),
 section('Reconhecer sem depender da cor',[
  'No modelo, siga conexões e posição. Uma cor é um recurso didático; não define a identidade anatômica. Ao ocultar o pulmão, a árvore brônquica aparece como um trajeto; ao recolocar os lobos, relacione cada ramo ao território que ventila.',
  'Os alvéolos não serão deduzidos de uma superfície pulmonar lisa. Para as estruturas microscópicas, use os slides de detalhe e diferencie explicitamente o esquema da geometria macroscópica.'],references=refs(8,92,93,131))
 ],[
 question('Qual é a última estrutura da zona condutora?','O bronquíolo terminal.','A presença de alvéolos na parede caracteriza o início da zona respiratória, nos bronquíolos respiratórios.',refs(8)),
 question('Ventilar um alvéolo garante que seu ar oxigene o sangue?','Não; também é necessário que haja perfusão e uma barreira adequada à difusão.','A ventilação leva ar; a circulação entrega sangue à superfície de troca.',refs(4,125)),
 question('Que abertura liga a cavidade nasal à nasofaringe?','Os cóanos.','As narinas comunicam o exterior com a entrada nasal; os cóanos são as aberturas posteriores.',refs(19,42)),
 question('Por que dois livros podem classificar a laringe de formas diferentes?','Porque a divisão superior/inferior depende da convenção topográfica usada.','Para esta revisão, mantenha a convenção da aula e não confunda essa divisão com condutora/respiratória.',refs(9,lecture='R1',time='08:10–09:06'))
 ],ids(42,44)+ids(104,118)+ids(192,198))

chapter('resp_02','2. Nariz: forma, paredes e mucosa',
 'Use o esqueleto e os limites da cavidade para entender como o nariz filtra, aquece, umidifica e permite a olfação.',
 ['Reconhecer nariz externo, septo e parede lateral.','Diferenciar concha, meato e cóano.','Relacionar mucosa respiratória, mucosa olfatória e vascularização.'],[
 section('Nariz externo e vestíbulo',[
  'A raiz é a região superior de implantação; o dorso segue até o ápice. As asas delimitam lateralmente as narinas. Ossos nasais e maxilas sustentam a parte superior; cartilagem septal, cartilagens laterais e alares sustentam a porção mais móvel.',
  'O vestíbulo fica imediatamente após a narina e mantém características de pele, incluindo vibrissas. A filtração inicial de partículas maiores ali é diferente da limpeza mucociliar das regiões mais profundas. Prócero, nasal, levantador do lábio superior e da asa do nariz e abaixador do septo participam da forma e movimentação local.'],references=refs(10,11,12,14,lecture='R2',time='00:03–02:15')),
 section('Paredes: use três referências',table=(['Referência','Componentes e relações','Como reconhecer'],[
  ['Septo nasal','Cartilagem do septo anteriormente; lâmina perpendicular do etmoide superiormente; vômer posteroinferiormente.','Parede medial que separa as cavidades direita e esquerda.'],
  ['Parede lateral','Conchas superior e média pertencem ao etmoide; a inferior é um osso próprio. Participam também maxila, lacrimal, palatino e esfenoide.','Saliências em prateleiras com espaços abaixo delas.'],
  ['Teto e assoalho','Região cribriforme do etmoide no teto; processos palatinos das maxilas e lâminas horizontais dos palatinos no palato duro.','Não confundir a crista galli, intracraniana, com uma concha nasal.']]),references=refs(16,17,18,19,lecture='R2',time='03:49–07:00')),
 section('Concha não é meato',[
  'Conchas são saliências revestidas por mucosa. Meatos são passagens situadas abaixo das conchas correspondentes. Essa organização amplia a superfície de contato do ar com a mucosa e cria trajetos para drenagem de seios e do ducto nasolacrimal.',
  'O meato superior fica abaixo da concha superior. O recesso esfenoetmoidal está acima e posteriormente a ela: são espaços distintos. Os cóanos são as aberturas posteriores; não são um quarto meato.'],references=refs(19,36)),
 section('Mucosa, vasos e nervos: forma explica função',[
  'A região respiratória ocupa a maior parte da cavidade: vasos aquecem o ar, secreções o umidificam e retêm partículas, e cílios ajudam a deslocar o muco para a faringe. A região olfatória é superior, próxima ao teto, à concha superior e ao septo adjacente. A olfação envolve o nervo olfatório; sensibilidade geral não é a mesma modalidade.',
  'O material destaca contribuições arteriais dos territórios carotídeos externo e interno e redes venosas nas conchas. A comunicação das veias faciais com vias profundas ajuda a explicar por que infecções da região nasal merecem atenção anatômica. Epistaxe significa sangramento nasal; rinorreia, escoamento de secreção; anosmia, perda da olfação.'],references=refs(20,24,25,26,27,30,31,33,lecture='R2',time='07:15–15:35'))
 ],[
 question('Quais são os três componentes principais do septo nasal?','Cartilagem septal, lâmina perpendicular do etmoide e vômer.','Eles ocupam predominantemente as regiões anterior, superior e posteroinferior, respectivamente.',refs(17)),
 question('Qual concha nasal é um osso independente?','A concha nasal inferior.','As conchas média e superior são partes do etmoide.',refs(18,19)),
 question('O espaço abaixo da concha média chama-se como?','Meato nasal médio.','Concha é a saliência; meato é o espaço de passagem abaixo dela.',refs(19,36)),
 question('Por que a mucosa nasal é tão vascularizada?','A vascularização ajuda a aquecer o ar inspirado.','Ela atua junto à umidificação e à retenção/remoção de partículas para condicionar o ar.',refs(20,26)),
 question('Vibrissas e cílios respiratórios são a mesma estrutura?','Não.','Vibrissas são pelos do vestíbulo; cílios são especializações celulares que participam do transporte do muco.',refs(14,20))
 ],ids(1,33)+ids(218,220))

chapter('resp_03','3. Seios paranasais e caminhos de drenagem',
 'Memorize cada seio junto de sua abertura e use a parede lateral nasal para reconstruir a drenagem.',
 ['Localizar seios frontal, maxilar, esfenoidal e células etmoidais.','Associar cada grupo ao meato ou recesso correto.','Explicar a diferença entre cavidade, óstio e via de drenagem.'],[
 section('Cavidades aéreas que se comunicam com o nariz',[
  'Os seios paranasais são cavidades nos ossos frontal, maxila, esfenoide e etmoide, revestidas por mucosa contínua com a nasal. Os etmoidais formam um conjunto de células, agrupadas em anteriores, médias e posteriores.',
  'Na peça ou no 3D, identificar o volume de um seio é apenas a primeira etapa. Sua relação com a cavidade nasal depende de uma abertura e de um trajeto de drenagem. Um volume fechado no modelo não demonstra que seu óstio esteja representado.'],references=refs(34,35,36,lecture='R2',time='15:35–19:42')),
 section('Mapa de drenagem que precisa ser recuperado de memória',table=(['Origem','Destino na cavidade nasal','Referência espacial'],[
  ['Seio frontal','Meato médio','Via do ducto frontonasal e região do infundíbulo; trajeto apresenta variações.'],
  ['Seio maxilar','Meato médio','Óstio na parede medial do seio, próximo à região do hiato semilunar.'],
  ['Células etmoidais anteriores','Meato médio','Região anterior do complexo de drenagem.'],
  ['Células etmoidais médias','Meato médio','Relação com a bolha etmoidal.'],
  ['Células etmoidais posteriores','Meato superior','Abaixo da concha superior.'],
  ['Seio esfenoidal','Recesso esfenoetmoidal','Acima/posteriormente à concha superior.'],
  ['Ducto nasolacrimal','Meato inferior','É uma via de drenagem lacrimal, não um seio paranasal.']]),references=refs(36,lecture='R2',time='17:07–18:31')),
 section('Bolha e hiato: reconhecer relações',[
  'A bolha etmoidal é uma saliência da parede lateral na região do meato médio, relacionada às células etmoidais médias. O hiato semilunar é uma fenda curva dessa mesma região. Ao estudar, procure primeiro concha média e meato médio, depois os relevos menores.',
  'Um óstio obstruído dificulta ventilação e depuração do seio correspondente. Essa relação espacial ajuda a entender sinusite sem reduzir o mecanismo a uma simples cavidade cheia: mucosa, drenagem e comunicação precisam ser consideradas.'],references=refs(36,37))
 ],[
 question('Quais grupos drenam para o meato médio?','Frontal, maxilar e células etmoidais anteriores e médias.','Organize quatro origens para um mesmo destino; depois estude o trajeto específico de cada uma.',refs(36)),
 question('Onde drena o seio esfenoidal?','No recesso esfenoetmoidal.','O recesso não é sinônimo de meato superior; o meato superior recebe células etmoidais posteriores.',refs(36)),
 question('Qual estrutura drena no meato inferior?','O ducto nasolacrimal.','A relação explica a comunicação entre drenagem lacrimal e cavidade nasal.',refs(36)),
 question('Por que localizar um seio no 3D não basta para aprender sua drenagem?','Porque volume, óstio e trajeto são elementos diferentes.','Confirme a abertura e seu destino em figura detalhada quando a malha representar apenas o volume.',refs(36))
 ],ids(22,24)+ids(34,41)+ids(221))

chapter('resp_04','4. Faringe: cruzamento entre ar e alimento',
 'Organize as três partes da faringe pelas estruturas anteriores e relacione músculos, tonsilas e comunicações.',
 ['Distinguir nasofaringe, orofaringe e laringofaringe.','Reconhecer o óstio da tuba e o anel tonsilar.','Explicar o papel dos constritores e músculos longitudinais.'],[
 section('Três partes, um tubo musculofascial',table=(['Parte','Relação anterior','Limite útil'],[
  ['Nasofaringe','Cavidade nasal, pelos cóanos','Superior ao palato mole.'],
  ['Orofaringe','Cavidade oral, pelo istmo das fauces','Posterior à boca, inferior ao palato mole.'],
  ['Laringofaringe','Laringe e seu ádito','Segue inferiormente ao esôfago, próximo à borda inferior da cricóidea/C6.']]),references=refs(41,42,43,lecture='R2',time='19:42–21:12')),
 section('Nasofaringe e orelha média',[
  'Na parede lateral da nasofaringe, localize o óstio faríngeo da tuba auditiva e o toro tubário. As pregas salpingofaríngea e salpingopalatina relacionam-se com esse relevo. A tonsila faríngea ocupa a região superior/posterior; as tonsilas tubárias ficam próximas aos óstios.',
  'A tuba comunica a nasofaringe com a orelha média e participa da equalização de pressão e da depuração de secreções. A frase do slide44 que menciona drenagem de perilinfa dos canais semicirculares está incorreta: esses canais pertencem à orelha interna.'],references=refs(44,45,extra=['openstax_ear'])),
 section('Tonsilas e deglutição',[
  'Tonsilas faríngea, tubárias, palatinas e lingual constituem tecido linfoide ao redor da entrada dos tratos respiratório e digestório. A hipertrofia da tonsila faríngea é o contexto anatômico da chamada adenoide; ela pode reduzir o espaço da nasofaringe.',
  'Durante a deglutição, a coordenação do palato mole, faringe e laringe direciona o bolo ao esôfago. A elevação do palato mole ajuda a separar a nasofaringe; a proteção laríngea envolve elevação e fechamento em vários níveis, e não somente a epiglote.'],references=refs(44,45,46,72,lecture='R2',time='23:26–25:07')),
 section('Músculos: estreitar e elevar',[
  'Os constritores superior, médio e inferior envolvem a faringe e participam do transporte do bolo por contrações coordenadas. Estilofaríngeo, salpingofaríngeo e palatofaríngeo seguem uma orientação longitudinal e participam da elevação/encurtamento faríngeo.',
  'A inervação motora é predominantemente vagal pelo plexo faríngeo. Guarde a exceção: o estilofaríngeo recebe o glossofaríngeo (IX). O IX também tem papel sensitivo relevante na orofaringe; não resuma todo o plexo a uma única função ou a um único nervo.'],references=refs(47,48,49,51,lecture='R2',time='25:07–27:29',extra=['uams_nerves']))
 ],[
 question('O que separa topograficamente nasofaringe de orofaringe?','O plano do palato mole.','A nasofaringe fica superior; a orofaringe comunica-se com a boca inferiormente.',refs(42)),
 question('A tuba auditiva comunica a nasofaringe com qual compartimento do ouvido?','Com a orelha média.','Ela não é uma via de drenagem dos líquidos da orelha interna.',refs(44,extra=['openstax_ear'])),
 question('Quais grupos formam o anel tonsilar?','Tonsilas faríngea, tubárias, palatinas e lingual.','A distribuição circunda a entrada das vias respiratória e digestória.',refs(44,45)),
 question('Qual músculo longitudinal da faringe é a exceção à inervação vagal predominante?','O estilofaríngeo, inervado pelo glossofaríngeo.','Separar ação muscular, sensibilidade e nervo motor evita a generalização da tabela do plexo.',refs(48,51,extra=['uams_nerves']))
 ],ids(42,60))

chapter('resp_05','5. Esqueleto da laringe e suas articulações',
 'Monte a laringe por camadas: hioide, cartilagens, membranas, ligamentos e pontos de inserção.',
 ['Identificar as cartilagens ímpares e pares.','Reconhecer processos aritenóideos e partes da cricóidea.','Relacionar articulações aos movimentos das pregas.'],[
 section('Um mapa de cima para baixo',[
  'O hioide fica superior à laringe e conecta-se à tireóidea pela membrana tireo-hióidea. A tireóidea forma uma proteção anterior e lateral; a cricóidea situa-se inferiormente e forma um anel completo. A traqueia continua abaixo, ligada à cricóidea pelo ligamento cricotraqueal.',
  'A epiglote relaciona-se com a entrada laríngea, posteriormente à raiz da língua. As aritenóideas apoiam-se sobre a parte posterior da cricóidea; as corniculadas ficam sobre seus ápices. As cuneiformes situam-se nas pregas ariepiglóticas.'],references=refs(53,54,55,56,57,58,64)),
 section('Cartilagens que você precisa distinguir',table=(['Conjunto','Cartilagens','Acidentes práticos'],[
  ['Ímpares','Tireóidea, cricóidea e epiglótica','Na tireóidea: lâminas, proeminência, linha oblíqua, incisuras e cornos. Na cricóidea: arco anterior estreito e lâmina posterior alta.'],
  ['Pares','Aritenóideas, corniculadas e cuneiformes','Nas aritenóideas, processo vocal aponta anteriormente e recebe o ligamento vocal; processo muscular é lateral e recebe músculos.'],
  ['Epiglote e língua','Epiglote, pregas glossoepiglóticas e valéculas','O pecíolo é a extremidade inferior; as valéculas são depressões entre raiz da língua e epiglote, não furos na cartilagem.']]),references=refs(53,55,56,57,58,61,63,64)),
 section('Movimento depende da articulação',[
  'Nas articulações cricotireóideas, o movimento relativo da tireóidea e da cricóidea muda a tensão das pregas vocais. Nas cricoaritenóideas, rotação e deslizamento das aritenóideas alteram a posição dos processos vocais, aproximando ou afastando as pregas.',
  'O processo vocal e o processo muscular pertencem à mesma cartilagem, mas exercem papéis mecânicos diferentes. Para fixar, identifique a cricóidea posteriormente, encontre a base da aritenóidea e só então indique seus processos.'],references=refs(57,58,64,extra=[{'source':'utah_larynx','page':79}])) ,
 section('Membranas e ligamentos: relações que orientam',bullets=[
  'Membrana tireo-hióidea: entre hioide e tireóidea, reforçada por ligamentos mediano e laterais.',
  'O ramo interno do laríngeo superior acompanha vasos laríngeos superiores através dessa membrana.',
  'Ligamento cricotireóideo mediano: região anterior entre tireóidea e cricóidea; diferencie-o do cricotraqueal, abaixo da cricóidea.',
  'Ligamentos tireoepiglótico e hioepiglótico relacionam a epiglote à tireóidea e ao hioide.'],references=refs(56,57,62,65))
 ],[
 question('Quais são as três cartilagens laríngeas ímpares?','Tireóidea, cricóidea e epiglótica.','Aritenóideas, corniculadas e cuneiformes são pares.',refs(53)),
 question('Onde a cricóidea é mais alta?','Posteriormente, na lâmina.','Seu arco anterior é mais estreito; essa assimetria permite orientar a cartilagem isolada.',refs(57,58)),
 question('Qual processo aritenóideo recebe o ligamento vocal?','O processo vocal.','O processo muscular recebe inserções musculares e permite transferir força para o movimento da cartilagem.',refs(64)),
 question('O espaço entre língua e epiglote chama-se como?','Valécula epiglótica.','As pregas glossoepiglóticas delimitam as depressões; a valécula não é um orifício da epiglote.',refs(63)),
 question('Que membrana é atravessada pelo ramo interno do laríngeo superior?','A membrana tireo-hióidea.','Essa relação permite associar esqueleto, vasos e inervação em uma mesma vista.',refs(65))
 ],ids(61,89)+ids(217))

chapter('resp_06','6. Laringe: respiração, proteção e voz',
 'Aprenda o efeito de cada movimento antes de decorar o músculo e o nervo que o produzem.',
 ['Diferenciar pregas vocais e vestibulares, glote e rima.','Relacionar músculos intrínsecos à abertura e tensão das pregas.','Distinguir laríngeo superior, recorrente e inferior.'],[
 section('Cavidade e pregas',[
  'O vestíbulo estende-se do ádito até as pregas vestibulares. As pregas vocais ficam inferiores às vestibulares; entre cada prega vestibular e vocal existe um ventrículo laríngeo. Inferiormente às pregas vocais está a cavidade infraglótica, que continua com a traqueia.',
  'Glote compreende as pregas vocais e a rima da glote. A rima é a abertura entre as pregas; não use os dois termos como sinônimos absolutos. Em vista superior, relacione epiglote anterior, aritenóideas posteriores e pregas que convergem anteriormente.'],references=refs(72,73,extra=['uams_head'])),
 section('Ação muscular: o movimento é a pista',table=(['Músculo/grupo','Efeito principal','Associação útil'],[
  ['Cricoaritenóideo posterior','Abduz as pregas vocais','Abre a rima para passagem de ar; único par abdutor.'],
  ['Cricoaritenóideo lateral e aritenóideos','Aduzem pregas/aritenóideas','Aproximam os elementos durante fechamento e fonação.'],
  ['Cricotireóideo','Alonga e aumenta a tensão das pregas','Não deve ser decorado apenas como adutor.'],
  ['Tireoaritenóideo','Encurta e reduz a tensão, com participação na aproximação','Ajusta posição e tensão junto aos demais músculos.'],
  ['Vocal','Ajuste fino local da tensão','Integra a massa muscular da prega vocal.']]),references=refs(66,70,extra=[{'source':'utah_larynx','page':81}])) ,
 section('Fonação e fechamento protetor',[
  'Na respiração, a abertura varia conforme a demanda de fluxo. Para a fonação, as pregas são aproximadas e o fluxo expiratório sustenta sua oscilação. Músculos posicionam e tensionam as pregas; não contraem uma vez por cada vibração sonora. A altura da voz depende, entre outros fatores, de comprimento, tensão e massa vibrante.',
  'A proteção da via aérea combina elevação da laringe, aproximação de pregas e aritenóideas e movimento da epiglote. Os músculos extrínsecos movimentam o conjunto: supra-hióideos e alguns músculos faríngeos participam da elevação; infra-hióideos estabilizam ou deprimem conforme suas fixações.'],references=refs(66,67,68,70,72,lecture='R2',time='35:02–40:48')),
 section('Inervação: guarde a exceção motora',table=(['Nervo','Papel para esta revisão','Relação'],[
  ['Laríngeo superior, ramo interno','Sensibilidade da mucosa superior às pregas vocais','Atravessa a membrana tireo-hióidea.'],
  ['Laríngeo superior, ramo externo','Motor para o cricotireóideo','Exceção entre os músculos intrínsecos.'],
  ['Laríngeo recorrente → laríngeo inferior','Demais músculos intrínsecos e sensibilidade abaixo das pregas','Direito contorna subclávia direita; esquerdo contorna arco aórtico.']]),references=refs(81,extra=[{'source':'utah_larynx','page':83}])) ,
 section('Irrigação e relações com a tireoide',[
  'A artéria laríngea superior deriva da tireóidea superior; a inferior relaciona-se à tireóidea inferior. O trajeto acompanha regiões onde também passam os nervos laríngeos. Localizar artérias, membrana e nervos no mesmo plano é mais útil do que decorar listas isoladas.',
  'Para treino prático, diferencie a cartilagem tireóidea da glândula tireoide. A semelhança do nome não implica que sejam o mesmo órgão ou o mesmo tipo de tecido.'],references=refs(79,80,81))
 ],[
 question('Qual prega está mais superior: vocal ou vestibular?','A vestibular.','O ventrículo localiza-se entre a vestibular superior e a vocal inferior.',refs(72)),
 question('Rima da glote e glote significam exatamente a mesma coisa?','Não: a rima é a abertura; a glote inclui pregas vocais e rima.','Essa distinção evita identificar uma prega como se fosse apenas um espaço.',refs(72,extra=['uams_head'])),
 question('Qual músculo abre as pregas vocais por abdução?','O cricoaritenóideo posterior.','Sua posição posterior na cricóidea ajuda a reconhecê-lo na prática.',refs(66)),
 question('Qual é a exceção à inervação pelo laríngeo inferior dos músculos intrínsecos?','O cricotireóideo, inervado pelo ramo externo do laríngeo superior.','Relacione esta exceção à função de tensionar as pregas.',refs(81)),
 question('Por que o recorrente esquerdo desce mais no tórax?','Porque contorna o arco aórtico.','O direito contorna a subclávia direita; os dois trajetos são assimétricos.',refs(81)),
 question('O músculo vocal produz cada vibração por uma contração rápida?','Não.','A atividade muscular regula postura e tensão; o fluxo de ar sustenta a oscilação das pregas aproximadas.',refs(70,72))
 ],ids(90,103)+ids(202,216)+ids(222))

chapter('resp_07','7. Traqueia e brônquios principais',
 'Use parede posterior, carina e ângulo de ramificação para orientar a via aérea central.',
 ['Orientar a traqueia e identificar suas partes.','Explicar a função do suporte cartilaginoso e músculo traqueal.','Comparar brônquios principais direito e esquerdo.'],[
 section('Traqueia: suporte anterior, flexibilidade posterior',[
  'A traqueia continua a laringe inferiormente à cricóidea. Possui uma parte cervical e outra torácica. As cartilagens incompletas posteriormente sustentam a luz; entre elas há ligamentos anulares. A parede membranácea posterior contém o músculo traqueal e relaciona-se com o esôfago.',
  'O formato permite manter a via aérea aberta e acomodar movimentos e mudanças de calibre. Para orientar uma peça isolada, procure primeiro a interrupção posterior dos anéis e depois a bifurcação inferior.'],references=refs(84,85,86,lecture='R3',time='00:00–01:36')),
 section('Carina e nível da bifurcação',[
  'A carina é a crista interna na bifurcação traqueal, entre as entradas dos brônquios principais. É um relevo dentro da luz, não uma peça externa separada. Um modelo que mostre apenas a superfície externa da bifurcação pode não demonstrá-la.',
  'Use como referência usual a origem em C6 e a bifurcação próxima do ângulo esternal/plano T4–T5 no adulto. A posição muda com respiração, postura e indivíduo; o T6 do slide84 não deve ser memorizado como nível fixo para todas as situações.'],references=refs(84,85,extra=['uams_thorax'])),
 section('Assimetria dos brônquios principais',table=(['Característica','Direito','Esquerdo'],[
  ['Calibre e comprimento','Mais largo e mais curto','Mais estreito e mais longo'],
  ['Direção','Mais vertical','Mais oblíquo'],
  ['Divisão lobar','Superior, médio e inferior','Superior e inferior'],
  ['Relação de estudo','Após a saída do lobar superior, segue o brônquio intermédio','Percorre um trajeto mais longo até o hilo']]),references=refs(89,90,91,lecture='R3',time='02:44–04:11')),
 section('Da cartilagem à parede bronquiolar',[
  'A ramificação reduz progressivamente o calibre das vias. Brônquios intrapulmonares apresentam suporte cartilaginoso distribuído em placas; bronquíolos não têm cartilagem. A musculatura lisa passa a ser uma referência importante para entender variação de calibre e resistência ao fluxo.',
  'A maior verticalidade do principal direito ajuda a explicar a tendência de corpos estranhos aspirados seguirem para esse lado. É uma tendência anatômica, não uma regra absoluta para toda posição ou faixa etária.'],references=refs(89,95,98,99,lecture='R3',time='05:14–06:29'))
 ],[
 question('Que estrutura vizinha ajuda a orientar a parede posterior da traqueia?','O esôfago.','Ele fica posteriormente; a parede membranácea traqueal é a região sem fechamento cartilaginoso completo.',refs(85,86)),
 question('A carina é um ramo da árvore brônquica?','Não; é a crista interna da bifurcação.','Os ramos são os brônquios principais; a carina separa suas entradas.',refs(85)),
 question('Qual principal é mais curto, largo e vertical?','O direito.','Essas características favorecem a entrada de material aspirado no lado direito.',refs(89)),
 question('A ausência de cartilagem ajuda a distinguir que parte da via aérea?','Os bronquíolos.','Brônquios possuem suporte cartilaginoso; bronquíolos mantêm parede com musculatura lisa, mas sem cartilagem.',refs(95,98))
 ],ids(104,118))

chapter('resp_08','8. Lobos e segmentos broncopulmonares',
 'Relacione hierarquia brônquica a territórios pulmonares e estude a convenção segmentar apresentada pela professora.',
 ['Passar de principal para lobar e segmentar.','Nomear os segmentos de cada lobo.','Reconhecer variações de agrupamento no pulmão esquerdo.'],[
 section('Principal → lobar → segmentar',[
  'Cada brônquio principal dirige-se a um pulmão; brônquios lobares ventilam lobos; brônquios segmentares seguem para territórios broncopulmonares. Segmento é território de parênquima, e brônquio segmentar é a via que o ventila. Eles não são a mesma estrutura.',
  'Um segmento recebe um brônquio segmentar e um ramo arterial pulmonar. Veias pulmonares percorrem planos entre territórios; por isso, não descreva todo o conjunto vascular de um segmento como inteiramente isolado. A organização segmentar fornece referências para localização e ressecção anatômica.'],references=refs(92,93,95,lecture='R3',time='04:11–05:14')),
 section('Pulmão direito: dez segmentos no esquema da aula',table=(['Lobo','Código usual','Nome'],[
  ['Superior','S1 / B1','Apical'],['Superior','S2 / B2','Posterior'],['Superior','S3 / B3','Anterior'],
  ['Médio','S4 / B4','Lateral'],['Médio','S5 / B5','Medial'],
  ['Inferior','S6 / B6','Superior'],['Inferior','S7 / B7','Basal medial'],['Inferior','S8 / B8','Basal anterior'],['Inferior','S9 / B9','Basal lateral'],['Inferior','S10 / B10','Basal posterior']]),references=refs(92)),
 section('Pulmão esquerdo: siga a convenção do slide93',table=(['Lobo','Código usual','Nome'],[
  ['Superior','S1+2 / B1+2','Apicoposterior'],['Superior','S3 / B3','Anterior'],['Superior, língula','S4 / B4','Lingular superior'],['Superior, língula','S5 / B5','Lingular inferior'],
  ['Inferior','S6 / B6','Superior'],['Inferior','S7 / B7','Basal medial'],['Inferior','S8 / B8','Basal anterior'],['Inferior','S9 / B9','Basal lateral'],['Inferior','S10 / B10','Basal posterior']]),references=refs(93)),
 section('Como lidar com variação e treinar',[
  'O slide esquerdo agrupa apical e posterior e mantém basais medial e anterior separados. Outros atlas mostram um basal anteromedial combinado; não transforme a contagem de um atlas em correção automática da figura da aula. S designa o território segmentar; B designa o brônquio correspondente.',
  'No 3D, isole o lobo, oculte seu parênquima e siga o ramo lobar até os segmentares. Depois tente nomear os ramos sem rótulos. A malha da árvore mostra trajetos; os limites volumétricos completos dos segmentos exigem representação própria e não podem ser inferidos só por cor do brônquio.'],references=refs(92,93,95))
 ],[
 question('Quais são os segmentos do lobo médio direito?','Lateral e medial.','Correspondem usualmente a S4/B4 e S5/B5.',refs(92)),
 question('A língula pertence a qual lobo?','Ao lobo superior esquerdo.','Seus segmentos são lingular superior e lingular inferior; ela não é um terceiro lobo esquerdo.',refs(93,104)),
 question('O segmento superior do lobo inferior é um dos segmentos basais?','Não.','Ele é S6; o grupo basal corresponde aos territórios inferiores seguintes.',refs(92,93)),
 question('Que união segmentar aparece no lobo superior esquerdo da aula?','Apical e posterior formam o apicoposterior.','O esquema ainda mantém os segmentos basais medial e anterior separados.',refs(93)),
 question('B3 e S3 designam exatamente a mesma coisa?','Não: B3 é o brônquio; S3 é o território segmentar.','A conexão funcional entre via e território não elimina a diferença de estrutura.',refs(92,93))
 ],ids(113,142))

chapter('resp_09','9. Pulmões: superfícies, fissuras, hilo e raiz',
 'Oriente cada pulmão pela forma global e confirme o lado por fissuras e relações mediastinais.',
 ['Diferenciar faces, ápice, base e margens.','Reconhecer lobos e fissuras.','Separar hilo de raiz e identificar impressões dos órgãos vizinhos.'],[
 section('Orientação antes de nomear',[
  'O ápice aponta superiormente; a base, ou face diafragmática, é inferior e côncava. A face costal acompanha a parede torácica; a mediastinal volta-se medialmente e contém o hilo. Margens delimitam transições entre superfícies.',
  'Comece por medial/lateral e superior/inferior. Só depois use fissuras e impressões para decidir direita/esquerda. Uma vista rodada pode inverter a aparência da tela, mas não a lateralidade anatômica.'],references=refs(101,102,103,104,105)),
 section('Lobos e fissuras',table=(['Pulmão','Lobos','Fissuras e marcos'],[
  ['Direito','Superior, médio e inferior','Horizontal separa superior de médio; oblíqua separa inferior dos outros dois.'],
  ['Esquerdo','Superior e inferior','Oblíqua separa os dois; incisura cardíaca e língula pertencem à região do lobo superior.']]),references=refs(103,104)),
 section('Hilo é uma região; raiz é um conjunto',[
  'Hilo é a área da face mediastinal por onde estruturas entram e saem. Raiz, ou pedículo, é o conjunto que liga o pulmão ao mediastino: brônquio, artéria e veias pulmonares, vasos brônquicos, linfáticos/linfonodos e nervos, envolvidos pela continuidade pleural.',
  'A figura105 aproxima os termos, mas a distinção ajuda na prova prática: apontar o hilo significa localizar a região; descrever a raiz exige reconhecer seus componentes. Um brônquio isolado não constitui todo o pedículo.'],references=refs(105,106,107,lecture='R4',time='03:00–05:16')),
 section('A superfície guarda a forma dos vizinhos',table=(['Lado','Relações destacadas no material','Como estudar'],[
  ['Direito','Veia cava superior, cava inferior, arco da ázigos e esôfago','Localize cada sulco em relação ao hilo, ao ápice e à base.'],
  ['Esquerdo','Arco aórtico, subclávia, esôfago e impressão cardíaca','Relacione a impressão maior ao coração e diferencie incisura de impressão cardíaca.']]),references=refs(108,109,117))
 ],[
 question('Qual fissura existe apenas no pulmão direito típico?','A fissura horizontal.','Ela separa o lobo superior do médio.',refs(103)),
 question('A base pulmonar corresponde a qual face?','À face diafragmática.','Sua concavidade acompanha a cúpula do diafragma.',refs(103,105)),
 question('Qual a diferença entre hilo e raiz?','Hilo é a região de passagem; raiz é o conjunto de estruturas que passa por ela.','Essa distinção permite descrever localização e composição sem confundi-las.',refs(105,106)),
 question('Língula e incisura cardíaca são a mesma coisa?','Não.','A incisura é uma escavação da margem anterior; a língula é a projeção do lobo superior esquerdo inferior a essa região.',refs(104)),
 question('Por que o pulmão direito apresenta um sulco para a ázigos?','Porque o arco da veia ázigos relaciona-se com sua região mediastinal superior à raiz.','Sulcos são pistas das relações, e não vasos contidos dentro do parênquima.',refs(108))
 ],ids(138,160))

chapter('resp_10','10. Pleura: continuidade, recessos e sensibilidade',
 'Visualize uma membrana contínua com porções visceral e parietal e um espaço potencial entre elas.',
 ['Distinguir folhetos e partes da pleura parietal.','Localizar recessos e ligamento pulmonar.','Relacionar inervação à dor pleural.'],[
 section('Do pulmão à parede',[
  'A pleura visceral adere ao pulmão e acompanha as fissuras. A parietal reveste internamente a parede torácica, o diafragma e a face lateral do mediastino. Os folhetos tornam-se contínuos na região da raiz.',
  'Entre eles, a cavidade pleural é um espaço potencial com pequena quantidade de líquido, que permite deslizamento. Não é um compartimento normalmente cheio de ar. A separação gráfica de camadas em um atlas é um recurso para mostrar essa relação.'],references=refs(110,111,112,lecture='R4',time='05:16–07:40')),
 section('Partes da pleura parietal',table=(['Parte','Contato','Elemento associado'],[
  ['Costal','Face interna da parede torácica','Fáscia endotorácica entre pleura e parede.'],
  ['Diafragmática','Face superior do diafragma','Fáscia frenicopleural mencionada no material.'],
  ['Mediastinal','Faces laterais do mediastino','Continuidade na raiz e em suas reflexões.'],
  ['Cervical/cúpula','Prolongamento superior na raiz do pescoço','Membrana suprapleural, ou fáscia de Sibson, como reforço.']]),references=refs(113,114,115,116)),
 section('Recessos e ligamento pulmonar',[
  'Os recessos são regiões de reflexão pleural disponíveis para expansão do pulmão. O costodiafragmático está entre pleuras costal e diafragmática; o costomediastinal, entre costal e mediastinal. Uma fissura entre lobos não é um recesso pleural.',
  'O ligamento pulmonar prolonga inferiormente a bainha pleural da raiz como uma dupla prega. É uma continuidade da reflexão pleural, e não um cordão ligamentar rígido. A frase do slide117 sobre “dobra da pleura visceral” precisa ser interpretada junto à continuidade dos folhetos na raiz.'],references=refs(117,118,extra=['uams_thorax'])),
 section('Dor, líquido e movimento',[
  'A pleura parietal tem sensibilidade somática: nervos intercostais suprem a parte costal e a periferia diafragmática; o frênico supre a mediastinal e a região central diafragmática. A visceral recebe fibras autonômicas pelo plexo pulmonar e não apresenta a mesma sensibilidade dolorosa somática da parietal.',
  'Líquido pleural excessivo pode acumular-se em regiões dependentes, incluindo recessos, e limitar a expansão. Para a prova, associe localização, folheto e nervo; as figuras de procedimentos servem aqui para reconhecer relações anatômicas.'],references=refs(119,120,127,128,lecture='R4',time='16:45–17:14'))
 ],[
 question('Qual folheto entra nas fissuras pulmonares?','A pleura visceral.','Ela acompanha a superfície do pulmão, incluindo superfícies interlobares.',refs(112)),
 question('Que duas partes formam o recesso costodiafragmático?','Pleuras parietais costal e diafragmática.','O nome expressa a reflexão entre as superfícies; não é uma fissura pulmonar.',refs(118)),
 question('Onde fica o ligamento pulmonar?','Inferiormente à raiz do pulmão.','É uma dupla prega pleural que continua a bainha da raiz.',refs(117)),
 question('Qual nervo participa da sensibilidade da pleura mediastinal?','O nervo frênico.','Intercostais e frênico repartem territórios da pleura parietal.',refs(128)),
 question('O espaço pleural normal contém ar?','Não; é um espaço potencial com uma película de líquido.','Ar nesse compartimento modifica o acoplamento entre pulmão e parede, como ocorre no pneumotórax.',refs(110,111))
 ],ids(161,172)+ids(182,183))

chapter('resp_11','11. Circulação, linfa e nervos dos pulmões',
 'Separe circulação de troca, circulação nutritiva, drenagem linfática e controle autonômico.',
 ['Comparar artérias/veias pulmonares e brônquicas.','Reconstruir a drenagem pelos principais linfonodos.','Diferenciar controle dos brônquios de comando dos músculos ventilatórios.'],[
 section('Duas circulações que se encontram',table=(['Sistema','Trajeto principal','Função'],[
  ['Pulmonar','Ventrículo direito → tronco/artérias pulmonares → capilares alveolares → veias pulmonares → átrio esquerdo','Conduzir sangue à superfície de troca gasosa.'],
  ['Brônquico','Ramos da circulação sistêmica, principalmente ligados à aorta torácica e suas variações','Nutrir paredes brônquicas e tecidos de suporte; contribui para pleura visceral e estruturas da raiz.']]),references=refs(123,124,125,126,lecture='R4',time='12:31–14:54')),
 section('Artéria e veia não são nomes de oxigenação',[
  'Artéria conduz sangue para fora do coração; veia, em direção ao coração. Assim, artérias pulmonares levam sangue relativamente pobre em O₂ aos pulmões, e veias pulmonares retornam sangue oxigenado ao átrio esquerdo. Cor vermelha/azul é uma convenção de desenho.',
  'A drenagem da circulação brônquica é compartilhada: parte segue por veias brônquicas sistêmicas e parte alcança veias pulmonares. Não memorize uma correspondência simples de toda artéria brônquica com uma única veia brônquica.'],references=refs(123,124,126)),
 section('Drenagem linfática: dos plexos à raiz',[
  'O plexo superficial está próximo da pleura visceral; o profundo acompanha estruturas broncovasculares. A linfa segue para linfonodos broncopulmonares, ou hilares, e depois para grupos traqueobronquiais e paratraqueais, alcançando troncos broncomediastinais.',
  'A rede tem conexões e variações; a sequência é um mapa de estudo, não uma série de tubos obrigatoriamente isolados. A pleura parietal segue drenagem relacionada à parede torácica, ao mediastino e à região cervical, conforme o território.'],references=refs(129,130,lecture='R4',time='17:14–18:39')),
 section('Autonômico nos brônquios; somático na bomba ventilatória',[
  'Os plexos pulmonares anterior e posterior recebem componentes vagais e simpáticos. Na síntese da aula, ação parassimpática favorece broncoconstrição e secreção; ativação simpática/adrenérgica favorece broncodilatação. Isso modifica a via aérea, não substitui os movimentos da caixa torácica.',
  'O diafragma recebe comando motor pelos nervos frênicos; os músculos intercostais, pelos nervos intercostais. Diferencie esse controle somático dos músculos esqueléticos do controle autonômico da musculatura lisa e das glândulas da árvore brônquica.'],references=refs(99,127,128,lecture='R4',time='14:54–17:14'))
 ],[
 question('Qual circulação fornece sangue aos capilares de troca alveolar?','A pulmonar.','A circulação brônquica tem função nutritiva para paredes e estruturas de suporte.',refs(123,125,126)),
 question('Por que a artéria pulmonar transporta sangue pobre em O₂ e ainda é uma artéria?','Porque sai do coração.','O critério artéria/veia é a direção do fluxo em relação ao coração.',refs(126)),
 question('Quais linfonodos recebem destaque na raiz do pulmão?','Os broncopulmonares, também chamados hilares.','Eles se relacionam às vias que seguem para grupos traqueobronquiais e paratraqueais.',refs(129)),
 question('O vago é o principal nervo motor do diafragma?','Não; o comando motor do diafragma é frênico.','O vago participa do controle autonômico broncopulmonar.',refs(127)),
 question('Que efeito sobre o calibre brônquico é associado ao parassimpático na aula?','Broncoconstrição.','O material também associa a ação vagal ao aumento da secreção glandular.',refs(99,127))
 ],ids(173,191)+ids(199,201))

chapter('resp_12','12. Alvéolos, surfactante e mecânica ventilatória',
 'Feche o caminho entre estrutura microscópica, propriedades do pulmão e movimentos da parede torácica.',
 ['Relacionar pneumócitos I e II às funções alveolares.','Explicar o efeito do surfactante.','Reconstruir as mudanças de volume e pressão durante a respiração.'],[
 section('Superfície fina e estável para troca',[
  'Pneumócitos tipo I são células delgadas que revestem grande parte da superfície de troca. Pneumócitos tipo II produzem surfactante e participam da manutenção do epitélio alveolar. A barreira alveolocapilar inclui o epitélio alveolar, a interface de membranas basais e o endotélio capilar.',
  'A espessura reduzida favorece difusão, mas o alvéolo também precisa permanecer aberto. A superfície úmida gera tensão superficial; o surfactante reduz essa tensão e contribui para a estabilidade, especialmente quando o volume alveolar diminui.'],references=refs(125,131,132,lecture='R4',time='18:39–20:32')),
 section('Imaturidade pulmonar',[
  'Na prematuridade, produção ou disponibilidade insuficiente de surfactante pode favorecer colapso alveolar, reduzir complacência e aumentar o esforço necessário para ventilar. O mecanismo básico é dificuldade de manter/reabrir unidades de troca; não é uma tendência primária de todos os alvéolos a romperem.',
  'O material também relaciona a ventilação neonatal à geometria das costelas, à complacência da parede e à maturação muscular. Esses fatores atuam em conjunto; não basta transportar diretamente a mecânica de um tórax adulto para o recém-nascido.'],references=refs(133,141,142,lecture='R4',time='24:31–25:57')),
 section('Volume muda primeiro; o gradiente move o ar',table=(['Etapa','Volume e músculos','Pressão alveolar e fluxo'],[
  ['Inspiração tranquila','Diafragma contrai e desce; tórax expande com participação dos intercostais externos.','Pressão alveolar cai transitoriamente abaixo da atmosférica; ar entra.'],
  ['Fim da inspiração','O volume atingiu o nível inspirado.','As pressões se igualam e o fluxo cessa, mesmo com volume aumentado.'],
  ['Expiração tranquila','Relaxamento inspiratório e recuo elástico reduzem o volume.','Pressão alveolar fica transitoriamente acima da atmosférica; ar sai.'],
  ['Expiração forçada','Músculos abdominais e componentes expiratórios da parede torácica contribuem ativamente.','O aumento de pressão favorece saída de ar, limitado também pelo calibre da via.']]),references=refs(135,136,138,139,140,lecture='R4',time='20:32–24:31')),
 section('Duas pressões que não devem ser confundidas',[
  'Pressão alveolar é a do ar dentro dos alvéolos e determina o fluxo em relação à atmosfera. Pressão intrapleural refere-se ao espaço pleural e, na respiração tranquila normal, é subatmosférica. A diferença entre pressão alveolar e intrapleural contribui para manter o pulmão distendido.',
  'O líquido pleural permite deslizamento e transmite o movimento da parede ao pulmão. Quando o tórax expande, o pulmão acompanha essa expansão; o aumento de volume reduz a pressão alveolar e atrai ar. Não descreva a inspiração como entrada de ar que primeiro empurra e expande o tórax.'],references=refs(110,135,136,extra=['openstax_mechanics'])) ,
 section('Um roteiro de revisão em três escalas',bullets=[
  'Macroscopia: mostre diafragma, intercostais, pulmões e pleuras; explique que elementos se movem.',
  'Via aérea: siga traqueia, brônquios e bronquíolos; relacione calibre à passagem de ar.',
  'Microanatomia: reconheça alvéolo, capilar, pneumócitos e surfactante em figura; explique difusão e estabilidade.',
  'Feche os rótulos e explique a cadeia: contração → aumento de volume → queda de pressão alveolar → entrada de ar.'],references=refs(8,125,131,136,138))
 ],[
 question('Qual pneumócito produz surfactante?','O tipo II.','O tipo I é especialmente delgado e ocupa grande parte da superfície de troca.',refs(131)),
 question('Como o surfactante facilita a ventilação?','Reduz a tensão superficial e favorece a estabilidade alveolar.','Isso reduz a tendência ao colapso e o trabalho para manter/reabrir os alvéolos.',refs(131,133)),
 question('Na inspiração, a pressão alveolar fica momentaneamente maior ou menor que a atmosférica?','Menor.','A diferença de pressão permite que o ar entre; o aumento de volume torácico/pulmonar precede esse fluxo.',refs(136)),
 question('A expiração tranquila exige contração intensa dos músculos expiratórios?','Não.','Ela decorre principalmente do relaxamento inspiratório e do recuo elástico; expiração forçada recruta músculos adicionais.',refs(138)),
 question('No fim da inspiração, por que o fluxo para mesmo com o pulmão expandido?','Porque a pressão alveolar se iguala à atmosférica.','Fluxo depende do gradiente de pressão, não apenas do volume existente.',refs(136)),
 question('Qual é a consequência básica de surfactante insuficiente no pulmão imaturo?','Maior tendência ao colapso alveolar e menor complacência.','O mecanismo não deve ser reduzido a ruptura alveolar, como pode sugerir uma leitura literal da transcrição automática.',refs(133))
 ],ids(192,201)+ids(161,166))

data={'version':1,'system':'respiratory','title':'Sistema respiratório — teoria conectada à prática','sources':sources,'chapters':chapters,
 'reviewStatus':'Síntese autoral revisada com slides, trechos ASR localizados e fontes institucionais para conflitos; não é transcrição integral nem gabarito oficial.',
 'limitations':['O roteiro respiratório oficial da Carmem não foi localizado. A seleção principal deriva dos slides de 144 páginas; IDs R### são editoriais.','Timestamps localizam trechos em transcrições automáticas. Não houve revisão integral do áudio e as falas não foram tratadas como autoridade contra a anatomia.','As questões são exercícios originais de recuperação ativa, não questões oficiais da prova.','Variações de segmentação, posição e dimensões exigem atenção à convenção usada; cores do modelo são recursos de estudo.','Associação de uma aula ou capítulo a uma malha não certifica sua fidelidade anatômica. Estruturas sem representação adequada devem ser estudadas na figura indicada.']}
(OUT/'theory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Chapters',len(chapters),'sections',sum(len(c['sections']) for c in chapters),'recall',sum(len(c['recall']) for c in chapters))
