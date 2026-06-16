import sys
import os

RESERVED = [
    'class','constructor','function','method',
    'field','static','var','int','char','boolean',
    'void','true','false','null','this','let','do',
    'if','else','while','return'
]

PUNCT = set('{}()[].,;+-*/&|<>=~')

class JackTokenizer:
    def __init__(self, path):
        self.path = path
        self.result = []
        raw = open(path).read()
        self.src = raw

    def _clean(self, txt):
        buf = []
        i = 0
        n = len(txt)
        while i < n:
            if txt[i:i+2] == '//':
                while i < n and txt[i] != '\n':
                    i += 1
            elif txt[i:i+2] == '/*':
                i += 2
                while i < n and txt[i-1:i+1] != '*/':
                    i += 1
                i += 1
            elif txt[i] == '"':
                end = i + 1
                while end < n and txt[end] != '"':
                    end += 1
                buf.append(txt[i:end+1])
                i = end + 1
            else:
                buf.append(txt[i])
                i += 1
        return ''.join(buf)

    def tokenize(self):
        cleaned = self._clean(self.src)
        i = 0
        n = len(cleaned)
        while i < n:
            ch = cleaned[i]
            if ch.isspace():
                i += 1
                continue
            if ch == '"':
                j = i + 1
                while j < n and cleaned[j] != '"':
                    j += 1
                self.result.append(('stringConstant', cleaned[i+1:j]))
                i = j + 1
                continue
            if ch in PUNCT:
                self.result.append(('symbol', ch))
                i += 1
                continue
            if ch.isdigit():
                j = i
                while j < n and cleaned[j].isdigit():
                    j += 1
                self.result.append(('integerConstant', cleaned[i:j]))
                i = j
                continue
            if ch.isalpha() or ch == '_':
                j = i
                while j < n and (cleaned[j].isalnum() or cleaned[j] == '_'):
                    j += 1
                word = cleaned[i:j]
                if word in RESERVED:
                    self.result.append(('keyword', word))
                else:
                    self.result.append(('identifier', word))
                i = j
                continue
            i += 1
        self._dump_xml()
        return self.result

    def _esc(self, s):
        s = s.replace('&', '&amp;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        s = s.replace('"', '&quot;')
        return s

    def _dump_xml(self):
        stem = os.path.splitext(os.path.basename(self.path))[0]
        out = stem + 'T.xml'
        with open(out, 'w') as f:
            f.write('<tokens>\n')
            for kind, val in self.result:
                f.write(f'<{kind}> {self._esc(val)} </{kind}>\n')
            f.write('</tokens>\n')
