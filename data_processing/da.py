"""
Dialogue act (DA) representation classes. Note that DAs in Dialmonkey are composed
of intent-slot-value triples, i.e., intents are slot-specific. In a typical case,
all slots will carry the same intent, but there are cases when multiple intents are required.

The code here is adapted from TGen (https://github.com/UFAL-DSG/tgen)
"""

import re


class DAI(object):
    """Simple representation of a single dialogue act item (intent-slot-value triple)."""

    __slots__ = ['intent', 'slot', 'value', 'confidence']

    def __init__(self, intent, slot=None, value=None, confidence=1.0):
        self.intent = intent
        self.slot = slot
        self.value = value
        self.confidence = confidence

    def __str__(self):
        intn_str = str(self.intent)
        slot_str = '(' + (self.slot if self.slot is not None else '')
        quote = '\'' if (str(self.value) is not None and (' ' in str(self.value) or ':' in str(self.value))) else ''
        val_str = (('=' + quote + str(self.value) + quote) if self.value is not None else '') + ')'
        conf_str = '/%.3f' % self.confidence if self.confidence != 1.0 else ''
        return intn_str + slot_str + val_str + conf_str

    def __bytes__(self):
        return str(self).encode('ascii', errors='replace')

    def __repr__(self):
        return 'DAI.parse("' + str(self) + '")'

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return (self.intent == other.intent and
                self.slot == other.slot and
                self.value == other.value)

    def __lt__(self, other):
        return (self.intent < other.intent or
                (self.intent == other.intent and self.slot < other.slot) or
                (self.intent == other.intent and self.slot == other.slot and
                 self.value < other.value))

    def __le__(self, other):
        return (self.intent < other.intent or
                (self.intent == other.intent and self.slot < other.slot) or
                (self.intent == other.intent and self.slot == other.slot and
                 self.value <= other.value))

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    @staticmethod
    def parse(dai_text):
        m = re.search(r'/([0-9\.]+)$', dai_text)
        conf = 1.0
        if m:
            dai_text = dai_text[:m.start()]
            conf = float(m.group(1))
        intent, svp = dai_text[:-1].split('(', 1)

        if not svp:  # no slot + value (e.g. 'hello()')
            return DAI(intent, confidence=conf)

        if '=' not in svp:  # no value (e.g. 'request(to_stop)')
            return DAI(intent, svp, confidence=conf)

        slot, value = svp.split('=', 1)
        if value.endswith('"#'):  # remove special '#' characters in Bagel data (TODO treat right)
            value = value[:-1]
        if value[0] in ['"', '\'']:  # remove quotes
            value = value[1:-1]
        return DAI(intent, slot, value, conf)


