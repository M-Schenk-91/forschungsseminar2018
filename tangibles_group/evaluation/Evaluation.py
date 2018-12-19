
from enum import Enum


class Experiment:
    class ExperimentType(Enum):
        NONE = -1
        REVIEW = 0

    @staticmethod
    def get_experiment_specification(_id):
        if _id == Experiment.ExperimentType.NONE.value:
            return None
        elif _id == Experiment.ExperimentType.REVIEW.value:
            return Experiment.__ReviewExperiment.specification()

    class __ReviewExperiment:

        @staticmethod
        def specification():
            d = {}

            categories = []
            contents = []

            with open('res/eval/review/files/review_contents.txt') as f:
                for i, l in enumerate(f):
                    if i == 0:
                        if l != "#CONTENTS\n":
                            raise ValueError("No suitable heading for content")
                    else:
                        tokens = l.split("__")

                        contents.append(tokens[1])
                        categories.append(tokens[2])

            with open('res/eval/review/review_settings.txt') as f:
                for i, l in enumerate(f):
                    if i == 0:
                        if l != "#REVIEW\n":
                            raise ValueError("No suitable heading for review experiment")
                    else:
                        tokens = l.split(" ")
                        d[tokens[0]] = [int(s) for s in tokens[1:]]

                        if len(d[tokens[0]]) == 1:
                            d[tokens[0]] = d[tokens[0]][0]

            if d['PAPERS'] + d['PICTURES'] != d['FILES']:
                raise ValueError("Inconsistency with the number of papers and pictures in terms of the desired overall amount of files")

            if d['DELEGATE_PAPERS'] + d['DO_AT_ONCE_PAPERS'] != d['PAPERS']:
                raise ValueError("Inconsistency with the number of delete papers and doAtOnce papers in terms of the desired overall amount of papers")

            if d['CAT_PICTURES_SEND_VIA_EMAIL'] + d['OTHER_PICTURES_DELETE'] != d['PICTURES']:
                raise ValueError("Inconsistency with the number of cat pictures and other pictures in terms of the desired overall amount of papers")

            test_sequence = []

            for i, num in enumerate(d['TEST_SEQUENCE']):
                test_sequence.append({'pid': d['PARTICIPANT'], 'id': i, 'content': contents[num - 1], 'category': categories[num - 1][:-1]})

            return test_sequence

    class Logging:

        @staticmethod
        def log(path, rows):
            s = ''

            for row in rows:
                s += (str(row) + ';')

            with open(path, 'a') as out:
                out.write(s[:-1] + '\n')
