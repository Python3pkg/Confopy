# coding: utf-8
'''
File: reports.py
Author: Oliver Zscheyge
Description:
    Implementation of all reports
'''

from confopy.analysis import Report, Analyzer, mean_stdev
from confopy.analysis.rule import eval_doc
from functools import reduce


METRIC_NAMES = ["wordlength", "spellcheck", "lexicon", "sentlength", "ari", "personalstyle", "impersonalstyle", "passiveconstructs", "simplepres", "adverbmodifier", "deadverbs", "fillers", "examplecount", "sentlengthvar"]
RULE_NAMES = ["introduction", "subsections", "floatreference", "floatreferencebefore", "floatcaption"]
MAX_METRIC_STR_LEN = reduce(max, [len(name) for name in METRIC_NAMES])
PAD = 2
METRIC_COL_WIDTH = MAX_METRIC_STR_LEN + PAD

ROUND = 2
class DocumentAverages(Report):
    """Average metric values for multiple documents.
    """
    def __init__(self):
        super(DocumentAverages, self).__init__("docsavg",
                                               "de",
                                               "Durchschnitt über mehrere Dokumente",
                                               """\
Evaluiert die Metriken für mehrere Dokumente, berechnet den Durchschnitt
    und die Standardabweichung.
    Listet in der letzten Spalte die Metrikwerte des TIGER-Corpus (deutsche
    Sprachreferenz).
    Unterstützt die Option --latex.""")

    def execute(self, docs, args):
        output = list()
        metric_names = METRIC_NAMES
        A = Analyzer.instance()
        metrics = [A.get(metric=m) for m in metric_names]
        metrics = [m for m in metrics if m != None]
        corp = A.get(corpus="TIGER")
        results = list()
        for m in metrics:
            results.append([m.evaluate(d) for d in docs])
        stats = [mean_stdev(r, ROUND) for r in results]
        if args.latex:
            output.append("\\begin{tabular}{l|l l|r}")
            output.append("    Metric & mean & stdev & TIGER \\\\")
            output.append("    \\hline")
        else:
            output.append("# Bericht \"%s\"" % self.ID)
            output.append("")
            output.append(" * MEAN:  der Mittelwert über alle Dokumente")
            output.append(" * STDEV: die dazugehörige Standardabweichung")
            output.append(" * TIGER: Metrikwert für die deutsche Sprachereferenz,")
            output.append("          den TIGER-Corpus")
            output.append("")
            output.append("%s | MEAN  | STDEV | TIGER" % "METRIC".ljust(METRIC_COL_WIDTH))
            output.append("%s-+-------+-------+------" % "".ljust(METRIC_COL_WIDTH, "-"))
        for i in range(len(metrics)):
            # Execute metrics on reference corpus
            val = metrics[i].evaluate(corp)
            val = round(val, ROUND)
            if args.latex:
                output.append("    %s & %s & %s & %s \\\\" % (metric_names[i].ljust(METRIC_COL_WIDTH), stats[i][0], stats[i][1], val))
            else:
                output.append("%s | %05.2f | %05.2f | %05.2f" % (metric_names[i].ljust(METRIC_COL_WIDTH), stats[i][0], stats[i][1], val))
        if args.latex:
            output.append("\\end{tabular}")
        return "\n".join(output)

Analyzer.register(DocumentAverages())

