"""
Corelain — Party Wall area pages (MKT-01 "township pages" + "local authority page").

Run from CRADAR/:  python3 src/seo/townships.py
It writes:
  src/html/party-wall-surveyors/<area>.html  one page per focus area
  src/html/party-wall-surveyors/<borough>.html one hub per borough with focus areas
  src/html/partials/pw-areas.html             "Areas we cover" strip (all pages)
  src/seo/sitemap.xml                         every indexable URL
  src/seo/llms.txt                            block between the AREAS markers

Each page carries facts that are specific to the area (postcode, council,
conservation areas, housing, typical projects) so the pages are not
near-duplicates. Keep the facts checkable: designations come from each council's
own conservation area list (Trafford Council; Stockport's open data CSVs).
Everything that varies with the local authority — council name, planning register,
ISO region — belongs in BOROUGHS, not in an `if borough ==` test.
The area list must match FOCUS ids in src/js/data/areas.js.
"""
import html
import json
import re
from pathlib import Path

# Party Wall questions are shared with the main FAQ (src/data/faq-templates.json)
TEMPLATES = json.loads((Path(__file__).resolve().parents[1] / 'data' / 'faq-templates.json').read_text())
CHEV = ('<svg class="cr-faq__chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6l6 -6"/></svg>')

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / 'src/html/party-wall-surveyors'
AREAS_PARTIAL = ROOT / 'src/html/partials/pw-areas.html'
SITEMAP = ROOT / 'src/seo/sitemap.xml'
LLMS = ROOT / 'src/seo/llms.txt'

PW_URL = 'https://www.corelain.com/party-wall-surveyor-manchester'
ENQUIRY = PW_URL + '#partywall-enquiry'
TRAFFORD_PLANNING = 'https://pa.trafford.gov.uk/online-applications/'
WARRINGTON_PLANNING = 'https://www.warrington.gov.uk/planning'
STOCKPORT_PLANNING = 'https://planning.stockport.gov.uk/PlanningData-live/'

# Everything that changes with the local authority. A borough listed here gets its
# own hub page; areas carry the council name, planning register and ISO region from it.
BOROUGHS = {
    'Trafford': dict(council='Trafford Council', planning=TRAFFORD_PLANNING, region='GB-TRF',
                     address_region='Greater Manchester',
                     lead='Corelain\'s Party Wall surveyors cover the whole of Trafford, from Old Trafford, Stretford '
                          'and Urmston to Timperley, Hale, Hale Barns and the villages around Dunham Massey. Choose '
                          'your area for local advice on notices, awards and the projects we see most.'),
    'Stockport': dict(council='Stockport Metropolitan Borough Council', planning=STOCKPORT_PLANNING, region='GB-SKP',
                      address_region='Greater Manchester',
                      lead='Corelain\'s Party Wall surveyors cover the whole of Stockport, from the Heatons and Cheadle '
                           'to Offerton, Hazel Grove, Bramhall and Marple. Choose your area for local advice on notices, '
                           'awards and the projects we see most.'),
    'Warrington': dict(council='Warrington Borough Council', planning=WARRINGTON_PLANNING, region='GB-WRT',
                       address_region='Cheshire',
                       lead='Corelain\'s Party Wall surveyors cover Warrington.'),
}
HUB = lambda borough: '/party-wall-surveyors/' + borough.lower()

