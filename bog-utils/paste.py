#!/usr/bin/env python3.6

import urllib.request
import urllib.error
import urllib.parse
import optparse
import os

# user editable config
#
# automatic syntax highlighting choice by file extension
# defaults are pastebin's common extensions from web interface
# add your own based on the filetypes you use
syntax_filetypes = {
    '.sh': 'bash', '.c': 'c', '.h': 'c', '.cpp': 'cpp', '.cs': 'csharp', '.css': 'css', '.html': 'html',
    '.htm': 'html', '.java': 'java', '.js': 'javascript', '.lua': 'lua', '.pl': 'perl', '.php': 'php',
    '.py': 'python', '.rb': 'rails', '.patch': 'diff'
}
#
# end of config


devkey = '6c71766cdadff9f33347e80131397ac2'  # don't edit this


def guess_syntax(ext):
    return syntax_filetypes.get(ext, 'text')


def paste(name, syntax, expire, filenames, private=False, quiet=False):
    # validate expiry/format options
    if syntax:
        syntaxes = (
            '4cs', '6502acme', '6502kickass', '6502tasm', 'abap', 'actionscript',
            'actionscript3', 'ada', 'algol68', 'apache', 'applescript', 'apt_sources', 'asm', 'asp',
            'autoconf', 'autohotkey', 'autoit', 'avisynth', 'awk', 'bascomavr', 'bash', 'basic4gl',
            'bibtex', 'blitzbasic', 'bnf', 'boo', 'bf', 'c', 'c_mac', 'cil', 'csharp', 'cpp', 'cpp-qt',
            'c_loadrunner', 'caddcl', 'cadlisp', 'cfdg', 'chaiscript', 'clojure', 'klonec', 'klonecpp',
            'cmake', 'cobol', 'coffeescript', 'cfm', 'css', 'cuesheet', 'd', 'dcs', 'delphi', 'oxygene',
            'diff', 'div', 'dos', 'dot', 'e', 'ecmascript', 'eiffel', 'email', 'epc', 'erlang', 'fsharp',
            'falcon', 'fo', 'f1', 'fortran', 'freebasic', 'gambas', 'gml', 'gdb', 'genero', 'genie',
            'gettext', 'go', 'groovy', 'gwbasic', 'haskell', 'hicest', 'hq9plus', 'html4strict', 'html5',
            'icon', 'idl', 'ini', 'inno', 'intercal', 'io', 'j', 'java', 'java5', 'javascript', 'jquery',
            'kixtart', 'latex', 'lb', 'lsl2', 'lisp', 'llvm', 'locobasic', 'logtalk', 'lolcode',
            'lotusformulas', 'lotusscript', 'lscript', 'lua', 'm68k', 'magiksf', 'make', 'mapbasic',
            'matlab', 'mirc', 'mmix', 'modula2', 'modula3', '68000devpac', 'mpasm', 'mxml', 'mysql',
            'newlisp', 'text', 'nsis', 'oberon2', 'objeck', 'objc', 'ocaml-brief', 'ocaml', 'pf', 'glsl',
            'oobas', 'oracle11', 'oracle8', 'oz', 'pascal', 'pawn', 'pcre', 'per', 'perl', 'perl6',
            'php', 'php-brief', 'pic16', 'pike', 'pixelbender', 'plsql', 'postgresql', 'povray',
            'powershell', 'powerbuilder', 'proftpd', 'progress', 'prolog', 'properties', 'providex',
            'purebasic', 'pycon', 'python', 'q', 'qbasic', 'rsplus', 'rails', 'rebol', 'reg', 'robots',
            'rpmspec', 'ruby', 'gnuplot', 'sas', 'scala', 'scheme', 'scilab', 'sdlbasic', 'smalltalk',
            'smarty', 'sql', 'systemverilog', 'tsql', 'tcl', 'teraterm', 'thinbasic', 'typoscript',
            'unicon', 'uscript', 'vala', 'vbnet', 'verilog', 'vhdl', 'vim', 'visualprolog', 'vb',
            'visualfoxpro', 'whitespace', 'whois', 'winbatch', 'xbasic', 'xml', 'xorg_conf', 'xpp',
            'yaml', 'z80', 'zxbasic'
        )

        if syntax.lower() not in syntaxes:
            if not quiet:
                print('Error: unknown syntax. Valid values are (detailed explanation: http://pastebin.com/api#5 ):')
                print(syntaxes)
            return

    if expire:
        expires = 'N', '10M', '1H', '1D', '1M'
        if expire.upper() not in expires:
            if not quiet:
                print('Error: unknown expiry time. Valid values are (see --help):')
                print(expires)
            return
    else:
        # read files from arguments
        targets = []
        for filename in filenames:
            with open(filename) as f:
                add = {'api_paste_code': f.read(), 'filename': filename}
                if (len(filenames) == 1) & (name is not None):
                    add['api_paste_name'] = name
                if syntax:
                    add['api_paste_format'] = syntax.lower()
                else:
                    add['api_paste_format'] = guess_syntax(os.path.splitext(filename)[1])
                targets.append(add.copy())

        for target in targets:
            # make actual paste requests
            filename = target.pop('filename')
            target['api_dev_key'] = devkey
            target['api_option'] = 'paste'
            if private:
                target['api_paste_private'] = '1'
            if expire:
                target['api_paste_expire_date'] = expire.upper()
            data = urllib.parse.urlencode(target).encode('ascii')
            try:
                req = urllib.request.urlopen('http://pastebin.com/api/api_post.php', data)
            except urllib.error.URLError:
                if not quiet:
                    print('Error uploading', filename + ':', 'Network error')
                return
            else:
                reply = req.read().decode()
                if 'Bad API request' in reply:
                    if not quiet:
                        print('Error uploading', filename + ':', reply)
                    return
                else:
                    if not quiet:
                        print(filename, 'uploaded to:', reply)
                    else:
                        return reply


def main():
    parser = optparse.OptionParser(usage='usage: %prog [OPTIONS] [FILE]...\nPastebin FILE(s) or standard input')
    parser.add_option('-n', '--name', dest='name', metavar='NAME',
                      help='Name/title of paste (ignored for multiple files)')
    parser.add_option('-s', '--syntax', dest='syntax', metavar='FORMAT',
                      help='Specify syntax format (common types will be guessed from filename otherwise, use -s none to stop this)')
    parser.add_option('-p', '--private', dest='private', action='store_true', default=False,
                      help='Private paste')
    parser.add_option('-e', '--expire', dest='expire', metavar='EXPIRY',
                      help='Specify expiry date: N = never, 10M = 10 minutes, 1H = 1 hour, 1D = 1 day, 1M = 1 month')
    parser.add_option('-q', '--quiet', dest='quiet', action='store_true', default=False,
                      help='Suppress information messages and print only URLs')

    options, args = parser.parse_args()

    paste(options.name,
          options.syntax,
          options.expire,
          args,
          options.private,
          options.quiet)


if __name__ == '__main__':
    main()
