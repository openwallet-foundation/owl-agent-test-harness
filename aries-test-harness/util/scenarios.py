import argparse
import glob
import re

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

def select_features(features, tag_options) -> List[Feature]:

    if not tag_options:
        return features

    # Add the leading '@' when not already given
    def prefix(topt):
        tlst = topt.split(',')
        for n in range(len(tlst)):
            t = tlst[n]
            if t[0] == '~' and t[1] != '@':
                t = '~@' + t[1:]
            elif t[0] != '~' and t[0] != '@':
                t = '@' + t
            tlst[n] = t
        return ','.join(tlst)

    tag_options = [prefix(t) for t in tag_options]
    print(f'Selecting: {tag_options}')

    def selected(feature_tags):
        result = True
        for tlst in [x.split(',') for x in tag_options]:
            exclude = tlst[0][0] == '~'
            if exclude and set(tlst) & set(['~'+ft for ft in feature_tags]):
                result = result and False
            if not exclude and not (set(tlst) & set(feature_tags)):
                result = result and False
        return result

    # Collect the relevant tags
    relevant_tags = []
    for topt in tag_options:
        relevant_tags.extend(topt.split(','))
    relevant_tags = [x for x in relevant_tags if x[0] != '~']
    # print(f"Relevant: {relevant_tags}")

    result = []
    for f in features:
        auxf = Feature(f.name, f.tags)
        for s in f.scenarios:
            if selected(f.tags + s.tags):
                auxf.scenarios.append(s)
        auxf.tags = list(set(relevant_tags) & set(f.tags))
        for s in auxf.scenarios:
            scenario_tags = [x for x in s.tags if re.match(r'@T\d{3}.*', x)]
            scenario_tags.extend(sorted(set(relevant_tags) & set(f.tags + s.tags)))
            s.tags = scenario_tags
        if auxf.scenarios:
            result.append(auxf)
    return result

def show_features(features, markdown):
    prefix = ""
    for f in features:
        print()
        if markdown:
            fheader = f'Feature: {f.name}'
            print(f'| Status | {fheader}')
            print(f'|:------:|:{"".ljust(len(fheader)+1, "-")}|')
        else:
            print(f"{prefix}Feature: {f.name}")
        for s in f.scenarios:
            jtags = " ".join(s.tags)
            prefix = markdown and '|        |' or ''
            if jtags:
                print(f"{prefix} {jtags} - {s.name}")
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

    parser = argparse.ArgumentParser(description="Display selected test scenarios/features filtered by associated tags",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80))

    parser.add_argument(
        "-t",
        "--tags",
        action="append",
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
        # args.tags = ['@AcceptanceTest', '@AIP10', '~@wip']        
        main(args.tags, args.markdown)
    except KeyboardInterrupt:
        exit(1)