# id, name, postcode, borough, geo (lat, lng), intro, housing, projects, conservation, notes, extra FAQ
AREAS = [
    dict(id='old-trafford', name='Old Trafford', pc='M16', borough='Trafford', geo=(53.4600, -2.2790),
         intro='Old Trafford is one of Trafford\'s most densely built neighbourhoods, with long Victorian and Edwardian terraces either side of Chester Road. Almost every house shares a party wall, so loft conversions, rear extensions and flat conversions here nearly always need a notice.',
         housing='Terraced streets make up most of the housing, with apartment blocks along Chester Road and Trafford Wharfside and interwar semi-detached pockets around Seymour Park. Terraces and flats together accounted for about nine in ten sales recorded over the last three years, so shared walls are the norm.',
         projects=['Loft conversions', 'Single-storey rear extensions', 'Flat and HMO conversions', 'Chimney breast removal'],
         conservation=['Empress Conservation Area (Chester Road / Empress Street)'],
         notes='Trafford\'s 2018 HMO Article 4 direction covers Old Trafford, so a small house-share conversion needs planning permission as well as any party wall notices.',
         faq=[('Does converting an Old Trafford terrace into flats need a party wall notice?',
               'Usually. Splitting a terraced house normally means new floors, sound insulation and steel bearing into the party wall, which is work under section 2 of the Act and needs two months\' notice to each adjoining owner.')]),
    dict(id='stretford', name='Stretford', pc='M32', borough='Trafford', geo=(53.4466, -2.3086),
         intro='Stretford\'s Victorian and Edwardian terraces and interwar semi-detached streets share party walls almost everywhere, so rear extensions and loft conversions here usually involve the Party Wall Act.',
         housing='Long runs of terraced houses around the town centre and Edge Lane, with 1930s semi-detached homes further out. Most houses share at least one party wall, and many rear gardens meet along a party fence wall.',
         projects=['Loft conversions with steel beams', 'Single-storey rear extensions', 'Kitchen side returns', 'Chimney breast removal'],
         conservation=['Longford Park Conservation Area'],
         notes='Stretford sits on the Metrolink Altrincham line, close to the Old Trafford regeneration area.',
         faq=[('Are party wall notices common in Stretford?',
               'Yes. Most Stretford homes are terraced or semi-detached, so loft conversions, chimney breast removal and rear extensions usually involve work to a party wall or excavation near a neighbour\'s foundations.')]),
    dict(id='sale', name='Sale', pc='M33', borough='Trafford', geo=(53.4246, -2.3226),
         intro='Sale combines Victorian and Edwardian terraces near the Bridgewater Canal with large interwar semi-detached estates, so loft conversions and two-storey extensions here often need a party wall notice.',
         housing='Victorian and Edwardian terraces near the town centre and canal, and extensive 1930s semi-detached streets towards Brooklands and Ashton upon Mersey.',
         projects=['Loft conversions', 'Two-storey side extensions', 'Rear kitchen extensions', 'Basement and cellar conversions'],
         conservation=['Brogden Grove Conservation Area', 'Ashton-on-Mersey Village Conservation Area'],
         notes='The Bridgewater Canal runs through the centre of Sale.',
         faq=[('Does a side extension on a semi-detached house in Sale need a party wall notice?',
               'Often. A side extension on a 1930s semi usually needs new foundations close to the neighbour\'s house, and may build a wall on the boundary line, which brings in sections 1 and 6 of the Act.')]),
    dict(id='hale-barns', name='Hale Barns', pc='WA15', borough='Trafford', geo=(53.3700, -2.3060),
         intro='Hale Barns is mostly large detached homes on generous plots. Even with no shared wall, deep foundations, basements and replacement houses near the boundary often fall under section 6 of the Party Wall Act.',
         housing='Large detached houses, many rebuilt or heavily extended, on wide plots. Party walls are rare, but neighbouring buildings are often within 3 to 6 metres of new foundations.',
         projects=['Replacement dwellings', 'Basements', 'Two-storey extensions', 'Garages and outbuildings near the boundary'],
         conservation=[],
         notes='No conservation area of its own; the South Hale and Ashley Heath conservation areas are in neighbouring Hale.',
         faq=[('Do detached houses in Hale Barns need party wall notices?',
               'They can. Section 6 of the Act covers excavation within 3 metres of a neighbour\'s building, or within 6 metres for deeper foundations, whether or not the houses share a wall. Basements and replacement houses often trigger it.')]),
    dict(id='hale', name='Hale', pc='WA15', borough='Trafford', geo=(53.3786, -2.3483),
         intro='Hale\'s Victorian and Edwardian houses, many inside conservation areas, are often extended with basements and large rear extensions that need careful party wall planning.',
         housing='Substantial Victorian and Edwardian semi-detached houses around Hale station and village, with later infill. Many sit inside one of three conservation areas.',
         projects=['Basements', 'Large rear extensions', 'Loft conversions', 'Boundary walls'],
         conservation=['Hale Station Conservation Area', 'South Hale Conservation Area', 'Ashley Heath Conservation Area'],
         notes='Conservation area rules add planning steps, but they do not replace the Party Wall Act.',
         faq=[('Does being in a Hale conservation area change the party wall process?',
               'No. Conservation area consent and planning rules are separate from the Party Wall Act. If the work is notifiable you still need to serve notice, even with planning permission in place.')]),
    dict(id='timperley', name='Timperley', pc='WA15', borough='Trafford', geo=(53.3970, -2.3240),
         intro='Timperley is a large interwar and post-war suburb of semi-detached houses. Side extensions, rear extensions and loft conversions on a semi almost always involve the party wall itself or excavation close to the neighbour\'s foundations.',
         housing='Mostly 1930s and post-war semi-detached houses across Timperley Central and Timperley North, with terraces near the village and the Metrolink stop and newer flats on infill plots. Semi-detached homes were more than half of all sales recorded over the last three years.',
         projects=['Two-storey side extensions', 'Loft conversions with steel beams', 'Rear kitchen extensions', 'Garage conversions'],
         conservation=[],
         notes='No conservation area in Timperley itself; the nearest Trafford designations are the Altrincham ones, a little over a mile away.',
         faq=[('Do I need a party wall notice to convert a garage in Timperley?',
               'Often yes. Many Timperley semis have a garage against the boundary or attached to the neighbour\'s, so cutting a new opening, raising the wall or underpinning it is notifiable work under section 2 of the Act.')]),
    dict(id='carrington', name='Carrington', pc='M31', borough='Trafford', geo=(53.4361, -2.3946),
         intro='Carrington is changing fast, with new housing planned around the village. Building next to existing homes, and extending older houses in the village, can both bring in the Party Wall Act.',
         housing='A small village with older cottages and terraces, surrounded by former industrial land and Carrington Moss. New housing is planned under the New Carrington allocation in the Places for Everyone plan.',
         projects=['Rear extensions', 'Loft conversions', 'Building next to existing homes', 'Excavation for new foundations'],
         conservation=[],
         notes='Large new developments must serve notices on existing neighbours where their excavation or boundary walls come close.',
         faq=[('Do new housing developments in Carrington have to serve party wall notices?',
               'Yes, where their work is notifiable. A developer digging foundations within 3 or 6 metres of an existing home, or building on the boundary, must serve notice on the owner like anyone else.')]),
    dict(id='partington', name='Partington', pc='M31', borough='Trafford', geo=(53.4194, -2.4265),
         intro='Partington grew rapidly in the 1960s and 1970s as an overspill town, so most homes are semi-detached or terraced and share a party wall with at least one neighbour.',
         housing='Post-war semi-detached and terraced houses from the town\'s 1960s and 1970s expansion, plus newer estates. Shared party walls are the norm.',
         projects=['Single-storey rear extensions', 'Loft conversions', 'Porches and side extensions', 'Chimney breast removal'],
         conservation=[],
         notes='Partington sits between the Manchester Ship Canal and Carrington Moss.',
         faq=[('Does a rear extension on a Partington semi need a party wall notice?',
               'Usually. Rear extensions on semi-detached houses normally need foundations close to the neighbour\'s, and often a wall on the boundary line, so sections 1 and 6 apply.')]),
    dict(id='dunham-massey', name='Dunham Massey', pc='WA14', borough='Trafford', geo=(53.3836, -2.3916),
         intro='Around the National Trust\'s Dunham Massey estate, historic cottages and farm buildings sit in conservation areas and the Green Belt, so extensions need planning, heritage and party wall advice together.',
         housing='Historic cottages, farmhouses and converted farm buildings, often attached, around Dunham Town and Dunham Woodhouses, with larger homes on the edge of Altrincham.',
         projects=['Barn and outbuilding conversions', 'Rear extensions to cottages', 'Repairs to shared walls', 'Underpinning'],
         conservation=['Dunham Town Conservation Area', 'Dunham Woodhouses Conservation Area'],
         notes='Much of the area is Green Belt, which limits the size of extensions.',
         faq=[('Do repairs to an old shared wall in Dunham Massey need a party wall notice?',
               'Often. Repairing, underpinning or rebuilding a party wall is work under section 2 of the Act, and needs two months\' notice to the neighbour unless they agree in writing.')]),
    dict(id='warburton', name='Warburton', pc='WA13', borough='Trafford', geo=(53.4005, -2.4549),
         intro='Warburton is a small rural village in the Green Belt with a historic core. Attached cottages and old boundary walls mean that even modest works can involve the Party Wall Act.',
         housing='Historic cottages, farmhouses and a small number of newer homes along Bent Lane and Paddock Lane, with the village core in a conservation area.',
         projects=['Cottage extensions', 'Barn conversions', 'Rebuilding boundary walls', 'Underpinning'],
         conservation=['Warburton Village Conservation Area'],
         notes='The village is in the Green Belt, south of the Manchester Ship Canal and the Warburton toll bridge.',
         faq=[('Is a garden boundary wall covered by the Party Wall Act in Warburton?',
               'It can be. A wall standing astride the boundary and separating two gardens is a party fence wall, so raising, rebuilding or underpinning it needs notice.')]),
    dict(id='urmston', name='Urmston', pc='M41', borough='Trafford', geo=(53.4487, -2.3540),
         intro='Urmston\'s Edwardian terraces and interwar semis share party walls street after street, making loft conversions and rear extensions the most common reasons for a party wall notice here.',
         housing='Edwardian and Victorian terraces near the town centre and station, interwar semi-detached houses towards Flixton and Davyhulme, and some post-war estates.',
         projects=['Loft conversions', 'Rear and side return extensions', 'Chimney breast removal', 'Structural alterations'],
         conservation=[],
         notes='No conservation area in Urmston itself; Flixton Village Conservation Area is next door.',
         faq=[('Does removing a chimney breast in an Urmston terrace need a party wall notice?',
               'Usually. A chimney breast on a party wall is part of that wall, so removing it is work under section 2 and needs two months\' notice unless the neighbour agrees in writing.')]),
    # ── Stockport ──────────────────────────────────────────────────────────────
    # Conservation areas and Article 4 directions come from Stockport Council's own
    # open data (Conservation_Areas_Stockport.csv, Article4_Dataset_Stockport.csv).
    # faq_only: these pages carry their own full question set, so the shared
    # Party Wall templates are not appended (they would repeat the same ground).
    dict(id='heaton-moor', name='Heaton Moor', pc='SK4', borough='Stockport', geo=(53.4227, -2.1843), faq_only=True,
         intro="Heaton Moor is a popular residential area north of Stockport, known for its Victorian character and established residential streets. We provide Party Wall advice to building owners and adjoining owners across Heaton Moor and the surrounding area.",
         housing="Heaton Moor has a mix of terraced, semi-detached and detached homes, including many older properties alongside later housing. Extensions, loft conversions and alterations are common types of work that can bring the Party Wall etc. Act 1996 into consideration.",
         projects=['Loft conversions', 'Rear and side extensions', 'Structural alterations', 'Adjacent excavations'],
         conservation=['Heaton Moor Conservation Area (designated 1989)', 'Mauldeth Road Conservation Area (designated 1989)'],
         notes="Article 4 Directions apply within parts of the Heaton Moor and Mauldeth Road Conservation Areas, meaning some works that would otherwise be permitted development may require planning permission. Party Wall requirements are separate and depend on the proposed works.",
         faq=[
             ('Do I need a Party Wall Notice for an extension in Heaton Moor?',
              'A Party Wall Notice may be required if the extension involves building a new wall on or astride the boundary, carrying out works to an existing party wall, or excavating close to a neighbouring building and below the level of its foundations. Whether notice is required depends on the design, location and depth of the proposed works.'),
             ('Does a loft conversion in Heaton Moor need a Party Wall Notice?',
              'Not every loft conversion requires notice. However, notice is commonly required where the works involve cutting into a party wall to insert steel beams or padstones, raising a party wall or carrying out other structural alterations to the party structure.'),
             ('I have received a Party Wall Notice in Heaton Moor. What should I do?',
              'Read the notice carefully and check what works are proposed. You can consent in writing or dissent. If a dispute arises, you can agree to the appointment of one Agreed Surveyor or appoint your own Party Wall Surveyor.'),
             ('Do I need a Party Wall agreement in Heaton Moor?',
              '“Party wall agreement” is a commonly used term, but it is not a specific document under the Party Wall etc. Act 1996. Where notifiable work is proposed, a Party Wall Notice is served. The adjoining owner can consent in writing or, if a dispute arises, the appointed surveyor or surveyors can resolve matters through a Party Wall Award.'),
             ('Should I consent to a Party Wall Notice?',
              "That depends on the proposed works and whether you are comfortable with the information provided. Before consenting, you can ask for further details about the works. Consent does not remove the building owner's responsibility for damage caused by the notifiable works."),
             ("What happens if I don't respond to a Party Wall Notice?",
              'For a Party Structure Notice, if you do not consent within 14 days, a dispute is deemed to have arisen under the Act. The surveyor appointment process can then begin. The precise procedure depends on the type of notice served.'),
             ('Do I need my own Party Wall Surveyor?',
              "Not necessarily. Where a dispute arises, you and the building owner can agree to appoint one Agreed Surveyor, or each owner can appoint a separate surveyor. An appointed Party Wall Surveyor's role is to act impartially under the Act rather than simply represent one owner's interests."),
             ("Who pays the Party Wall Surveyor's fees?",
              "Where the works are solely for the building owner's benefit, the building owner will normally pay the reasonable costs of the Party Wall process, including the adjoining owner's surveyor where a separate surveyor is reasonably appointed. The surveyors can determine responsibility for costs where circumstances differ."),
             ('What is a Party Wall Award?',
              'A Party Wall Award is the document made by the appointed surveyor or surveyors where a dispute has arisen. It sets out the works covered by the Award and how certain Party Wall matters are to be dealt with, which can include access, working arrangements and making good damage.'),
             ('What is a Schedule of Condition?',
              'A Schedule of Condition records the condition of the adjoining property before the notifiable works begin, usually with written descriptions and photographs. It provides a useful record of existing cracks and defects if damage is alleged during or after the works.'),
             ("What happens if my neighbour's building work damages my property?",
              'Report the damage promptly and keep photographs or other evidence. Where damage has resulted from works carried out under the Act, the building owner may be required to make good the damage or, in relevant circumstances, provide compensation. A pre-works Schedule of Condition can help establish whether damage is new.'),
             ("Can I stop my neighbour's extension using the Party Wall Act?",
              'The Party Wall etc. Act 1996 does not normally give an adjoining owner the right to prevent lawful building work simply because they object to it. Instead, the Act provides a process for certain works to proceed while protecting the interests of adjoining owners. Planning permission and Party Wall requirements are separate matters.'),
         ]),
    dict(id='cheadle', name='Cheadle', pc='SK8', borough='Stockport', geo=(53.3920, -2.2004), faq_only=True,
         intro="Cheadle runs from the old village centre out towards Gatley, with Victorian cottages and terraces alongside substantial areas of interwar semi-detached housing. The area has an established suburban character, with older properties concentrated around the historic centre and larger residential streets extending outwards.",
         housing="Cheadle has a mix of terraced, semi-detached and detached housing, with many properties positioned relatively close to their neighbours. Shared party walls are common within the terraced and semi-detached housing, while extensions can also involve excavation close to neighbouring buildings. This means Party Wall matters can arise from both alterations to existing shared structures and new extension works.",
         projects=['Single-storey rear extensions', 'Loft conversions', 'Two-storey side extensions', 'Garage conversions'],
         conservation=['Cheadle Village Conservation Area (designated 1974)', 'Gatley Village Conservation Area (designated 1979)', 'Brooklyn Crescent Conservation Area (designated 1979)'],
         notes="Article 4 Directions apply in parts of Cheadle Village and Brooklyn Crescent, restricting certain permitted development rights. This means planning permission may be required for some alterations that would otherwise be permitted development.",
         faq=[
             ('I have received a Party Wall Notice in Cheadle. What should I do?',
              'Read the notice carefully and check what works are proposed. You can consent to the works or dissent. If a dispute arises, you can agree with the building owner to appoint one Agreed Surveyor, or appoint your own Party Wall Surveyor.'),
             ('Should I consent or dissent to a Party Wall Notice?',
              'There is no single answer that suits every property. Before responding, make sure you understand the proposed works and how they may affect your property. If you consent, the works can proceed without a Party Wall Award. If you dissent, the Party Wall surveyor process is used to resolve the dispute and an Award can be made.'),
             ("What happens if I don't respond to a Party Wall Notice?",
              'For Party Structure and qualifying excavation notices, if you do not consent within 14 days, a dispute is deemed to have arisen. The surveyor appointment process can then follow. The procedure is different for certain Line of Junction notices.'),
             ('Can I appoint my own Party Wall Surveyor?',
              "Yes. If a dispute has arisen, you can appoint your own Party Wall Surveyor, or you and the building owner can jointly appoint one Agreed Surveyor. An appointed surveyor has a statutory role under the Party Wall etc. Act 1996 and is not simply there to represent one owner's interests."),
             ('Who pays for my Party Wall Surveyor if my neighbour is doing the work?',
              "Where the works are solely for the building owner's benefit, the building owner will normally be responsible for the reasonable costs of the Party Wall process, including reasonable fees for the adjoining owner's surveyor. The allocation of costs can vary depending on the circumstances and who benefits from the works."),
             ('What is a Schedule of Condition and should I have one?',
              "A Schedule of Condition records the condition of your property before the notifiable works begin, normally using written descriptions and photographs. It provides a useful record of existing cracks and defects if damage is alleged during or after your neighbour's building work."),
             ("What happens if my neighbour's building work damages my property?",
              'Record the damage and notify the relevant Party Wall Surveyor promptly. Where damage has resulted from works carried out under the Act, the building owner may be required to make good the damage or provide compensation. A pre-works Schedule of Condition can help establish whether damage is new.'),
             ('What if my neighbour starts work without serving a Party Wall Notice?',
              'If your neighbour has started work that you believe should have been notified under the Party Wall etc. Act 1996, take advice promptly. Depending on the circumstances, an adjoining owner may need to consider legal remedies, including seeking an injunction before the notifiable work progresses further.'),
             ('Do I need a Party Wall Notice for a rear extension in Cheadle?',
              'A Party Wall Notice may be required if the extension involves building at the boundary, carrying out work to an existing party wall, or excavating close to a neighbouring building and below the level of its foundations. Whether notice is required depends on the position and design of the proposed extension.'),
             ('Do side or wraparound extensions in Cheadle need a Party Wall Notice?',
              'They can. Side and wraparound extensions may involve building at the boundary or excavating new foundations close to a neighbouring building. Depending on the design and position of the works, notices under Sections 1 and/or 6 of the Party Wall etc. Act 1996 may be required.'),
             ('Does a loft conversion in Cheadle need a Party Wall Notice?',
              'Not every loft conversion requires notice. A Party Wall Notice may be required where the works involve cutting into a party wall to insert structural beams or padstones, raising the party wall or carrying out other notifiable alterations to the party structure.'),
             ('Do I need a Party Wall agreement for an extension in Cheadle?',
              '“Party Wall agreement” is a commonly used term, but it is not a specific document under the Party Wall etc. Act 1996. If an extension involves notifiable works, the appropriate Party Wall Notice must be served. The adjoining owner can consent in writing or, if a dispute arises, the appointed surveyor or surveyors can resolve matters through a Party Wall Award.'),
         ]),
    dict(id='offerton', name='Offerton', pc='SK2', borough='Stockport', geo=(53.4035, -2.1270), faq_only=True,
         intro="Offerton is a popular residential area east of Stockport town centre, with a range of established residential neighbourhoods. We provide Party Wall advice to building owners and adjoining owners across Offerton and the surrounding area.",
         housing="Offerton has a mix of semi-detached, detached and terraced homes, including older properties alongside more modern housing. Extensions, loft conversions and structural alterations are common types of work that can bring the Party Wall etc. Act 1996 into consideration.",
         projects=['Single-storey rear extensions', 'Loft conversions', 'Chimney breast removal', 'Internal structural alterations'],
         conservation=[],
         notes="No conservation areas have been identified within Offerton. Permitted development rights may apply depending on the property and proposed works, but this does not remove the need to comply with the Party Wall etc. Act 1996 where applicable.",
         faq=[
             ('Do I need a Party Wall Agreement for an extension in Offerton?',
              'Not every extension needs a Party Wall Agreement, but many require notice under the Party Wall etc. Act 1996. Notice may be required if you are building at or astride the boundary, carrying out work to an existing party wall or structure, or excavating close to and below the foundations of a neighbouring building.'),
             ('I have received a Party Wall Notice in Offerton. What should I do?',
              'Read the notice carefully and check the proposed works before responding. You can consent to the works or dissent. If a dispute arises, you can agree to use one Agreed Surveyor with the building owner or appoint your own Party Wall Surveyor.'),
             ('What happens if I do not respond to a Party Wall Notice?',
              'For a Party Structure Notice, if you do not consent in writing within 14 days, a dispute is deemed to have arisen under the Act. The dispute can then be resolved through the surveyor and Party Wall Award procedure.'),
             ('Do I have to pay for my own Party Wall Surveyor?',
              "Usually, the building owner carrying out the works pays the reasonable costs of the adjoining owner's surveyor where those costs arise from dealing with the proposed works under the Act. However, responsibility for costs ultimately depends on the circumstances."),
             ("What happens if my neighbour's building work damages my property?",
              'A Schedule of Condition can record the condition of your property before work begins. If damage is caused by works carried out under the Act, the Party Wall Award can set out how the damage should be made good or otherwise dealt with.'),
             ('How much notice does my neighbour have to give me?',
              "The notice period depends on the work. Party Structure Notices generally require at least two months' notice, while notices for qualifying excavation or building at the boundary generally require at least one month."),
             ('Can my neighbour start work before a Party Wall Award is agreed?',
              'Where a dispute has arisen over notifiable work, the Party Wall procedures should be completed before the notifiable works proceed. Starting notifiable work without following the Act can leave the building owner exposed to legal action, including the possibility of an injunction.'),
             ("Can I stop my neighbour's extension using the Party Wall Act?",
              'The Party Wall Act is not normally a way of stopping otherwise lawful development. It provides a process for dealing with certain works affecting party walls, boundaries and nearby excavations, while helping to protect the interests of both owners.'),
             ("My neighbour's Offerton property is rented. Who should receive the Party Wall Notice?",
              'The notice must be served on the relevant adjoining owner or owners. This can include the freeholder and someone holding a lease for more than one year, so a rented property may have more than one adjoining owner for the purposes of the Act.'),
             ('Does planning permission mean a Party Wall Notice is not required?',
              'No. Planning permission, Building Regulations and the Party Wall etc. Act 1996 are separate. Having planning permission or Building Regulations approval does not remove the need to comply with the Party Wall Act where it applies.'),
             ('Does a loft conversion in Offerton need a Party Wall Notice?',
              'It can. A loft conversion may be notifiable where the works affect a party wall or party structure, for example where structural members are inserted into or supported by the party wall. Whether notice is required depends on the proposed works and construction of the property.'),
             ('Does removing a chimney breast require a Party Wall Notice?',
              'It can. Where a chimney breast forms part of a party wall, its removal may involve work covered by section 2 of the Party Wall etc. Act 1996, meaning notice may be required before the work starts.'),
         ]),
    dict(id='hazel-grove', name='Hazel Grove', pc='SK7', borough='Stockport', geo=(53.3797, -2.1212), faq_only=True,
         intro="Hazel Grove is a popular residential area within Stockport, centred around the A6 and well connected to Stockport and Manchester. We provide Party Wall advice to building owners and adjoining owners across Hazel Grove and the surrounding area.",
         housing="Hazel Grove has a mix of semi-detached, detached and terraced homes, including older properties alongside more modern housing. Extensions, loft conversions and alterations are common types of work that can bring the Party Wall etc. Act 1996 into consideration.",
         projects=['Single-storey rear extensions', 'Loft conversions', 'Two-storey side extensions', 'Adjacent excavation'],
         conservation=[],
         notes="No conservation areas are listed within Hazel Grove. Party Wall Act requirements may still apply to works such as extensions, loft conversions and excavation close to neighbouring buildings.",
         faq=[
             ('Do I need a Party Wall agreement for an extension in Hazel Grove?',
              'Not every extension needs a Party Wall agreement. However, you may need to serve a Party Wall notice if the work involves building on or at the boundary, carrying out certain works to a party wall, or excavating close to a neighbouring building. If your neighbour consents in writing, a Party Wall Award is not normally required.'),
             ('Does a detached house in Hazel Grove ever need a Party Wall notice?',
              "Yes. A detached house can still require a Party Wall notice even if there is no shared wall. For example, section 6 may apply where excavation is within 3 metres of a neighbouring building and extends below the level of the neighbour's foundations."),
             ('Do I need a Party Wall notice for a loft conversion?',
              'It depends on the proposed work. A notice will often be required where a loft conversion involves cutting into a party wall to insert beams or other structural supports. A loft conversion does not automatically require notice, so the proposed works need to be considered.'),
             ("How close can I excavate to my neighbour's property?",
              'Section 6 may apply where excavation is within 3 metres of a neighbouring building and extends below the level of its foundations. It can also apply within 6 metres for sufficiently deep excavations, depending on the depth and position of the proposed foundations in relation to the neighbouring building.'),
             ('How much notice do I need to give my neighbour?',
              "Generally, at least one month's notice is required for building a new wall on or at the boundary and for adjacent excavation. At least two months' notice is generally required for notifiable work to an existing party structure. Notices normally cease to have effect if the work has not started within 12 months."),
             ('What happens if my neighbour does not reply to a Party Wall notice?',
              'If an adjoining owner does not respond within the relevant 14-day period, a dispute may be deemed to have arisen. The surveyor appointment procedure can then begin so that the notifiable works can be dealt with through a Party Wall Award.'),
             ("Who pays the Party Wall surveyor's fees?",
              "The building owner carrying out the work will usually pay the reasonable surveyor's fees arising from the notifiable works. This will commonly include the reasonable fees of the adjoining owner's surveyor where a separate surveyor is appointed."),
             ('I have received a Party Wall notice in Hazel Grove. What should I do?',
              'Check what work is proposed and which notice has been served. You can consent in writing or dissent. If a dispute arises, both owners can appoint one agreed surveyor, or each owner can appoint a separate surveyor.'),
             ('Do I have to pay for my own Party Wall surveyor as an adjoining owner?',
              "Usually not where the proposed works are solely for the building owner's benefit. The building owner will normally be responsible for the adjoining owner's reasonable surveyor's fees, although responsibility for costs ultimately depends on the circumstances."),
             ("What happens if my neighbour's building work damages my property?",
              'A Schedule of Condition can record the condition of your property before the notifiable works start. If damage is caused by works carried out under the Party Wall Act, the building owner may be required to make good the damage or, where appropriate, pay compensation.'),
             ("Does planning permission mean I don't need a Party Wall notice?",
              'No. Planning permission, Building Regulations approval and the Party Wall process are separate. Having planning permission does not remove the requirement to serve a Party Wall notice where the proposed works are notifiable.'),
         ]),
    dict(id='bramhall', name='Bramhall', pc='SK7', borough='Stockport', geo=(53.3630, -2.1623), faq_only=True,
         intro="Bramhall is a popular residential area within Stockport, known for its established neighbourhoods and attractive residential setting. We provide Party Wall advice to building owners and adjoining owners across Bramhall and the surrounding area.",
         housing="Bramhall has a mix of detached and semi-detached homes, with many properties set within larger plots. Rear and side extensions, garden rooms and other alterations are common types of work that can bring the Party Wall etc. Act 1996 into consideration.",
         projects=['Rear and wrap-around extensions', 'Basements and swimming pool', 'Outbuildings and garden rooms', 'Excavation close to neighbouring buildings'],
         conservation=['Bramall Park Conservation Area (designated 2005)', 'Bramhall Lane South Conservation Area (designated 2005)', 'Syddal Park Conservation Area (designated 2005)'],
         notes="All three Bramhall conservation areas are also subject to Article 4 directions, which can mean that alterations permitted elsewhere require planning permission here.",
         faq=[
             ('My Bramhall house is detached. Do I still need to follow the Party Wall Act?',
              'Yes, potentially. A detached house can still be affected by the Party Wall etc. Act 1996. For example, excavation for an extension, basement or other works may be notifiable if it is within 3 metres of a neighbouring building and goes deeper than the bottom of its foundations. The Act can therefore apply even where the properties do not share a wall.'),
             ('Do I need a party wall agreement for an extension in Bramhall?',
              'Often, yes. You may need to serve a Party Wall Notice if the extension involves building a new wall on or astride the boundary, carrying out work to an existing party structure, or excavating close to a neighbouring building. Whether the Act applies depends on the location and design of the proposed works.'),
             ("Does my neighbour's extension need a party wall notice?",
              'Possibly. If your neighbour is building on or close to the boundary, carrying out work to a shared wall, or excavating close to your property and below the level of your foundations, the works may fall within the Party Wall etc. Act 1996.'),
             ('How much notice do I need to give my neighbour?',
              "Generally, one month's notice is required for building a new wall at the boundary or for qualifying excavation works. Two months' notice is generally required for works to an existing party structure."),
             ('What happens if my neighbour does not reply to a party wall notice?',
              'If an adjoining owner does not respond within 14 days, a dispute is deemed to have arisen under the Act. Surveyors can then be appointed to deal with the notifiable works and, where required, agree a Party Wall Award.'),
             ('I have received a party wall notice in Bramhall. What should I do?',
              'Read the notice carefully and respond within the stated timeframe. You can consent to the works, or dissent and appoint a surveyor. The two owners can also agree to use one impartial surveyor, known as the agreed surveyor.'),
             ('Do I have to pay for my own party wall surveyor?',
              "Usually not. Where the works are solely for the benefit of the building owner, the building owner will normally be responsible for the reasonable costs of the adjoining owner's surveyor."),
             ('Can I start building before the Party Wall process is complete?',
              'Not where notifiable works have not been properly dealt with. If the adjoining owner consents to the notice, a Party Wall Award may not be necessary. If a dispute arises, the relevant matters will normally need to be resolved before the notifiable works proceed.'),
             ("What if my neighbour's building work damages my property?",
              'Where surveyors are appointed, a Schedule of Condition will typically be prepared before the works begin. This provides a record of the adjoining property and can help establish whether damage has resulted from the works. The Party Wall Act also provides mechanisms for making good or compensating for damage caused by notifiable works.'),
             ('Does planning permission cover party wall matters?',
              'No. Planning permission, Building Regulations and the Party Wall etc. Act 1996 are separate requirements. Obtaining planning permission does not remove the need to comply with the Party Wall Act where the proposed works are notifiable.'),
             ("Can I stop my neighbour's extension using the Party Wall Act?",
              'The Party Wall Act is not normally a means of preventing lawful development. Its purpose is to regulate certain works and provide procedures and protections for both building owners and adjoining owners.'),
         ]),
    dict(id='marple', name='Marple', pc='SK6', borough='Stockport', geo=(53.3971, -2.0634), faq_only=True,
         intro="Marple is a popular residential area within Stockport, close to the Peak District and centred around the Peak Forest and Macclesfield canals. We provide Party Wall advice to building owners and adjoining owners across Marple and the surrounding area.",
         housing="Marple has a mix of detached, semi-detached and terraced homes, including older stone-built properties alongside more modern housing. Extensions, loft conversions and alterations are common types of work that can bring the Party Wall etc. Act 1996 into consideration.",
         projects=['Rear and side extensions', 'Loft conversions', 'Stone cottage alterations', 'Excavation on sloping plots'],
         conservation=['Marple Bridge Conservation Area (designated 1974)', 'Compstall Conservation Area (designated 1974)', 'Mellor/Moorend Conservation Area (designated 1978)', 'Mill Brow Conservation Area (designated 1978)', 'Station Road/Winnington Road Conservation Area (designated 1988)', 'Peak Forest Canal Conservation Area (designated 2000)', 'Macclesfield Canal Conservation Area (designated 2000)', 'All Saints, Marple Conservation Area (designated 2005)'],
         notes="Article 4 Directions apply within parts of Marple, including several conservation areas, meaning some works that would normally benefit from permitted development rights may require planning permission.",
         faq=[
             ('Do I need a Party Wall Agreement for an extension in Marple?',
              '​You may need to follow the Party Wall etc. Act 1996 if your extension involves work to a shared wall, building on or near the boundary, or excavating close to your neighbour’s property. Whether the Act applies depends on the type and location of the proposed works.'),
             ('My neighbour is building an extension in Marple. Do I need a Party Wall Agreement?',
              'If your neighbour’s proposed works fall within the Party Wall etc. Act 1996, they should serve the appropriate Party Wall Notice before the relevant work starts. You can then either consent to the works or appoint a Party Wall Surveyor.'),
             ('What should I do if I receive a Party Wall Notice in Marple?',
              'You should review the notice and proposed works before deciding how to respond. You can consent to the works or, if you wish to have the works formally regulated, appoint a Party Wall Surveyor.'),
             ('Can I appoint my own Party Wall Surveyor in Marple?',
              'Yes. If you do not wish to consent to the notice, you can appoint your own Party Wall Surveyor. Alternatively, you and your neighbour can agree to appoint the same surveyor as the Agreed Surveyor.'),
             ('Who pays the Party Wall Surveyor’s fees?',
              'In most straightforward cases, the Building Owner carrying out the works pays the reasonable Party Wall Surveyor’s fees. However, responsibility for fees can depend on the circumstances and the nature of the works.'),
             ('What happens if my neighbour starts work without serving a Party Wall Notice?',
              'If the work falls within the Party Wall etc. Act 1996 and no notice has been served, you should seek advice as soon as possible. The appropriate next step will depend on the works being carried out and how far they have progressed.'),
             ('Do loft conversions require a Party Wall Notice in Marple?',
              'They can. Loft conversions often involve inserting steel beams or other structural elements into a party wall. Where the proposed works fall within the Party Wall etc. Act 1996, notice should be served before the relevant work begins.'),
             ('Does removing a chimney breast require a Party Wall Notice?',
              'It can. Chimney breast removal may involve cutting into or altering a party wall, particularly where structural support is required. The proposed works should be reviewed to determine whether a Party Wall Notice is necessary.'),
             ('Do new foundations or excavations near my property require a Party Wall Notice?',
              'Potentially. Excavation for an extension or other structure may fall within the Party Wall etc. Act 1996 where it is sufficiently close to a neighbouring building and extends below the level of its foundations.'),
             ('Do the canal conservation areas in Marple affect Party Wall requirements?',
              'The conservation areas around the Peak Forest and Macclesfield Canals relate mainly to planning and conservation controls rather than changing the requirements of the Party Wall etc. Act 1996. Party Wall requirements are considered separately and depend on the type of work proposed, such as work to a shared structure or excavation close to a neighbouring property.'),
             ('Does a garage conversion or demolition require a Party Wall Notice?',
              'Not necessarily. However, Party Wall procedures may apply where the works affect a shared structure, involve structural work to a party wall, or include excavation close to a neighbouring property.'),
             ('Can building work next door cause damage to my property?',
              'Building or excavation work close to an adjoining property can carry a risk of damage. A Schedule of Condition can record the condition of your property before the notifiable works start, providing a useful record if damage is later reported.'),
         ]),
]
ICO_PIN = '<path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0"/><path d="M17.657 16.657l-4.243 4.243a2 2 0 0 1 -2.827 0l-4.244 -4.243a8 8 0 1 1 11.314 0"/>'
ICO_EXT = '<path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6"/><path d="M11 13l9 -9"/><path d="M15 4h5v5"/>'
ICO_ARROW = '<path d="M5 12l14 0"/><path d="M13 18l6 -6"/><path d="M13 6l6 6"/>'
ICO_PHONE = '<path d="M5 4h4l2 5l-2.5 1.5a11 11 0 0 0 5 5l1.5 -2.5l5 2v4a2 2 0 0 1 -2 2a16 16 0 0 1 -15 -15a2 2 0 0 1 2 -2"/>'
ICO_CHART = '<path d="M3 13a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z"/><path d="M15 9a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z"/><path d="M9 5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z"/><path d="M4 20h14"/>'
SEP = '<li class="ax-breadcrumb__sep" aria-hidden="true"><svg class="ax-icon ax-icon--directional" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6l-6 6"/></svg></li>'