class DocumentComparison(Report):
    """Compares the metrics of 2 documents side by side
    """
    PAD = 2

    def __init__(self):
        super(DocumentComparison, self).__init__("doccomp",
                                                 "de",
                                                 "Vergleicht Vorher-/Nachher-Versionen",
                                                 """\
Benötigt eine gerade Anzahl n an Dokumenten (mind. 2).
    Vergleicht das erste Dokument mit dem (n / 2) + 1-sten Dokument usw.
    Bei 2 Dokumenten werden jeweils die Metriken bestimmt und gegenüber-
    gestellt.
    Bei mehr als 2 Dokumenten wird gezählt, wie häufig sich Metrikwerte
    verringert/erhöht haben oder gleich geblieben sind.
    Unterstützt die Option --latex.""")

    def _compare(self, vals):
        return "="

    def execute(self, docs, args):
        output = list()
        if len(docs) < 2 or len(docs) % 2 != 0:
            output.append("Error: Need an even number of documents (at least 2) for the document comparison report!")
        else:
            metric_names = METRIC_NAMES
            A = Analyzer.instance()
            metrics = [A.get(metric=m) for m in metric_names]
            metrics = [m for m in metrics if m != None]
            if len(docs) == 2:
                output.append("# Bericht \"%s\""% self.ID)
                output.append("")
                output.append(" * PROGRESS: Vorher- --> Nachher-Wert.")
                output.append("             (+) ... Erhöhung         ")
                output.append("             (-) ... Verringerung     ")
                output.append("             (=) ... gleichbleibend   ")
                output.append("")
                output.append("%s | PROGRESS" % "METRIC".ljust(METRIC_COL_WIDTH))
                output.append("%s-+---------------------" % "".ljust(METRIC_COL_WIDTH, "-"))
                for m in metrics:
                    vals = [m.evaluate(doc) for doc in docs]
                    progress = "="
                    if vals[0] > vals[1]:
                        progress = "-"
                    elif vals[0] < vals[1]:
                        progress = "+"
                    output.append("%s | %05.2f --> %05.2f  (%s)" % (m.ID.ljust(METRIC_COL_WIDTH), vals[0], vals[1], progress))

            else:
                half = len(docs) / 2
                if args.latex:
                    output.append("\\begin{tabular}{l|l l|l l|r}")
                    output.append("\\multirow{2}{*}{\\textbf{Metrik}} & \\multicolumn{2}{|c|}{\\textbf{Erhöhung}} & \\multicolumn{2}{|c|}{\\textbf{Verringerung}} & \\textbf{gleichbleibend} \\\\")
                    output.append("                                 & \\multicolumn{1}{|c}{$\\#$} & \\multicolumn{1}{c|}{$\\Delta$} & \\multicolumn{1}{|c}{$\\#$} & \\multicolumn{1}{c|}{$\\Delta$} & \\multicolumn{1}{c}{$\\#$} \\\\")
                    output.append("    \\hline")
                else:
                    output.append("# Bericht \"%s\"" % self.ID)
                    output.append("")
                    output.append(" * +:      Anzahl an Metrikerhöhungen")
                    output.append(" * DELTA+: Durchschnittliche Erhöhung um diesen Wert")
                    output.append(" * -:      Anzahl an Metrikverringerungen")
                    output.append(" * DELTA-: Durchschnittliche Verringerung um diesen Wert")
                    output.append(" * =:      Anzahl an Dokumentpaaren, bei denen der")
                    output.append("           Metrikwert gleich geblieben ist")
                    output.append("")
                    output.append("%s | +  | DELTA+ | -  | DELTA- | =  " % "METRIC".ljust(METRIC_COL_WIDTH))
                    output.append("%s-+----+--------+----+--------+----" % "".ljust(METRIC_COL_WIDTH, "-"))
                for m in metrics:
                    results = list()
                    for i in range(half):
                        results.append((m.evaluate(docs[i]), m.evaluate(docs[i + half])))
                    counts = [0, 0, 0] # greater, less, equal
                    avg_diffs = [0.0, 0.0]
                    for r in results:
                        if r[0] > r[1]:
                            counts[1] += 1
                            avg_diffs[1] += r[0] - r[1]
                        elif r[0] < r[1]:
                            counts[0] += 1
                            avg_diffs[0] += r[1] - r[0]
                        else:
                            counts[2] += 1
                    if counts[0] > 0:
                        avg_diffs[0] /= float(counts[0])
                        avg_diffs[0] = round(avg_diffs[0], ROUND + 1)
                    if counts[1] > 0:
                        avg_diffs[1] /= float(counts[1])
                        avg_diffs[1] = round(avg_diffs[1], ROUND + 1)
                    if args.latex:
                        output.append("    %s & %s & %s & %s & %s & %s \\\\" % (m.ID, counts[0], avg_diffs[0], counts[1], avg_diffs[1], counts[2]))
                    else:
                        output.append("%s | %02d | %06.3f | %02d | %06.3f | %02d" % (m.ID.ljust(METRIC_COL_WIDTH), counts[0], avg_diffs[0], counts[1], avg_diffs[1], counts[2]))
                if args.latex:
                    output.append("\\end{tabular}")
        return "\n".join(output)

