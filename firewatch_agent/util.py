
def unique(items):
    present = set()
    uniq_items = []
    for item in items:
        if item not in present:
            uniq_items.append(item)
            present.add(item)
    return uniq_items


assert unique('abca') == ['a', 'b', 'c']
