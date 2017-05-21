# coding: utf-8
'''
File: rules.py
Author: Oliver Zscheyge
Description:
    Rules governing structural properties of scientific texts.
'''

from confopy.analysis.rule import *
from confopy.analysis import Analyzer



class IntroductionRule(Rule):
    """Chapters must have introductions.
    """
    def __init__(self, ID="introduction", language="de", brief="Kapiteleinleitungen", description="Kapitel müssen eine Einleitung haben"):
        super(IntroductionRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_chapter(node) or has_introduction(node)

    def message(self, node):
        return "Kapitel \"%s\" hat keine Einleitung!" % node.title

Analyzer.register(IntroductionRule())


class SubsectionRule(Rule):
    """Sections must have at least 2 subsections or none at all.
    """
    def __init__(self, ID="subsections", language="de", brief="Mind. 2 Unterabschnitte", description="Sektionen haben entweder 2 oder keine Untersektionen"):
        super(SubsectionRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not (is_section(node) and count_subsections(node) > 0) or (count_subsections(node) >= 2)

    def message(self, node):
        return "Abschnitt \"%s\" hat nur einen Unterabschnitt!" % node.title

Analyzer.register(SubsectionRule())


class FloatReferenceRule(Rule):
    """Floating objects must be referenced in the surrounding text.
    """
    def __init__(self,
                 ID="floatreference",
                 language="de",
                 brief="Gleitobjekte-Referenzen",
                 description="Gleitobjekte müssen in den umliegenden Paragraphen referenziert werden"):
        super(FloatReferenceRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_float(node) or is_referenced(node)

    def message(self, node):
        return "Gleitobjekt \"%s\" wird nicht im Text referenziert!" % node.text.strip()

Analyzer.register(FloatReferenceRule())


class FloatReferenceBeforeRule(Rule):
    """Floating objects must be referenced in the text before their placement.
    """
    def __init__(self,
                 ID="floatreferencebefore",
                 language="de",
                 brief="Gleitobjekte-Referenzen",
                 description="Gleitobjekte müssen im vorstehenden Text referenziert werden"):
        super(FloatReferenceBeforeRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_float(node) or was_referenced_before(node)

    def message(self, node):
        return "Gleitobjekt \"%s\" wird nicht im vorstehenden Text referenziert!" % node.text.strip()

Analyzer.register(FloatReferenceBeforeRule())


class FloatCaptionRule(Rule):
    """Floating objects must have a caption.
    """
    def __init__(self, ID="floatcaption", language="de", brief="Gleitobjekte-Beschriftung", description="Gleitobjekte müssen beschriftet sein"):
        super(FloatCaptionRule, self).__init__(ID, language, brief, description)

    def evaluate(self, node):
        return not is_float(node) or has_caption(node)

    def message(self, node):
        return "Gleitobjekt \"%s\" hat keine oder eine zu kurze Beschriftung!" % node.text.strip()

Analyzer.register(FloatCaptionRule())