Analyzer.register(DocumentComparison())



class MultiDocumentReport(Report):
    """Metric values for multiple documents.
    """
    def __init__(self,
                 ID="multidoc",
                 lang="de",
                 brief="Überblick über mehrere Dokumente",
                 description="""\
Berechnet die Metrikwerte für mehrere Dokumente.
    Zählt zusätzlich die Anzahl der Regelverletzungen und der
    Über-/Unterschreitungen der Metrikerwartungsbereiche.
    Unterstützt die Option --latex."""):
        super(MultiDocumentReport, self).__init__(ID, lang, brief, description)

    def compute_exceedances(self, metric_names, results):
        exceedances = list()
        for i in range(len(metric_names)):
            metric_name = metric_names[i]
            expect = _METRIC_EXPECTATIONS[metric_name]
            metric_results = results[i]
            exceedances_for_metric = list()
            for val in metric_results:
                val = round(val, 2)
                if ((expect.low is not None) and val < expect.low) or ((expect.high is not None) and val > expect.high):
                    exceedances_for_metric.append(1)
                else:
                    exceedances_for_metric.append(0)
            exceedances.append(exceedances_for_metric)
        return exceedances

    def execute(self, docs, args):
        output = []
        metric_names = METRIC_NAMES
        A = Analyzer.instance()
        metrics = [A.get(metric=m) for m in metric_names]
        metrics = [m for m in metrics if m != None]
        corp = A.get(corpus="TIGER")
        results = list()
        for m in metrics:
            results.append([m.evaluate(d) for d in docs])

        exceedances = self.compute_exceedances(metric_names, results)
        exceedances_transposed = list(map(list, list(zip(*exceedances))))

        # Metric matrix output
        doc_numbers = list(range(1, len(docs) + 1))
        if args.latex:
            tabular_format_str = [" r" for d in docs]
            tabular_format_str = "".join(tabular_format_str)
            output.append("\\begin{tabular}{l|%s}" % tabular_format_str)
            docs_header_str = list(map("& doc%02d ".__mod__, doc_numbers))
            docs_header_str = "".join(docs_header_str)
            output.append("    Metrik %s\\\\" % docs_header_str)
            output.append("    \\hline")
            for i in range(len(metrics)):
                value_str = ""
                for doc_nr in range(len(results[i])):
                    if exceedances[i][doc_nr] == 1:
                        value_str = value_str + "& \emph{%.2f} " % results[i][doc_nr]
                    else:
                        value_str = value_str + "& %.2f " % results[i][doc_nr]
                #value_str = map(u"& %.2f ".__mod__, results[i])
                #value_str = u"".join(value_str)
                output.append("    %s %s\\\\" % (metric_names[i].ljust(METRIC_COL_WIDTH), value_str))
        else:
            output.append("# Bericht \"%s\"" % self.ID)
            output.append("")
            docs_header_str = list(map("| doc%02d ".__mod__, doc_numbers))
            docs_header_str = "".join(docs_header_str)
            output.append("%s%s" % ("METRIC".ljust(METRIC_COL_WIDTH), docs_header_str))
            dash_length = len(docs_header_str) - 2
            if dash_length < 0:
                dash_length = 0
            output.append("%s+%s" % ("".ljust(METRIC_COL_WIDTH, "-"), "".ljust(dash_length, "-")))
            for i in range(len(metrics)):
                value_str = list(map("| %05.2f ".__mod__, results[i]))
                value_str = "".join(value_str)
                output.append("%s%s" % (metric_names[i].ljust(METRIC_COL_WIDTH), value_str))

        # Exceedances/shortfalls
        exceedances_counts = list(map(sum, exceedances_transposed))
        if args.latex:
            output.append("    \\hline")
            exceedances_str = list(map("& %d ".__mod__, exceedances_counts))
            exceedances_str = "".join(exceedances_str)
            output.append("    %s %s\\\\" % ("Überschreitungen".ljust(METRIC_COL_WIDTH), exceedances_str))
        else:
            output.append("%s+%s" % ("".ljust(METRIC_COL_WIDTH, "-"), "".ljust(dash_length, "-")))
            exceedances_str = list(map("|    %02d ".__mod__, exceedances_counts))
            exceedances_str = "".join(exceedances_str)
            output.append("%s%s" % ("Transgressions".ljust(METRIC_COL_WIDTH), exceedances_str))

        # Rule violations
        rule_IDs = RULE_NAMES
        rules = [A.get(rule=ID) for ID in rule_IDs if A.get(rule=ID) is not None]
        violated_rule_counts = [len(eval_doc(doc, rules)) for doc in docs]

        if args.latex:
            violated_rule_counts_str = list(map("& %d ".__mod__, violated_rule_counts))
            violated_rule_counts_str = "".join(violated_rule_counts_str)
            output.append("    %s %s\\\\" % ("Regelverletzungen".ljust(METRIC_COL_WIDTH), violated_rule_counts_str))
            output.append("\\end{tabular}")
        else:
            violated_rule_counts_str = list(map("|    %02d ".__mod__, violated_rule_counts))
            violated_rule_counts_str = "".join(violated_rule_counts_str)
            output.append("%s%s" % ("Violated rules".ljust(METRIC_COL_WIDTH), violated_rule_counts_str))

        return "\n".join(output)

