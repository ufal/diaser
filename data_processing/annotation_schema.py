from copy import deepcopy
from data_processing.da import DAI
import json
import re
#[{
#  “dial_id”: 123,
#  “domains”: [“restaurant”, “train”],
#  “utterances”: [
#    {
#      “speaker”: “USER”,
#      “turn”: 0, # same for USER and SYSTEM in one turn
#      “utterance”: “I need to find a restaurant that serves chinese.”,
#      “nlu”: {
#        “domain”: “restaurant”,
#        “slots”: {“food”: “chinese”},
#        “intent”: “inform_restaurant”
#      } # end nlu
#      “state”: {
#        “restaurant”: {“food”: “chinese”}
#      } # end state
#      “db”: ?,
#      “inconsistency”: ?,
#    } # end turn
#   ...
#       ] # end turn_list
#} # end dialogue
#...
#] # end data

TAG_RE = re.compile('<.*?>')
NOT_SET = None
INTENTLISTFILE = "intentfile.txt" # list of possible intents for our dataset (1 intent / line)
DOMAINFILE = "domainfile.txt"# list of possible domains  for our dataset (1 intent / line)
SLOTFILE = "slotfile.txt"
ONTOFILE = "data/mwoz_ontology.json"
def get_domains_and_slots():
    ontology = json.load(open(ONTOFILE))
    return sorted(list(set([elem.split('-')[0] for elem in ontology]))), sorted(list(set([elem.split('-')[1] for elem in ontology])))

def write_domains_and_slots(domains,slots):
    with open(DOMAINFILE,'w')as d: 
         d.write('\n'.join(domains))

    with open(SLOTFILE,'w')as s: 
         s.write('\n'.join(slots))

domain,slot = get_domains_and_slots()
write_domains_and_slots(domain,slot)
def delex_utterance_fn(utterance, nlu, delex_ontology):
    delex = f' {utterance} '
    for dai in nlu:
        delex = delex.replace(f' {dai.value} ', f' [{dai.slot}] ')
    if delex_ontology is not None:
        for key, val in delex_ontology.items():
            delex = delex.replace(f' {key} ', f' [{val}] ')
    delex = delex[1:-1]
    return delex

class Dialogue:
    def __init__(self,
                 dialogue_id=NOT_SET, #-> str
                 domains=NOT_SET, # -> list
                 utterances=NOT_SET, # -> [Utterance()]
                 original_dataset=NOT_SET, # -> str
                 split=NOT_SET, # ->str
                 goal= NOT_SET, # -> dict
                 success=NOT_SET,): # -> bool
        # assert (type(dialogue_id) is str)
        # assert (type(domains) is set)
        # assert (type(utterances) is list)
        # assert (original_dataset in ["dstc",'camrest',"multiwoz","schema"] )
        # assert (split  in ['train','dev','test'] )
        # assert (type(goal) is dict)
        # assert (type(success) is bool)
        self._data = dict()
        self._data['dialogue_id'] = dialogue_id
        self._data['domains'] = domains
        self._data['utterances'] = [Utterance.load(u) for u in utterances]
        self._data['success'] = success
        self._data['original_dataset'] =  original_dataset
        self._data['goal'] = goal
        self._data["split"] = split

    
    # "goal": {
    #      constraints": [
    #          [
    #              "pricerange",
    #              "expensive"
    #          ],
    #          [
    #              "area",
    #              "south"
    #          ]
    #      ],
    #      "request-slots": [
    #          "address"
    #      ],
    #      "text": "Task 11193: You are looking for an expensive restaurant and it should be in the south part of town. Make sure you get the address of the venue."
    #  }
     
     
    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]
        return None

    def dump(self):
        data = deepcopy(self._data)
        data['utterances'] = [u.dump() for u in self._data['utterances']]
        return data

    @property
    def system_utterances(self):
        return [u for u in self._data['utterances'] if u.is_system]

    @property
    def user_utterances(self):
        return [u for u in self._data['utterances'] if u.is_user]

    @property
    def merged_turns(self):
        utterances = self._data['utterances']
        for i in range(0, len(utterances), 2):
            yield utterances[i], utterances[i+1]

    @staticmethod
    def load(dct):
        return Dialogue(dialogue_id=dct['dialogue_id'],
                        domains=dct['domains'],
                        utterances=dct['utterances'],
                        success=dct['success'],
                        goal=dct['goal'],
                        original_dataset=dct['original_dataset'])

    def extend_user_acts(self, acts):
        for tid, act in acts.items():
            self._data['utterances'][int(tid)].extend_nlu(act)

    def extend_goal(self, goal):
        if 'goal' in goal:
            goal = goal['goal']
        used_domains = {domain: goal for domain, domain_goal in goal.items() if domain != 'message' and len(domain_goal) > 0}
        if isinstance(goal['message'], list):
            goal['message'] = ' '.join(goal['message'])
        message = re.sub(TAG_RE, '', goal['message'])
        self._data['goal'] = goal

    def get_origin(self):
        return self._data['original_dataset']

