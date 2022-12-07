import glob

from typing import List

class Scenario:
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
    def __str__(self):
        return f'Scenario: {self.name}, {self.tags}'

class Feature:
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
        self.scenarios = []
    def __str__(self):
        return f'Feature: {self.name}, {self.tags}'

def select_features(features, tags) -> List[Feature]:
    if not tags:
        return features

    # Add the leading '@' when not already given
    tags = [(t.startswith('@') and t or '@' + t) for t in tags]
    print(f'Selecting by: {tags}')

    result = []
    for f in features:
        if set(tags) & set(f.tags):
            auxf = f
        else:
            auxf = Feature(f.name, f.tags)
            for s in f.scenarios:
                if set(tags) & set(s.tags):
                    auxf.scenarios.append(s)
        auxf.tags = list(set(tags) & set(f.tags))
        for s in auxf.scenarios:
            relevant_tags = list(filter(lambda x: x.startswith('@T'), s.tags))
            relevant_tags.extend(set(tags) & set(s.tags))
            s.tags = relevant_tags
        if auxf.scenarios:
            result.append(auxf)
    return result

def show_features(features, markdown):
    prefix = ""
    joined_tags = lambda x: " ".join(x.tags)
    for f in features:
        print()
        jtags = joined_tags(f)
        if markdown:
            fheader = f'Feature: {f.name}'
            print(f'| Status | {fheader}')
            print(f'|:------:|:{"".ljust(len(fheader)+1, "-")}|')
        else:
            if jtags:
                print(f"{prefix}{jtags}")
            print(f"{prefix}Feature: {f.name}")
        for s in f.scenarios:
            jtags = joined_tags(s)
            prefix = markdown and '|        |' or ''
            if jtags:
                print(f"{prefix} {jtags} {s.name}")
            else:
                print(f"{prefix} {s.name}")

def read_features() -> List[Feature]:
    features = []
    for path in sorted(glob.glob("./aries-test-harness/features/*.feature")):
        with open(path, 'r') as fin:
            feature = None
            last_line = None
            for line in fin.readlines():
                line = line.strip()
                if line.startswith('Feature'):
                    assert not feature, "Multiple features"
                    colidx = line.index(':')
                    name = line[colidx+1:].strip()
                    ftags = last_line.split()
                    feature = Feature(name, ftags)
                elif line.startswith('Scenario'):
                    assert feature, "No features"
                    colidx = line.index(':')
                    name = line[colidx+1:].strip()
                    stags = last_line.split()
                    scenario = Scenario(name, stags)
                    feature.scenarios.append(scenario)
                last_line = line
            if feature and feature.scenarios:
                features.append(feature)
    return features

def main(tags, markdown):
    features = read_features()
    selected = select_features(features, tags)
    show_features(selected, markdown)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Display selected test scenarios/features filtered by associated tags",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80))

    parser.add_argument(
        "-t",
        "--tags",
        required=True,
        help="Comma separated list of tags (e.g. AIP10,AIP20)",
    )
    parser.add_argument(
        "-md",
        "--markdown",
        action='store_true',
        help="Display result as markdown table",
    )
    args = parser.parse_args()

    try:
        tags = args.tags.split(',')
        main(tags, args.markdown)
    except KeyboardInterrupt:
        exit(1)