Analyzer.register(MultiDocumentReport())



class _MetricExpectation(object):
    """Stores expected metric values.
    """
    def __init__(self, low=None, high=None, msg_toolow="", msg_toohigh="", msg_ok="OK!"):
        """Initializer.
        Args:
            low:         Lowest expected metric value.
            high:        Highest expected metric value.
            msg_toolow:  Message to print when metric value is lower than low.
            msg_toohigh: Message to print when metric value is higher than high.
            msg_ok:      Message to print when metric value is between low and high.
        """
        super(_MetricExpectation, self).__init__()
        self.low = low
        self.high = high
        self.msg_toolow = msg_toolow
        self.msg_toohigh = msg_toohigh
        self.msg_ok = msg_ok

_METRIC_EXPECTATIONS = {
    "adverbmodifier":    _MetricExpectation(None       , 0.03 + 0.01, "", "Versuche weniger verstärkende/unpräzise Adverbien zu verwenden!"),
    "ari":               _MetricExpectation(None       , 67.6 + 4.36, "", "Erschwerte Lesbarkeit (zu lange Wörter/Sätze!)"),
    "deadverbs":         _MetricExpectation(None       , 0.03 + 0.03, "", "Versuche weniger tote Verben wie gehören, liegen, befinden, beinhalten, geben, bewirken etc. zu verwenden!"),
    "examplecount":      _MetricExpectation(1.83 - 0.83, None       , "Versuche mehr Beispiele zu nennen!", ""),
    "fillers":           _MetricExpectation(None       , 0.02 + 0.01, "", "Zu viele Füllwörter!"),
    "impersonalstyle":   _MetricExpectation(None       , 0.02 + 0.03, "", "Zu viele Sätze mit 'man'."),
    "lexicon":           _MetricExpectation(0.51 - 0.05, 0.51 + 0.05, "Zu geringer Wortschatz", "Zu vielfältiger Wortschatz (viele Fremdwörter?)"),
    "passiveconstructs": _MetricExpectation(None       , 0.27 + 0.1 , "", "Versuche mehr aktive Sätze zu bilden!"),
    "personalstyle":     _MetricExpectation(None       , 0.03 + 0.03, "", "Zu persönlicher Schreibstil! Sätze mit 'ich', 'wir', 'sie' umschreiben!"),
    "sentlength":        _MetricExpectation(None       , 14.6 + 2.78, "", "Zu viele lange Sätze!"),
    "sentlengthvar":     _MetricExpectation(7.68 - 2.41, None       , "Versuche kurze und lange Sätze mehr abzuwechseln!"),
    "simplepres":        _MetricExpectation(0.8  - 0.06, None       , "Zu wenig Sätze sind in Präsenz geschrieben!"),
    "spellcheck":        _MetricExpectation(0.15 - 0.05, 0.15 + 0.05, "Sehr armer Wortschatz!", "Entweder zu viele Rechtschreibfehler oder zu viele Fremdwörter!"),
    "wordlength":        _MetricExpectation(None       , 6.02 + 0.26, "", "Versuche kürzere Wörter zu verwenden!"),
}