class Slot(object):
    def __init__(self,
                 name = NOT_SET,
                 value = NOT_SET,
                 possible_values = []):
        assert (type(name) is str)
        assert (type(value) is str)
        self.possible_values = possible_values

        def get_available_values(self):
            return self.possible_slots

        def check_value(self,value):
            assert type(value) is str
            return value in self.possible_values

class Domain(object):
    available_domains = open(DOMAINFILE,'rt').readlines()
    def __init__(self,
                 name = NOT_SET,
                 possible_intents= NOT_SET
                 ):
        assert (name in Domain.available_domains)
        self.possible_intents = possible_intents

        def get_available_intents(self):
            return self.possible_intent

        def check_intent(self,intent):
            assert type(intent) is str
            return intent in self.possible_intents

class Intent(object):
    intent_list = open(INTENTLISTFILE,'rt').readlines() # un intent par ligne 
    def __init__(self,
                 name =NOT_SET,
                 possible_slots = []):
        assert (name in Intent.intentlist)
        self.possible_slots = possible_slots

    def get_available_slots(self):
        return self.possible_slots


    def check_slot(self,slot):
        assert type(slot) is Slot
        return slot in self.possible_slots

class Utterance:
    def __init__(self,
                 actor=NOT_SET,
                 turn=NOT_SET,
                 utterance=NOT_SET,
                 delex_utterance=NOT_SET,
                 nlu=NOT_SET,
                 intent=NOT_SET,
                 state=NOT_SET,
                 inconsistency=NOT_SET,
                 annotation_error=NOT_SET,
                 database=NOT_SET,
                 delexicalize=False,
                 delex_ontology=None
                 ):
        # print(actor)
        # assert( actor in [ 'user', 'system'] )
        # assert( (type( turn ) is int) and (turn >= 0))
        # assert( type( utterance ) is str )
        # assert( type( delex_utterance ) is str )
        # assert( (type( nlu ) is list) and (False not in [ type(x) is DAI for x in nlu ] ))
        # assert( type(intent) is str)
        # assert( type(state) is dict)
        # assert( type() is dict)


        self._data = dict()
        self._data['actor'] = actor.lower()
        self._data['turn'] = turn
        self._data['utterance'] = utterance
        self._data['intent'] = intent
        self._data['inconsistency'] = inconsistency
        self._data['annotation_error'] = annotation_error
        self._data['database'] = database
        if isinstance(nlu, list) and \
                len(nlu) > 0 and isinstance(nlu[0], str):
            self._data['nlu'] = [DAI.parse(dai) for dai in nlu]
        else:
            self._data['nlu'] = nlu
        if delexicalize:
            delex_utterance = delex_utterance_fn(utterance, self._data['nlu'], delex_ontology)
        self._data['delex_utterance'] = delex_utterance
        self._data['state'] = state



    def dump(self):
        data = deepcopy(self._data)
        data['nlu'] = [str(dai) for dai in data['nlu']]
        return data

    @property
    def is_system(self):
        return self._data['actor'] == 'system'

    @property
    def is_user(self):
        return not self.is_system

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]
        return None

    def extend_nlu(self, act):

        def _tr(key):
            key = key.replace('leaveat', 'leave at')\
                    .replace('arriveby', 'arrive by')\
                    .replace('bookstay', 'book stay')\
                    .replace('bookday', 'book day')\
                    .replace('bookpeople', 'book people')\
                    .replace('entrancefee', 'entrance fee')\
                    .replace('trainid', 'train id')
            return key

        substitutions = []
        for intent, slots in act['dialog_act'].items():
            for slot, val in slots:
                dai = DAI(intent, slot, val)
                self._data['nlu'].append(dai)

        for slot in act['span_info']:
            start = slot[3]
            end = slot[4]
            if start != end:
                key = slot[1]
                substitutions.append((start, end, _tr(key)))
        substitutions.sort(key=lambda x: x[0], reverse=True)
        delex_text = self._data['utterance']
        for s, e, k in substitutions:
            delex_text = f'{delex_text[:s]}[{k}]{delex_text[e:]}'
        self._data['delex_utterance'] = delex_text


    @staticmethod
    def load(dct):
        if isinstance(dct, Utterance):
            return dct
        return Utterance(actor=dct['actor'],
                         turn=dct['turn'],
                         utterance=dct['utterance'],
                         nlu=dct['nlu'],
                         intent=dct['intent'],
                         state=dct['state'])

class DstCamerstUtterance(Utterance):
    def __init__(self,origin=NOT_SET):
        Utterance.__init__(self)
        self.origin = origin


    # def unify_DA(self):