class DA(object):
    """Dialogue act -- a list of DAIs with a few special functions for parsing etc.."""

    def __init__(self, dais = None):
        self.dais = [] if dais is None else list(dais)

    def __getitem__(self, idx):
        return self.dais[idx]

    def __setitem__(self, idx, value):
        self.dais[idx] = value

    def __delitem__(self, idx):
        del self.dais[idx]

    def append(self, value):
        self.dais.append(value)

    def __str__(self):
        return '&'.join([str(dai) for dai in self.dais])

    def __bytes__(self):
        return str(self).encode('ascii', errors='xmlcharrefreplace')

    def __repr__(self):
        return 'DA.parse("' + str(self) + '")'

    def __hash__(self):
        return hash(repr(self))

    def __len__(self):
        return len(self.dais)

    def __eq__(self, other):
        if not isinstance(other, DA):
            return NotImplemented
        if len(self.dais) != len(other.dais):
            return False
        for self_dai, other_dai in zip(self.dais, other.dais):
            if self_dai != other_dai:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def sort(self):
        self.dais.sort()

    def merge_duplicate_dais(self, merge_conf=max):
        """Merge DAIs with the same intent-slot-value values. The confidence
        is manipulated by the merge_conf function (defaults to `max`)."""
        self.sort()
        pos = 0
        while pos < len(self.dais) - 1:
            if self[pos] == self[pos + 1]:
                conf = merge_conf([self[pos].confidence, self[pos + 1].confidence])
                self[pos].confidence = conf
                del self[pos]
            else:
                pos += 1

    @staticmethod
    def parse(da_text):
        """Parse a DA string into DAIs (DA types, slots, and values)."""
        da = DA()
        # here we get a list of (DAI, ")/conf", DAI, ")/conf"), the  '' at end gets removed with [:-1]
        dai_texts = re.split(r'(\)(?:/[0-9\.]+)?)(?:&|$)', da_text)[:-1]
        # now we process the list two at a time, i.e. one pair of DAI + ")/conf" at a time
        for dai_open, dai_close in (dai_texts[p:p + 2] for p in range(0, len(dai_texts), 2)):
            da.append(DAI.parse(dai_open + dai_close))
        return da

    class TagQuotes(object):
        """A helper class for numbering the occurrences of quoted things in the text."""
        def __init__(self):
            self.counter = 0

        def __call__(self, match):
            self.counter += 1
            return 'XXXQUOT%d' % self.counter

    @staticmethod
    def _protect_quotes(text):
        """Find and replace quoted parts of the sentence by tags."""
        tag_pattern = '"[^"]*"|\'[^\']*\''
        tags = re.findall(tag_pattern, text)
        sent = re.sub(tag_pattern, DA.TagQuotes(), text)
        return sent, tags

    @staticmethod
    def parse_cambridge_da(da_text):
        """Parse a Cambridge-style DA string a DA object."""
        da = DA()
        da_text, quoted = DA._protect_quotes(da_text.strip())
        quoted_num = 1

        for dai_text in re.finditer(r'(\??[a-z_]+)\(([^)]*)\)', da_text):
            intent, svps_text = dai_text.groups()

            if not svps_text:  # no slots/values (e.g. 'hello()')
                da.append(DAI(intent, None, None))
                continue

            # we have some slots/values – split them into DAI
            # (either slot or value must be non-empty here)
            svps = re.findall('([^,;=\'"]*=[^"\',;]+|[^,;=\'"]+(?:=(?:[^"\',;]+))?)(?:[,;]|[\'"]$|$)', svps_text)
            for svp in svps:

                if '=' not in svp:  # no value, e.g. '?request(near)'
                    da.append(DAI(intent, svp, None))
                    continue

                # we have a value
                slot, value = svp.split('=', 1)
                if slot == '':  # ignore empty slots
                    da.append(DAI(intent))
                    continue
                if 'XXXQUOT%d' % quoted_num in value:  # get back the quoted value
                    value = re.sub('XXXQUOT%d' % quoted_num, quoted.pop(0), value, count=1)
                    quoted_num += 1
                if re.match(r'^\'.*\'$', value) or re.match('^".*"$', value):
                    value = value[1:-1]
                assert not re.match(r'^\'', value) and not re.match(r'\'$', value)
                assert not re.match(r'^"', value) and not re.match(r'"$', value)

                da.append(DAI(intent, slot, value))

        return da

    @staticmethod
    def parse_dict(da_dict, assume_intent='inform'):
        """Parse an attribute-value dict, assuming the given DA type for all resulting DAIs."""
        da = DA()
        for slot, values in da_dict.items():
            for value in values.keys():
                da.append(DAI(assume_intent, slot, value))
        da.sort()
        return da

    def value_for_slot(self, slot):
        """Return the value for the given slot (None if unset or not present at all).
        Uses the first occurrence of this slot if found."""
        for dai in self.dais:
            if dai.slot == slot:
                return dai.value
        return None

    def has_value(self, value):
        """If the DA contains the given value, return the corresponding slot; return None
        otherwise. Abstracts away from "and" and "or" values (returns True for both coordination
        members)."""
        for dai in self.dais:
            if dai.value == value:
                return dai.slot
            if (dai.value is not None and
                    value not in [None, '?'] and
                    (re.match(r'.* (and|or) ' + value + r'$', dai.value) or
                     re.match(r'^' + value + r' (and|or) ', dai.value))):
                return dai.slot
        return None

    def set_value_for_slot(self, slot, value):
        """Replace the value of the given slot. Has no effect if the slot is not present
        in the DA. Will only replace the 1st occurrence of the slot."""
        for dai in self.dais:
            if dai.slot == slot:
                dai.value = value
                break

    def get_delexicalized(self, delex_slots):
        """Return a delexicalized copy o fthe current DA (delexicalize slots that are in
        the given parameter).

        @param delex_slots: a set of names of slots to be delexicalized
        @return: a new DA() object with delexicalized values
        """
        ret = DA()
        for dai in self:
            ret_dai = DAI(dai.intent, dai.slot,
                          'X-' + dai.slot
                          if (dai.slot in delex_slots and
                              dai.value not in ['none', None, 'dont_care'])
                          else dai.value)
            ret.append(ret_dai)
        return ret

    def to_human_string(self):
        """Return a string that is supposedly more human-readable than the standard DA form."""
        out = ''
        cur_dat = None
        for dai in self:
            if dai.intent != cur_dat:
                out += ('; ' if out else '') + dai.intent.upper()
                cur_dat = dai.intent
                if dai.slot:
                    out += ': '
            elif dai.slot:
                out += ', '
            if dai.slot:
                out += dai.slot
            if dai.value:
                out += ' = ' + dai.value
        return out

    def to_cambridge_da_string(self):
        """Convert to Cambridge-style DA string (opposite of parse_cambridge_da)."""
        out = ''
        cur_dat = None
        for dai in self:
            if dai.intent != cur_dat:
                out += (')&' if out else '') + dai.intent + '('
                cur_dat = dai.intent
            elif dai.slot:
                out += ','
            if dai.slot:
                out += dai.slot
            if dai.value:
                quote = '\'' if (' ' in dai.value or ':' in dai.value) else ''
                out += '=' + quote + dai.value + quote
        out += ')' if out else ''
        return out