class DocumentReport(Report):
    """Overview over a single document.
    """
    def __init__(self,
                 ID="document",
                 lang="de",
                 brief="Überblick über ein einzelnes Dokument",
                 description="""\
Berechnet die Metriken für ein Dokument und überprüft die Regeln.
    Kann auch auf mehreren Dokumenten nacheinander ausgeführt werden."""):
        super(DocumentReport, self).__init__(ID, lang, brief, description)

    def execute(self, docs, args):
        if len(docs) < 1:
            return ""
        output = []
        for doc in docs:
            output.append("# Dokumentbericht")
            output.append("")
            output.append("## Metriken")
            output.append("")
            for metric_ID in sorted((list(_METRIC_EXPECTATIONS.keys()))):
                output.append(self._execute_metric(metric_ID, doc))
            output.append("")
            output.append("## Regeln")
            output.append("")
            rule_IDs = RULE_NAMES
            A = Analyzer.instance()
            rules = [A.get(rule=ID) for ID in rule_IDs if A.get(rule=ID) is not None]
            rule_messages = eval_doc(doc, rules)
            if len(rule_messages) == 0:
                output.append("Es liegen keine Regelverletzungen vor!")
            else:
                for m in rule_messages:
                    output.append(m)
        return "\n".join(output)

    def _execute_metric(self, metric_ID, node):
        A = Analyzer.instance()
        metric = A.get(metric=metric_ID)
        val = metric.evaluate(node)
        expect = _METRIC_EXPECTATIONS.get(metric_ID, None)
        output = ""
        if expect is not None:
            val_str = str(round(val, ROUND))
            if (expect.low is not None) and (expect.high is not None):
                output = " * %s %s (erwartet: zw. %.2f und %.2f)" % (metric_ID, val_str, expect.low, expect.high)
            elif expect.low is not None:
                output = " * %s %s (erwartet: min. %.2f)" % (metric_ID, val_str, expect.low)
            elif expect.high is not None:
                output = " * %s %s (erwartet: max. %.2f)" % (metric_ID, val_str, expect.high)
            if (expect.low is not None) and val < expect.low:
                output += "\n     %s" % expect.msg_toolow
            elif (expect.high is not None) and val > expect.high:
                output += "\n     %s" % expect.msg_toohigh
            else:
                output += "\n     %s" % expect.msg_ok
        return output

Analyzer.register(DocumentReport())



class SectionsReport(DocumentReport):
    """Detailed analysis of a single document.
    """
    def __init__(self):
        super(SectionsReport, self).__init__("sections",
                                             "de",
                                             "Abschnittsweise Analyse eines Dokuments",
                                             """\
Berechnet die Metriken für jedes Kapitel einzeln.""")

    def execute(self, docs, args):
        output = list()
        output.append("# Abschnittsweiser Bericht")
        output.append("")
        doc = docs[0]
        sections = doc.sections()
        for sec in sections:
            output.append("## " + sec.title)
            output.append("")
            for metric_ID in sorted(_METRIC_EXPECTATIONS.keys()):
                output.append(self._execute_metric(metric_ID, sec))
            output.append("")

        return "\n".join(output)

Analyzer.register(SectionsReport())