e = html.escape


def svg(paths, cls=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>')


def pw_questions(area_name):
    """Party Wall FAQ (homeowners + neighbours) with the area filled in."""
    out = []
    for topic in TEMPLATES['topics']:
        if topic['key'] in ('partywall', 'notice'):
            out += [(it['q'].replace('{area}', area_name), it['a'].replace('{area}', area_name)) for it in topic['items']]
    return out


def faq_html(qa):
    items = ''.join(f'''
            <details class="cr-faq__item"{' open' if i == 0 else ''}>
              <summary><h3 class="cr-faq__q">{e(q)}</h3>{CHEV}</summary>
              <p class="cr-faq__a">{e(a)}</p>
            </details>''' for i, (q, a) in enumerate(qa))
    return items


def crumbs(trail):
    """trail: [(label, href|None)]"""
    out = []
    for i, (label, href) in enumerate(trail):
        last = i == len(trail) - 1
        inner = f'<a href="{href}">{e(label)}</a>' if href and not last else f'<span>{e(label)}</span>'
        cur = ' aria-current="page"' if last else ''
        out.append(f'<li class="ax-breadcrumb__item"{cur}>{inner}</li>')
    return SEP.join(out)


def jsonld(graph):
    return ('  <script type="application/ld+json">\n'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
            + '\n  </script>')


def org_ref():
    return {'@id': '{{siteUrl}}/#org'}


def page(*, path, title, desc, og_title, h1, eyebrow, lead, trail, body, graph, geo=None, region='GB-TRF', place=''):
    geo_params = ''
    if geo:
        geo_params = (f'\n  geoRegion="{region}" geoPlace="{place}" '
                      f'geoPosition="{geo[0]};{geo[1]}" geoIcbm="{geo[0]}, {geo[1]}"')
    return f'''<!doctype html>
<!-- GENERATED by src/seo/townships.py — edit there, then run: python3 src/seo/townships.py -->
<html lang="en-GB" data-ax-route="party-wall-surveyors" data-cr-shell="topbar" data-cr-title>
<head>{{{{> head
  seoTitle="{title}"
  seoDescription="{desc}"
  ogTitle="{og_title}"
  ogImageAlt="Corelain Party Wall surveyors — {h1}"
  canonical="{path}"{geo_params}
}}}}</head>
<body>
  <div class="ax-ambient" aria-hidden="true"><i></i></div>
  <div class="ax-layout">
    <div class="ax-shell">
      {{{{> header}}}}
      <main class="ax-main" id="ax-main">
        <section class="cr-twn-hero" role="region" aria-labelledby="cr-twn-h1">
          <nav class="ax-breadcrumb cr-twn-hero__crumbs" data-cr-static aria-label="Breadcrumb">
            <ol class="ax-breadcrumb__list">{crumbs(trail)}</ol>
          </nav>
          <span class="cr-twn-hero__eyebrow">{e(eyebrow)}</span>
          <h1 class="cr-twn-hero__title" id="cr-twn-h1">{e(h1)}</h1>
          <p class="cr-twn-hero__lead">{e(lead)}</p>
          <div class="cr-twn-hero__ctas">
            <a class="cr-twn-btn cr-twn-btn--light" href="{ENQUIRY}" target="_blank" rel="noopener" data-cr-cta="area-page-hero">Request a free consultation {svg(ICO_ARROW)}</a>
            <a class="cr-twn-btn cr-twn-btn--ghost" href="tel:01618201121" data-cr-cta="area-page-call">{svg(ICO_PHONE)} 0161 820 1121</a>
          </div>
        </section>

        <div class="ax-dash-grid">
{body}
        </div>
      </main>
      {{{{> footer}}}}
    </div>
  </div>
{jsonld(graph)}
  {{{{> command}}}}
  {{{{> scripts}}}}
  <script type="module" src="/src/js/pages/party-wall.js"></script>
</body>
</html>
'''


def service_node(path, area_served):
    return {
        '@type': 'Service',
        '@id': '{{siteUrl}}' + path + '#service',
        'name': 'Party Wall surveying',
        'serviceType': 'Party Wall surveying',
        'provider': org_ref(),
        'areaServed': area_served,
        'audience': [{'@type': 'Audience', 'audienceType': t} for t in
                     ('Homeowners', 'Adjoining owners', 'Architects and design professionals', 'Builders and professional referrers')],
        'url': PW_URL,
    }


def area_page(a):
    path = f'/party-wall-surveyors/{a["id"]}'
    name, pc, borough = a['name'], a['pc'], a['borough']
    b = BOROUGHS[borough]
    council, planning = b['council'], b['planning']
    title = f'Party Wall Surveyors in {name} ({pc}) | Corelain'
    desc = (f'Party wall surveyors in {name}, {pc}: notices, schedules of condition and awards for '
            f'extensions, lofts and basements. For homeowners, neighbours and architects.')
    ca = a['conservation']
    ca_html = (''.join(f'<li>{e(c)}</li>' for c in ca) if ca else '<li class="is-none">None listed for this area</li>')
    qa = a['faq'] if a.get('faq_only') else a['faq'] + pw_questions(name)
    trail = [('Near Me', '/'), (f'Party Wall Surveyors in {borough}', HUB(borough)), (name, None)]

    body = f'''          <!-- area at a glance (4) + local housing & projects (8) -->
          <section class="ax-card ax-col--4 cr-twn-facts" role="region" aria-labelledby="cr-twn-facts-title">
            <div class="ax-card__header"><div class="ax-card__titles">
              <span class="ax-card__eyebrow">At a glance</span>
              <h2 class="ax-card__title" id="cr-twn-facts-title">{e(name)} planning facts</h2>
            </div></div>
            <div class="ax-card__body" style="padding-top:0;">
              <dl class="cr-twn-dl">
                <div><dt>Postcode district</dt><dd class="ax-num">{e(pc)}</dd></div>
                <div><dt>Borough</dt><dd>{e(borough)}</dd></div>
                <div><dt>Planning authority</dt><dd><a href="{planning}" target="_blank" rel="noopener">{e(council)}</a></dd></div>
              </dl>
              <h3 class="cr-twn-sub">Conservation areas</h3>
              <ul class="cr-twn-ca">{ca_html}</ul>
              <p class="cr-card-note">{e(a['notes'])}</p>
              <a class="cr-radon__link cr-card-foot cr-areastats" href="/?area={a['id']}">
                {svg(ICO_CHART)}
                {e(name)} area stats
                <span class="cr-radon__ext">{svg(ICO_ARROW)}</span>
              </a>
            </div>
          </section>

          <section class="ax-card ax-col--8 cr-twn-local" role="region" aria-labelledby="cr-twn-local-title">
            <div class="ax-card__header"><div class="ax-card__titles">
              <span class="ax-card__eyebrow">Local knowledge</span>
              <h2 class="ax-card__title" id="cr-twn-local-title">Homes and party walls in {e(name)}</h2>
            </div></div>
            <div class="ax-card__body" style="padding-top:0;">
              <p class="cr-twn-p">{e(a['housing'])}</p>
              <h3 class="cr-twn-sub">Projects we see most in {e(name)}</h3>
              <ul class="cr-pro__chips">{''.join(f'<li>{e(p)}</li>' for p in a['projects'])}</ul>
              <h3 class="cr-twn-sub">How a party wall instruction works</h3>
              <ol class="cr-steps">
                <li><b>Project review</b><span>Drawings and scope checked against sections 1, 2 and 6.</span></li>
                <li><b>Notice strategy</b><span>Which neighbours, which notices and when, to protect your programme.</span></li>
                <li><b>Serve notices</b><span>Correctly drafted notices served on every adjoining owner.</span></li>
                <li><b>Schedule &amp; award</b><span>The neighbour's property recorded and the award agreed.</span></li>
                <li><b>Close-out</b><span>Post-works check and sign-off.</span></li>
              </ol>
            </div>
          </section>

          {{{{> pw-projects areaHtml='{e(name)}'}}}}
          {{{{> pw-pros}}}}
          {{{{> pw-notice areaHtml='{e(name)}'}}}}

          <section class="ax-card ax-col--12" role="region" aria-labelledby="cr-twn-faq-title">
            <div class="ax-card__header"><div class="ax-card__titles">
              <span class="ax-card__eyebrow">Quick answers</span>
              <h2 class="ax-card__title" id="cr-twn-faq-title">Party Wall questions in {e(name)}</h2>
              <p class="ax-card__subtitle">Based on the Party Wall etc. Act 1996</p>
            </div></div>
            <div class="ax-card__body cr-twn-faq" style="padding-top:0;">{faq_html(qa)}
            </div>
          </section>

          {{{{> pw-areas}}}}'''

    place = {'@type': 'Place', 'name': f'{name}, {borough}',
             'address': {'@type': 'PostalAddress', 'addressLocality': name, 'postalCode': pc,
                         'addressRegion': b['address_region'], 'addressCountry': 'GB'},
             'geo': {'@type': 'GeoCoordinates', 'latitude': a['geo'][0], 'longitude': a['geo'][1]}}
    graph = [
        {'@type': 'WebPage', '@id': '{{siteUrl}}' + path + '#webpage', 'url': '{{siteUrl}}' + path,
         'name': title, 'description': desc, 'inLanguage': 'en-GB',
         'isPartOf': {'@id': '{{siteUrl}}/#website'}, 'about': {'@id': '{{siteUrl}}' + path + '#service'},
         'dateModified': '{{buildDate}}', 'publisher': org_ref()},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': label, 'item': '{{siteUrl}}' + (href or path)}
            for i, (label, href) in enumerate(trail)]},
        service_node(path, place),
        {'@type': 'FAQPage', '@id': '{{siteUrl}}' + path + '#faq',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a_}} for q, a_ in qa]},
    ]
    return path, page(path=path, title=title, desc=desc,
                      og_title=f'Party Wall Surveyors in {name} ({pc})', h1=f'Party Wall Surveyors in {name}',
                      eyebrow=f'Party Wall surveyors · {pc} · {borough}', lead=a['intro'], trail=trail, body=body,
                      graph=graph, geo=a['geo'], region=b['region'],
                      place=f'{name}, {borough}')


