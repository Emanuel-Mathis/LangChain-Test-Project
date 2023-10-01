import os
import re
import json
import random
import warnings

class PDFTextExtraction:
    '''
    A class containing functions to extract text from pdf and remove header/footer
    '''

    def __init__(self, doc):
        self.doc = doc

    def __extract_text(self, page):
        '''Extract text from a page and returns a list of strings'''

        text = page.get_text(sort=True)
        text = text.split('\n')
        text = [t.strip() for t in text if t.strip()]

        return text

    def __compare(self, a, b):
        '''Fuzzy matching of strings to compare headers/footers in neighboring pages'''

        count = 0
        a = re.sub('\d', '@', a)
        b = re.sub('\d', '@', b)
        for x, y in zip(a, b):
            if x == y:
                count += 1
        return count / max(len(a), len(b))

    def __remove_header(self, elements, header_candidates, WIN):
        '''Extract headers from content dictionary. Helper function for extract_header_footer() function.'''

        header_weights = [1.0, 0.75, 0.5, 0.5, 0.5]
        detected = []

        for i, candidate in enumerate(header_candidates):
            temp = header_candidates[max(i-WIN, 1) : min(i+WIN, len(header_candidates))]
            maxlen = len(max(temp, key=len))
            for sublist in temp:
                sublist[:] =  sublist + [''] * (maxlen - len(sublist))

            for j, cn in enumerate(candidate):
                score = 0
                try:
                    cmp = list(list(zip(*temp))[j])
                    for cm in cmp:
                        score += self.__compare(cn,cm) * header_weights[j]
                    score = score/len(cmp)
                except:
                    score = header_weights[j]
                if score > 0.5:
                    detected.append(cn)
            del temp

            for d in detected:
                while d in elements[i]['text'][:6]:
                    elements[i]['text'].remove(d)

        return elements

    def __remove_footer(self, elements, footer_candidates, WIN):
        '''Extract footers from content dictionary. Helper function for extract_header_footer() function.'''

        footer_weights = [0.5, 0.5, 0.5, 0.75, 1.0]
        detected = []

        for i, candidate in enumerate(footer_candidates):
            temp = footer_candidates[max(i-WIN, 1) : min(i+WIN, len(footer_candidates))]
            maxlen = len(max(temp, key=len))
            for sublist in temp:
                sublist[:] =  [''] * (maxlen - len(sublist)) + sublist

            for j, cn in enumerate(candidate):
                score = 0
                try:
                    cmp = list(list(zip(*temp))[j])
                    for cm in cmp:
                        score += self.__compare(cn,cm)
                    score = score/len(cmp)
                except:
                    score = footer_weights[j]
                if score > 0.5:
                    detected.append(cn)
            del temp

            for d in detected:
                while d in elements[i]['text'][-6:]:
                    elements[i]['text'] = elements[i]['text'][::-1]
                    elements[i]['text'].remove(d)
                    elements[i]['text'] = elements[i]['text'][::-1]

        return elements

    def __remove_header_footer(self, elements):
        '''Extract headers and footers from all pages dynamically using page-association method'''

        header_candidates = []
        footer_candidates = []

        for element in elements:
            if element['text']: 
                header_candidates.append(element['text'][:5])
                footer_candidates.append(element['text'][-5:])

        WIN = 6
        if header_candidates and footer_candidates:
            elements = self.__remove_header(elements, header_candidates, WIN)
            elements = self.__remove_footer(elements, footer_candidates, WIN)

        return elements

    def get_pdf_data(self):
        '''Driver function to run end-to-end pdf parsing pipeline'''

        pages = self.doc.pages()
        content = dict()
        elements = []

        for idx, page in enumerate(pages):
            page_data = dict()
            text = self.__extract_text(self.doc[idx])

            page_data['page'] = idx
            page_data['text'] = text
            elements.append(page_data)

        content['elements'] = self.__remove_header_footer(elements)

        return content