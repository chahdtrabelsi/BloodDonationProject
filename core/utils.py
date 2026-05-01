def normalize_group(g):
    return g.strip().upper()
def groupes_compatibles(groupe):
    compat = {
        'O-': ['O-', 'O+', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }
    return compat.get(normalize_group(groupe), [])
def est_compatible_campagne(donneur, campagne):
    if not campagne.groupes_cibles:
        return True

    groupes_autorises = set()

    for g in campagne.groupes_cibles.split(","):
        groupes_autorises.update(groupes_compatibles(g))

    return normalize_group(donneur.groupe_sanguin) in groupes_autorises