def areas_in(borough):
    return [a for a in AREAS if a['borough'] == borough]


def hub_page(borough='Trafford'):
    areas = areas_in(borough)
    path = HUB(borough)
    title = f'Party Wall Surveyors in {borough} | Corelain'
    desc = (f'Party wall surveyors across {borough}: ' + ', '.join(a['name'] for a in areas[:-1]) +
            f' and {areas[-1]["name"]}. Notices, schedules of condition and awards.')
    cards = ''.join(f'''
              <a class="cr-twn-card" href="/party-wall-surveyors/{a['id']}">
                <span class="cr-twn-card__head"><b>{e(a['name'])}</b><span class="ax-badge ax-badge--soft ax-badge--neutral ax-badge--sm ax-num">{e(a['pc'])}</span></span>
                <span class="cr-twn-card__text">{e(a['intro'])}</span>
                <span class="cr-twn-card__more">Party Wall in {e(a['name'])} {svg(ICO_ARROW)}</span>
              </a>''' for a in areas)
    qa = pw_questions(borough)
    trail = [('Near Me', '/'), (f'Party Wall Surveyors in {borough}', None)]
    body = f'''          <section class="ax-card ax-col--12" role="region" aria-labelledby="cr-hub-areas-title">
            <div class="ax-card__header"><div class="ax-card__titles">
              <span class="ax-card__eyebrow">{e(borough)} areas</span>
              <h2 class="ax-card__title" id="cr-hub-areas-title">Party Wall advice by area</h2>
              <p class="ax-card__subtitle">Local housing, conservation areas and the projects we see most</p>
            </div></div>
            <div class="ax-card__body" style="padding-top:0;"><div class="cr-twn-cards">{cards}
            </div></div>
          </section>

          {{{{> pw-projects areaHtml='{e(borough)}'}}}}
          {{{{> pw-pros}}}}
          {{{{> pw-notice areaHtml='{e(borough)}'}}}}

          <section class="ax-card ax-col--12" role="region" aria-labelledby="cr-twn-faq-title">
            <div class="ax-card__header"><div class="ax-card__titles">
              <span class="ax-card__eyebrow">Quick answers</span>
              <h2 class="ax-card__title" id="cr-twn-faq-title">Party Wall questions in {e(borough)}</h2>
              <p class="ax-card__subtitle">Based on the Party Wall etc. Act 1996</p>
            </div></div>
            <div class="ax-card__body cr-twn-faq" style="padding-top:0;">{faq_html(qa)}
            </div>
          </section>'''
    graph = [
        {'@type': 'WebPage', '@id': '{{siteUrl}}' + path + '#webpage', 'url': '{{siteUrl}}' + path,
         'name': title, 'description': desc, 'inLanguage': 'en-GB',
         'isPartOf': {'@id': '{{siteUrl}}/#website'}, 'about': {'@id': '{{siteUrl}}' + path + '#service'},
         'dateModified': '{{buildDate}}', 'publisher': org_ref()},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Near Me', 'item': '{{siteUrl}}/'},
            {'@type': 'ListItem', 'position': 2, 'name': f'Party Wall Surveyors in {borough}', 'item': '{{siteUrl}}' + path}]},
        service_node(path, [{'@type': 'AdministrativeArea', 'name': borough}] +
                     [{'@type': 'Place', 'name': f'{a["name"]}, {a["borough"]}'} for a in areas]),
        {'@type': 'ItemList', 'name': f'Party Wall surveyors by area in {borough}',
         'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': a['name'],
                              'url': '{{siteUrl}}/party-wall-surveyors/' + a['id']} for i, a in enumerate(areas)]},
        {'@type': 'FAQPage', '@id': '{{siteUrl}}' + path + '#faq',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a_}} for q, a_ in qa]},
    ]
    return path, page(path=path, title=title, desc=desc, og_title=f'Party Wall Surveyors in {borough}',
                      h1=f'Party Wall Surveyors in {borough}', eyebrow=f'Party Wall surveyors · {borough} borough',
                      lead=BOROUGHS[borough]['lead'], trail=trail, body=body, graph=graph)


