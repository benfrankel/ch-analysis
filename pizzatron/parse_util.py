import difflib
import re
    

def after(s: str, substr: str):
    start = s.find(substr)
    if start == -1:
        return ''
    return s[start + len(substr):]


def normalize(text: str):
    text = text.lower()
    text = re.compile(r'[^\sa-z0-9]').sub('', text)
    text = re.compile(r'\s+').sub(' ', text)
    return text


def tokenize(text: str):
    raw_args = text.split()
    args = [normalize(word) for word in raw_args]
    return args, raw_args


def _is_typo_match(query, option, cutoff):
    s = difflib.SequenceMatcher()
    s.set_seqs(query, option)
    return s.ratio() >= cutoff


class Matcher:
    def __init__(
        self,
        options,

        default=None,

        allow_typo=False,
        typo_cutoff=1.0,
        typo_require_unique=False,

        allow_prefix=False,
        prefix_min_length=0,
        prefix_min_ratio=0.0,
        prefix_allow_typo=False,
        prefix_typo_cutoff=1.0,

        allow_substring=False,
        substring_min_length=0,
        substring_min_ratio=0.0,
    ):
        self.set_options(options)

        self.default = default
        
        self.allow_typo = allow_typo
        self.typo_cutoff = typo_cutoff
        self.typo_require_unique = typo_require_unique
        
        self.allow_prefix = allow_prefix
        self.prefix_min_length = prefix_min_length
        self.prefix_min_ratio = prefix_min_ratio
        self.prefix_allow_typo = prefix_allow_typo
        self.prefix_typo_cutoff = prefix_typo_cutoff
        
        self.allow_substring = allow_substring
        self.substring_min_length = substring_min_length
        self.substring_min_ratio = substring_min_ratio

    def set_options(self, options):
        self._options = options
        self._keys_by_length = list(sorted(options.keys(), key=len))

    def _is_exact(self, query, option):
        return query == option

    def _is_typo(self, query, option):
        return _is_typo_match(query, option, self.typo_cutoff)

    def _is_prefix(self, query, option):
        return option.startswith(query) or self.prefix_allow_typo and _is_typo_match(query, option[:len(query)], self.prefix_typo_cutoff)

    def _is_substring(self, query, option):
        return query in option

    def is_match(self, query, option):
        return (False
            or self._is_exact(query, option)
            or self.allow_typo and self._is_typo(query, option)
            or self.allow_prefix and len(query) >= max(self.prefix_min_length, self.prefix_min_ratio * len(option)) and self._is_prefix(query, option)
            or self.allow_substring and len(query) >= max(self.substring_min_length, self.substring_min_ratio * len(option)) and self._is_substring(query, option)
        )

    def _find_exact(self, query):
        if query in self._options:
            return query

        return None

    def _find_typo(self, query):
        matches = difflib.get_close_matches(
            query,
            self._options,
            n=2 if self.typo_require_unique else 1,
            cutoff=self.typo_cutoff,
        )
        if matches and (len(matches) == 1 or not self.typo_require_unique):
            return matches[0]

        return None

    def _find_prefix(self, query):
        if len(query) < self.prefix_min_length:
            return None

        for option in self._keys_by_length:
            if len(query) < self.prefix_min_ratio * len(option):
                break
            if self._is_prefix(query, option):
                return option

        return None

    def _find_substring(self, query):
        if len(query) < self.substring_min_length:
            return None
        
        for option in self._keys_by_length:
            if len(query) < self.substring_min_ratio * len(option):
                break
            if self._is_substring(query, option):
                return option

        return None

    def find(self, query):
        # Exact match
        match = self._find_exact(query)
        if match is not None:
            return match
    
        # Typo match
        if self.allow_typo:
            match = self._find_typo(query)
            if match is not None:
                return match
    
        # Prefix match
        if self.allow_prefix:
            match = self._find_prefix(query)
            if match is not None:
                return match
    
        # Substring match
        if self.allow_substring:
            match = self._find_substring(query)
            if match is not None:
                return match
    
        return None

    def get(self, query):
        key = self.find(query)
        if key is None:
            return None
        return self._options[key]

    def _score_exact(self, query, option):
        if query == option:
            return 1000

        return 0

    def _score_typo(self, query, option):
        s = difflib.SequenceMatcher()
        s.set_seqs(query, option)
        if s.ratio() >= self.typo_cutoff:
            return 800 + 100 * s.ratio()

        return 0

    def _score_prefix(self, query, option):
        if len(query) < min(self.prefix_min_length, self.prefix_min_ratio * len(option)):
            return 0

        if option.startswith(query):
            return 600 - (len(option) / (len(query) + 1))
        if self.prefix_allow_typo:
            s = difflib.SequenceMatcher()
            s.set_seqs(query, option[:len(query)])
            if s.ratio() >= self.prefix_typo_cutoff:
                return 500 + 50 * s.ratio()

        return 0

    def _score_substring(self, query, option):
        if len(query) < min(self.substring_min_length, self.substring_min_ratio * len(option)):
            return 0

        if query in option:
            return 400 - (len(option) / (len(query) + 1))

        return 0

    def score(self, query, option):
        return (0
            or self._score_exact(query, option)
            or (self._score_typo(query, option) if self.allow_typo else 0)
            or (self._score_prefix(query, option) if self.allow_prefix else 0)
            or (self._score_substring(query, option) if self.allow_substring else 0)
        )

    def scored_search(self, query):
        scored_options = []
        for option in self._options:
            score = self.score(query, option)
            if score > 0:
                scored_options.append((score, option))
        scored_options.sort(key=lambda x: -x[0])
        return scored_options

    def search(self, query, max_count=6, min_score=1, score_gap=1000):
        scored_options = self.scored_search(query)

        if not scored_options:
            return []

        options = []
        max_score = scored_options[0][0]
        min_score = min(min_score, max_score - score_gap)
        for score, key in scored_options:
            if score < min_score:
                break

            # Skip duplicate options from aliased keys
            option = self._options[key]
            if option in options:
                continue

            options.append(option)
            if len(options) >= max_count:
                break

        return options

    def longest_match(self, args, from_end=False):
        start = -1 if from_end else 0
        step = -1 if from_end else 1
    
        best_option = None
        matching_queries = []
        query = ''
        for arg in args[start::step]:
            if from_end:
                query = arg + query
            else:
                query += arg
    
            option = self.find(query)
            if option is not None:
                if best_option != option:
                    best_option = option
                    matching_queries = []
                matching_queries.append(query)
    
            if from_end:
                query = ' ' + query
            else:
                query += ' '
    
        if best_option is None:
            return None, None
    
        best_queries = difflib.get_close_matches(best_option, matching_queries, n=1, cutoff=0.0)
        if best_queries:
            best_query = best_queries[0]
        else:
            best_query = matching_queries[-1]
        best_index = best_query.count(' ') + 1
    
        return best_index, best_option

    def split(self, args, raw_args, from_end=False):
        if not args:
            return None, [], args, [], raw_args
    
        index, option = self.longest_match(args, from_end=from_end)
        if index is None:
            return None, [], args, [], raw_args
    
        if from_end:
            left = args[-index:]
            right = args[:-index]
            raw_left = raw_args[-index:]
            raw_right = raw_args[:-index]
        else:
            left = args[:index]
            right = args[index:]
            raw_left = raw_args[:index]
            raw_right = raw_args[index:]
    
        return option, left, right, raw_left, raw_right

    def parse(self, args, raw_args, from_end=False):
        key, _, args, _, raw_args = self.split(args, raw_args, from_end=from_end)
        option = self.default if key is None else self._options[key]
        return option, args, raw_args

    def parse_start_or_end(self, args, raw_args):
        key, _, args, _, raw_args = self.split(args, raw_args, from_end=False)
        if key is not None:
            return self._options[key], args, raw_args

        return self.parse(args, raw_args, from_end=True)
