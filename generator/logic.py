
def calculate_logic(info):
    for achievement in info['achievement_info']:
        sets = []
        for seq in info['sequences']:
            if 'requires' in info:
                break
            this_set = set()
            for l in seq:
                this_set.update(l)
                if achievement['name'] in l:
                    break
            if achievement['name'] in this_set:
                this_set.remove(achievement['name'])
                if not this_set:
                    # Can be the first achievement
                    achievement['requires'] = ''
                    break
                sets.append(this_set)
        if 'requires' not in achievement:
            and_set = sets[0].copy()
            for s in sets:
                and_set.intersection_update(s)
                if not and_set:
                    break
            or_sets = []
            for s in sets:
                or_set = s - and_set
                if not or_set:
                    or_sets = None
                    break
                if any(other.issubset(or_set) for other in or_sets):
                    continue
                or_sets = [existing for existing in or_sets if not or_set.issubset(existing)]
                or_sets.append(or_set)

            if and_set:
                and_str = ' AND '.join(f'|{x}|' for x in and_set)

            if or_sets:
                or_strs = []
                for or_set in or_sets:
                    or_strs.append(' AND '.join(f'|{x}|' for x in or_set))
                or_str = ' OR '.join(f'({x})' for x in or_strs)

            if and_set and or_sets:
                achievement['requires'] = f'{and_str} AND ({or_str})'
            elif and_set:
                achievement['requires'] = and_str
            else:
                achievement['requires'] = or_str