def areas_partial():
    bs = hub_boroughs()
    boroughs_label = ' and '.join([', '.join(bs[:-1]), bs[-1]]) if len(bs) > 1 else bs[0]
    # emitted straight into .ax-card__header, which is the flex row that spaces them
    hub_links = '\n    '.join(f'<a class="ax-btn ax-btn--link" href="{HUB(b)}">All {e(b)}</a>' for b in bs)
    links = ''.join(f'''
        <li><a class="cr-areas__chip" href="/party-wall-surveyors/{a['id']}">{svg(ICO_PIN)}<span>{e(a['name'])}</span><small class="ax-num">{e(a['pc'])}</small></a></li>'''
                    for a in AREAS)
    # `col` lets a page narrow the strip so something can sit beside it
    # (Near Me pairs it with the sponsored card); it spans the full row by default.
    return f'''<!-- GENERATED by src/seo/townships.py — "Areas we cover" (MKT-01 geographic focus) -->
<section class="ax-card ax-col--{{{{#if col}}}}{{{{col}}}}{{{{else}}}}12{{{{/if}}}} cr-areas" role="region" aria-labelledby="cr-areas-title">
  <div class="ax-card__header">
    <div class="ax-card__titles">
      <span class="ax-card__eyebrow">Greater Manchester</span>
      <h2 class="ax-card__title" id="cr-areas-title" data-cr-areas-title>Party Wall surveyors across {boroughs_label}</h2>
      <p class="ax-card__subtitle">Local Party Wall guides for each focus area</p>
    </div>
    {hub_links}
  </div>
  <div class="ax-card__body" style="padding-top:0;">
    <ul class="cr-areas__list" data-cr-areas-list>{links}
    </ul>
  </div>
</section>
'''


def hub_boroughs():
    """Boroughs with at least one focus area, in the order they appear in AREAS."""
    out = []
    for a in AREAS:
        if a['borough'] not in out:
            out.append(a['borough'])
    return out


def sitemap(paths):
    urls = ['  <url>\n    <loc>%SITE_URL%/</loc>\n    <lastmod>%BUILD_DATE%</lastmod>\n    <changefreq>weekly</changefreq>\n'
            '    <priority>1.0</priority>\n    <image:image>\n      <image:loc>%SITE_URL%/images/og-old-trafford.jpg</image:loc>\n'
            '    </image:image>\n  </url>']
    for p in paths:
        prio = '0.9' if p in {HUB(b) for b in hub_boroughs()} else '0.8'
        urls.append(f'  <url>\n    <loc>%SITE_URL%{p}</loc>\n    <lastmod>%BUILD_DATE%</lastmod>\n'
                    f'    <changefreq>monthly</changefreq>\n    <priority>{prio}</priority>\n  </url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by src/seo/townships.py -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + '\n'.join(urls) + '\n</urlset>\n')


def llms_block():
    out = ['<!-- AREAS:START -->', '## Corelain Party Wall surveying', '',
           'Corelain (https://www.corelain.com/) is a Manchester building surveying practice (Cardinal House, 20 St Mary\'s Parsonage, '
           'Manchester M3 2LY; 0161 820 1121; office@corelain.com). Its Party Wall surveyors serve notices, prepare schedules of condition '
           'and agree awards under the Party Wall etc. Act 1996, for:',
           '',
           '- Homeowners planning rear or side extensions, loft conversions, basements, excavation or structural alterations.',
           '- Adjoining owners who have received a party wall notice.',
           '- Architects, architectural technologists, designers, planning consultants and structural engineers (preliminary assessments, early risk identification, CPD).',
           '- Builders, extension and loft specialists, surveyors, solicitors and project managers who refer clients.',
           '',
           f'Party Wall service page: {PW_URL}',
           '',
           '### Party Wall pages by area']
    for b in hub_boroughs():
        out += ['', f'**{b}**', '', f'- {b} (all areas): %SITE_URL%{HUB(b)}']
        for a in areas_in(b):
            ca = '; conservation areas: ' + ', '.join(a['conservation']) if a['conservation'] else ''
            out.append(f'- {a["name"]} ({a["pc"]}, {a["borough"]}): %SITE_URL%/party-wall-surveyors/{a["id"]} — {a["intro"]}{ca}')
    out += ['<!-- AREAS:END -->']
    return '\n'.join(out)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    builders = [lambda b=b: hub_page(b) for b in hub_boroughs()] + [lambda a=a: area_page(a) for a in AREAS]
    for builder in builders:
        path, html_ = builder()
        (OUT_DIR / (path.rsplit('/', 1)[1] + '.html')).write_text(html_)
        paths.append(path)
    AREAS_PARTIAL.write_text(areas_partial())
    SITEMAP.write_text(sitemap(paths))

    llms = LLMS.read_text()
    if '<!-- AREAS:START -->' in llms:
        llms = re.sub(r'<!-- AREAS:START -->.*?<!-- AREAS:END -->', lambda _: llms_block(), llms, flags=re.S)
    else:
        llms = llms.replace('<!-- FAQ:START -->', llms_block() + '\n\n<!-- FAQ:START -->', 1)
    LLMS.write_text(llms)
    print(f'Area pages written: {len(paths)} → {OUT_DIR.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
